from database.imports import *
from sqlalchemy                         import Date
from sqlalchemy                         import ForeignKeyConstraint

from database.base import Base, HasNotes
#from notes import HasNotes

###---------------
###  People tables
###---------------

class User(Base):
    __tablename__='users'
    #because why the fuck not...
    pass

class Person(HasNotes, Base):
    __tablename__='people'
    PrefixName=Column(String) #BECAUSE FUCK YOU
    FirstName=Column(String)
    MiddleName=Column(String)
    LastName=Column(String)
    #Gender=Column(String,ForeignKey('sex.id')) #LOL
    Gender=Column(String)
    ForeignKeyConstraint('Person.Gender',['sex.name','sex.symbol','sex.abbrev'])
    Birthdate=Column(Date) #this is here to match the odML, I actually think it is stupid to have, but whatever
    #Role=Column(String,ForeignKey('role.id'))
    Role=Column(String)
    neurotree_id=Column(Integer) #for shits and gigs
    experiments=relationship('Experiment',backref='investigator') #SOMETHING SOMETHING ACCESS CONTROL also in theory this might be m-m in some wierd situation where >1 person involved
    projects=None #FIXME m-m


