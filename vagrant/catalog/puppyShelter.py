import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///puppies.db')
Base = declarative_base()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class Shelter(Base):
	__tablename__ = 'shelter'

	name = Column(String(250),nullable=False)
	address = Column(String(250))
	city = Column(String(30))
	state = Column(String(30))
	zipCode = Column(Integer)
	website = Column(String(250))
	id = Column(Integer,primary_key=True)


class Puppy(Base):
	__tablename__ = 'puppy'

	name = Column(String(250),nullable=False)
	pup_id = Column(Integer,primary_key=True)
	dob = Column(String(250))
	gender = Column(String(30))
	weight = Column(Integer)
	shelter_id = Column(Integer,ForeignKey('shelter.id'))
	shelter = relationship("Shelter")


Base.metadata.create_all(engine)


dog_shelter = Shelter(name="DogShelter_1",address="25 Cross Street",city="Chennai",
	state="TN",zipCode ="76555",website="www.doggy.de")


dog_shelter2 = Shelter(name="DogShelter_2",address="26 Cross Street",city="Chennai",
	state="TN",zipCode ="72555",website="www.doggy1.de")


dog_shelter3 = Shelter(name="DogShelter_3",address="29 Cross Street",city="Chennai",
	state="TN",zipCode ="76155",website="www.doggy2.de")


pup= Puppy(name="Julie",dob="12-3-3",gender="female",weight=120,shelter=dog_shelter)
pup1= Puppy(name="Harry",dob="12-3-3",gender="female",weight=120,shelter=dog_shelter2)
pup2= Puppy(name="Sally",dob="12-1-3",gender="female",weight=111,shelter=dog_shelter3)

#session.delete(dog_shelter)
session.add(dog_shelter)
"""session.add(dog_shelter2)
session.add(dog_shelter3)

session.add(pup)
session.add(pup1)
session.add(pup2)
"""
session.commit()

ds = session.query(Shelter).filter_by(name="DogShelter_1").first()
ds.name = "DogShelter_4"
session.add(ds)
session.commit()

ds = session.query(Shelter).filter_by(name="DogShelter_4").first()
print ds.name
ds.name = "Ram"
session.add(ds)
session.commit()

wquery = session.query(Shelter).filter_by(name="Ram").all()
for e in wquery:
	print e.name

print "before delete"

wquery = session.query(Shelter).filter_by(name="Ram").all()
for e in wquery:
	firstRec = e
session.delete(firstRec)
session.commit()

print "after delete"
wquery = session.query(Shelter).filter_by(name="Ram").all()
for e in wquery:
	print e.name
