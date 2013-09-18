from database.imports import *
from database.base import Base
from database.mixins import HasNotes

#TODO could just make this a hardware table and maybe CHECK that the type matches?
#then just have another table for any specifics on that, could do the same for the reagents, since most of them are going to have links to urls and msdses or whatever the fuck

###--------------------
###  Hardware inventory
###--------------------
class Hardware(Base):
    __tablename__='hardware'
    id=Column(Integer,primary_key=True) #FIXME should sub under type?
    type=Column(String,ForeignKey('hardwaretype.type'),nullable=False)
    name=Column(String)
    parent_id=Column(Integer,ForeignKey('hardware.id'))
    unique_id=Column(String,nullable=False) #FIXME
    sub_components=relationship('Hardware',primaryjoin='Hardware.id==Hardware.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))
    hwmetadata=relationship('HWMetaData',primaryjoin='Hardware.id==HWMetaData.hw_id') #FIXME should these just be blobs or what??? maybe by using a datatype column!??! that would mean I could just have a single metadata table per class...
    def __init__(self,Type=None,Parent=None,type=None,parent_id=None,unique_id=None):
        self.type=type
        self.parent_id=parent_id
        self.unique_id=unique_id
        if Type:
            if Type.name:
                self.type=Type.name
            else:
                raise AttributeError

        if Parent:
            if Parent.id:
                self.parent_id=Parent.id
            else:
                raise AttributeError


class Amplifier(Base): #used for enforcing data integrity for cells
    __tablename__='amplifiers'
    id=None
    type=Column(String(20))
    serial=Column(Integer,primary_key=True) #this should be sufficient for everything I need
    headstages=relationship('Headstage',primaryjoin='Amplifier.serial==Headstage.amp_serial',backref=backref('amp',uselist=False))

class Headstage(HasNotes,Base): #used for enforcing data integrity for cells
    #using the id here because it actually requires fewer columns it seems? also adding the serial every time can be a bitch... need a way to double check to make sure though
    #id=None
    #channel=Column(Integer,primary_key=True)
    amp_serial=Column(Integer,ForeignKey('amplifiers.serial'),unique=True,nullable=False)
    relationship('Cell',backref=backref('headstage',uselist=False))
    #relationship('DataFile',backref='channel') #TODO FIXME need a way to consistently link these... maybe via the metadata?


class LED(HasNotes, Base):
    #wavelength=Column(Float(53),nullable=False) #FIXME this should be unit contrained???! #FIXME THIS is hardware metadata, ideally we would like to use a constraint, but that leads to a proliferation of tables >_<
    #this is to EASE record keeping not constrain it
    test_DateTime=None
    voltage_intensity_plot=None


###-------------------
###  Reagent inventory
###-------------------

class ReagentInventory(Base): #TODO these seem almost like a constraint
    __tablename__='reagents'
    """base table for all reagents, long run could probably could interface with and inventory, but we arent anywhere near there yet"""
    id=None
    name=Column(String,primary_key=True)
    #FIXME citeables need to be like notes...
    document_id=Column(Integer,ForeignKey('citeable.id')) #recipe msds you name it
    #these are basically recipes or references to things I buy instead of make
    current_ammount=relationship('ReagentLot') #FIXME this should give a count??? ala litter?
    #TODO reorder if current amount < x


class ReagentLot(Base): #These are instances of reagents.... nope, just use a metadata table to store creation dates and shit like that?
    """actual instances of reagents that are made"""
    id=None
    reagent_id=Column(String,ForeignKey('reagents.name'),primary_key=True)
    creation_dateTime=Column(DateTime,primary_key=True) #FIXME this fucking problem again
    done_dateTime=Column(DateTime) #FIXME this fucking problem again
    #reagentmetadata=relationship('ReaMetaData',primaryjoin='ReagentLot.id==ReaMetaData.reagent_id',backref='reagent') #FIXME make this a m-m self referential association ? this won't let me keep track of the individual lots of stuff I use to make a solution or a stock though... think about that


"""
class Stock(HasNotes, Base):
    #id=None
    id=Column(Integer,primary_key=True)
    recipe_id=Column(Integer,ForeignKey('recipe.id'),nullable=False)#,primary_key=True)
    mix_dateTime=Column(DateTime,nullable=False)#,primary_key=True) #this is a mix date time so it will do for a primary key FIXME not if I make 5 stocks at once and try to enter them at the same time

class Solution(HasNotes, Base): #using an id for the one since so much to pass along
    __tablename__='solutions'
    recipe_id=Column(Integer,ForeignKey('recipe.id'),nullable=False) #sometimes it is easier to have an ID column if other tables need access
    #stock_id=Column(Integer,ForeignKey('stock.id'),unique=True)
    mix_dateTime=Column(DateTime,nullable=False) #this is a mix date time so it will do for a primary key
    #expmetadata=relationship('MetaData') #FIXME FUCK god damn it now we need a table per things tha thave md...
    #osmolarity=Column(Integer,ForeignKey('metadata.id'),unique=True) #FIXME NOW we need units :/ and HOW do we deal with THAT
"""


