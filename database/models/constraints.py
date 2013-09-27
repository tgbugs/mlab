#contains all the constraint tables and their initial values 
from database.imports   import *
from database.models.base    import Base
from database.models.mixins    import HasDataFiles, HasCiteables

###----------------------------------------------------------------
###  Helper classes/tables for mice (normalization and constraints)
###----------------------------------------------------------------

class HardwareType(Base):
    type=Column(String(30),primary_key=True)
    description=Column(Text)

    things=relationship('Hardware',primaryjoin='HardwareType.type==Hardware.type')
    #def __init__(self,type):
        #self.type=type
    def __repr__(self):
        return '\n%s\n%s%s'%(self.type, self.description, ''.join([thing.strHelper(1) for thing in self.things]))


class ExperimentType(Base):
    id=Column(String(20),primary_key=True)
    abbrev=Column(String)
    def __init__(self,id=None,abbrev=None):
        self.id=id
        self.abbrev=abbrev
    def __repr__(self):
        return super().__repr__()


class SI_PREFIX(Base): #Yes, these are a good idea because they are written once, and infact I can enforce viewonly=True OR even have non-root users see those tables as read only
    symbol=Column(Unicode(2),primary_key=True)
    prefix=Column(String(5),nullable=False)
    E=Column(Integer,nullable=False)
    #relationship('OneDData',backref='prefix') #FIXME makesure this doesn't add a column!
    def __repr__(self):
        return '%s'%(self.symbol)
    

class SI_UNIT(Base):
    symbol=Column(Unicode(3),primary_key=True)
    name=Column(String(15),nullable=False) #this is also a pk so we can accept plurals :)
    def __repr__(self):
        return '%s'%(self.symbol)


class SEX(Base):
    """Static table for sex"""
    name=Column(String(14),primary_key=True)
    symbol=Column(Unicode(1),nullable=False,unique=True) #the actual symbols
    abbrev=Column(String(1),nullable=False,unique=True) #'m','f','u'
    def __repr__(self):
        return '\n%s %s %s'%(self.name,self.abbrev,self.symbol)


class Strain(HasCiteables, Base): #TODO HasCiteable!@? need something between citeable and datafile
    id=Column(Integer,primary_key=True) #FIXME
    jax_id=Column(String(10))
    name=Column(Unicode(50)) #scrape from jax
    abbrev=Column(String(15))
    #will be VERY useful when converting for real things
    #FIXME: by reflection from jax??? probably not
    #id=Column(String(20),primary_key=True,autoincrement=False)
    #TODO can just use datafiles to get the data on them via
    #http://jaxmice.jax.org/strain/*.html
    #make a way to put the data in via a url
    def __init__(self,jax_id,name=None,abbrev=None,Citeables=[]):
        #name=getJaxData(jax_id) #TODO
        self.jax_id=jax_id
        self.name=name
        self.abbrev=abbrev
        self.citeables.extend(Citeables)
    

