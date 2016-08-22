from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base,SportMenu

engine = create_engine('sqlite:///sports.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


baseball = Catalog(name="Baseball")
basketball = Catalog(name="Basketball")
soccer = Catalog(name="Soccer")
golf = Catalog(name="Golf")

session.add(baseball)
session.add(basketball)
session.add(soccer)
session.add(golf)
session.commit()


t = Catalog(name="Tennis")
session.add(t)
session.commit()
menuItem1 = SportMenu(name="tennis ball", description="flourescent colored ball used to play",catalog=t)
session.add(menuItem1)
session.commit()

menuItem2 = SportMenu(name="Racket", description="the device with strings used to hit the ball",catalog=t)
session.add(menuItem2)
session.commit()

menuItem3 = SportMenu(name="net", description="3 inch barrier that separates the two sides of the court",catalog=t)
session.add(menuItem3)
session.commit()


b = Catalog(name="Badminton")
session.add(b)
session.commit()
menuItem1 = SportMenu(name="birdie", description="small conical shaped object made of feather",catalog=b)
session.add(menuItem1)
session.commit()

menuItem2 = SportMenu(name="Racket", description="the device with strings used to hit the birdie",catalog=b)
session.add(menuItem2)
session.commit()

menuItem3 = SportMenu(name="net", description="5 inch barrier that separates the two sides of the court",catalog=b)
session.add(menuItem3)
session.commit()


c = Catalog(name="Cricket")
session.add(c)
session.commit()
menuItem1 = SportMenu(name="Bat", description="flat-surfaced wooden piece with a long handle. It has a curved surface on the back. Held by a bastman in the hand",catalog=c)
session.add(menuItem1)
session.commit()

menuItem2 = SportMenu(name="Stumps", description="the three wooden sticks on each end of the cricket pitch. Batsmen goal is to prevent the ball from hitting the stumps",catalog=c)
session.add(menuItem2)
session.commit()

menuItem3 = SportMenu(name="Fielder", description="one of 11 players on the field belonging to the bowling team",catalog=c)
session.add(menuItem3)
session.commit()


catalog = session.query(Catalog).all()
for e in catalog:
    print e.name

session.commit()
