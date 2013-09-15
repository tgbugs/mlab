from database.imports import *

from database.base import Base, HasNotes
#from notes import HasNotes

#TODO could just make this a hardware table and maybe CHECK that the type matches?
#then just have another table for any specifics on that, could do the same for the reagents, since most of them are going to have links to urls and msdses or whatever the fuck

###--------------------
###  Hardware inventory
###--------------------

class Amplifier(Base): #used for enforcing data integrity for cells
    __tablename__='amplifiers'
    id=None
    type=Column(String(20))
    serial=Column(Integer,primary_key=True) #this should be sufficient for everything I need
    headstages=relationship('Headstage',primaryjoin='Amplifier.serial==Headstage.amp_serial',backref=backref('amp',uselist=False))

class Headstage(HasNotes,Base): #used for enforcing data integrity for cells
    #using the id here because it actually requires fewer columns it seems? also adding the serial every time can be a bitch... need a way to double check to make sure though
    channel=Column(Integer,primary_key=True)
    amp_serial=Column(Integer,ForeignKey('amplifiers.serial'),primary_key=True)
    relationship('Cell',backref=backref('headstage',uselist=False))

class LED(HasNotes, Base):
    wavelength=None
    test_DateTime=None
    voltage_intensity_plot=None


###-------------------
###  Reagent inventory
###-------------------

class Reagent(Base): #TODO
    __tablename__='reagents'
    """base table for all reagents, long run could probably could interface with and inventory, but we arent anywhere near there yet"""


class Stock(HasNotes, Base):
    id=None
    recipe_id=Column(Integer,ForeignKey('recipe.id'),primary_key=True)
    mix_dateTime=Column(DateTime,primary_key=True) #this is a mix date time so it will do for a primary key FIXME not if I make 5 stocks at once and try to enter them at the same time

class Solution(HasNotes, Base): #using an id for the one since so much to pass along
    __tablename__='solutions'
    recipe_id=Column(Integer,ForeignKey('recipe.id'),primary_key=True) #sometimes it is easier to have an ID column if other tables need access
    mix_dateTime=Column(DateTime,unique=True) #this is a mix date time so it will do for a primary key
    #expmetadata=relationship('MetaData') #FIXME FUCK god damn it now we need a table per things tha thave md...
    #osmolarity=Column(Integer,ForeignKey('metadata.id'),unique=True) #FIXME NOW we need units :/ and HOW do we deal with THAT

    stock_id=Column(Integer,ForeignKey('stock.mix_dateTime'))


