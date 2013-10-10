#contains all the constraint tables and their initial values 
from database.imports   import *
from database.models.base    import Base
from database.models.mixins    import HasDataFiles, HasCiteables

###----------------------------------------------------------------
###  Helper classes/tables for mice (normalization and constraints)
###----------------------------------------------------------------

class SI_PREFIX(Base): #Yes, these are a good idea because they are written once, and infact I can enforce viewonly=True OR even have non-root users see those tables as read only
    symbol=Column(Unicode(2),primary_key=True)
    prefix=Column(String(5),nullable=False)
    E=Column(Integer,nullable=False)
    #relationship('OneDData',backref='prefix') #FIXME makesure this doesn't add a column!
    def __repr__(self):
        return '%s'%(self.symbol)
    

class SI_UNIT(Base):
    symbol=Column(Unicode(4),primary_key=True)
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
