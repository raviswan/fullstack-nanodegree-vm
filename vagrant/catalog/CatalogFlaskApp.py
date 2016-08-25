from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask import session as login_session
import random,string
from sqlalchemy import create_engine,desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, SportMenu, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sport Catalog"

engine = create_engine('sqlite:///sports.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    print "gconnect is here"
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    print "gconnect1 is here"
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print "gconnect2 is here"
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print "gconnect3 is here"
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if the user exists , if not make a new one 
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token'] 
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/catalog/<int:catalog_id>/menu/JSON')
def catalogMenuJSON(catalog_id):
    #catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(SportMenu).filter_by(catalog_id=catalog_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/catalog/<int:catalog_id>/menu/<int:item_id>/JSON')
def menuItemJSON(catalog_id, item_id):
    item = session.query(SportMenu).filter_by(id=item_id).one()
    return jsonify(Menu_Item=item.serialize)


@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Catalog).all()
    return jsonify(sports=[r.serialize for r in catalog])


# Show all catalog items
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    catalog = session.query(Catalog).all()
    latest = (session.query(SportMenu).order_by(desc(SportMenu.time_stamp)).\
                join(Catalog.sport_menu).limit(10).values(SportMenu.name,\
                    Catalog.name))
    latest_items = []
    for i,s in latest:
        latest_items.append({i,s})
    return render_template('catalog.html', catalog=catalog,latest_items=latest_items)

# Show catalog description
@app.route('/catalog/<string:sport_name>/')
@app.route('/catalog/<string:sport_name>/items/')
def showMenu(sport_name):
    currSport = session.query(Catalog).filter_by(name=sport_name).one()
    fullCatalog = session.query(Catalog).all()
    items = session.query(SportMenu).filter_by(catalog_id=currSport.id).all()
    itemCount =  session.query(SportMenu).filter_by(catalog_id=currSport.id).count()
    return render_template('sportMenu.html', items=items, itemCount = itemCount, currSport=currSport,
        fullCatalog=fullCatalog)
    # return 'This page is the menu for restaurant %s' % restaurant_id
    # 

# Show catalog description
@app.route('/catalog/<string:sport_name>/<string:item_name>/')
def showDescription(sport_name,item_name):
    currSport = session.query(Catalog).filter_by(name=sport_name).one()
    itemToDescribe = session.query(SportMenu).filter_by(name=item_name, catalog_id=currSport.id).one()
    return render_template('description.html', item=itemToDescribe,sport_name=sport_name)

# Create a new catalog item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newSport():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newSport = Catalog(name=request.form['name'],user_id=login_session['user_id'])
        session.add(newSport)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newSport.html')




@app.route('/catalog/<int:sport_id>/edit/', methods=['GET', 'POST'])
def editSport(sport_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedSport = session.query(
        Catalog).filter_by(id=sport_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedSport.name = request.form['name']
            return redirect(url_for('showCatalog'))
    else:
        return render_template(
            'editSport.html', catalog=editedSport)

    # return 'This page will be for editing restaurant %s' % restaurant_id

# Delete a restaurant


@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteSport(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(
            url_for('showRestaurants', catalog_id=catalog_id))
    else:
        return render_template(
            'deleteRestaurant.html', catalog=itemToDelete)
    # return 'This page will be for deleting restaurant %s' % restaurant_id



@app.route(
    '/catalog/<int:catalog_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(catalog_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = SportMenu(name=request.form['name'], description=request.form[
                           'description'], catalog_id=catalog_id,user_id = login_session['user_id'] )
        session.add(newItem)
        session.commit()

        return redirect(url_for('showMenu', catalog_id=catalog_id))
    else:
        return render_template('newmenuitem.html', catalog_id=catalog_id)


@app.route('/catalog/<string:sport_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def editMenuItem(sport_name,item_name):
    if 'username' not in login_session:
        return redirect('/login')
    sportForEditedItem = session.query(Catalog).filter_by(name=sport_name).one()
    editedItem = session.query(SportMenu).filter_by(name=item_name,catalog_id=sportForEditedItem.id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showMenu', sport_name=sport_name))
    else:
        return render_template('editmenuitem.html', sport = sportForEditedItem,item=editedItem)
    # return 'This page is for editing menu item %s' % menu_id

# Delete a menu item


@app.route('/catalog/<string:sport_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(SportMenu).filter_by(name=item_name).one()
    sportForDeletedItem = session.query(Catalog).filter_by(id=itemToDelete.catalog_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showMenu', sport_name=sportForDeletedItem.name))
    else:
        return render_template('deletemenuitem.html', item=itemToDelete)
    # return "This page is for deleting menu item %s" % menu_id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
