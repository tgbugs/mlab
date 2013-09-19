from database.imports import *
from database.base import Base
from database.mixins import HasNotes, IsDataSource, HasMetaData

#TODO could just make this a hardware table and maybe CHECK that the type matches?
#then just have another table for any specifics on that, could do the same for the reagents, since most of them are going to have links to urls and msdses or whatever the fuck

###-----------------------------------
###  Hardware inventory, aka rig parts
###-----------------------------------

class Hardware(HasMetaData, IsDataSource, Base):
    __tablename__='hardware'
    id=Column(Integer,primary_key=True)     #this is going to be a hierarchical structure
    parent_id=Column(Integer,ForeignKey('hardware.id')) #sadly we can't make this nullable :( :( can still suggest sr
    type=Column(String,ForeignKey('hardwaretype.type'),nullable=False)
    name=Column(String)
    unique_id=Column(String) #FIXME fuck
    sub_components=relationship('Hardware',primaryjoin='Hardware.id==Hardware.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))
    #hwmetadata=relationship('HWMetaData',primaryjoin='Hardware.id==HWMetaData.hw_id') #FIXME should these just be blobs or what??? maybe by using a datatype column!??! that would mean I could just have a single metadata table per class...
    def __init__(self,Type=None,Parent=None,type=None,parent_id=None,name=None,unique_id=None):
        self.type=type
        self.parent_id=parent_id
        self.name=name
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

    def strHelper(self):
        return '%s '%(self.name)

    def __repr__(self):
        name=None
        uid=''
        parent=None
        children=None
        try: name=self.name
        except: pass
        try:
            if self.unique_id:
                uid=self.unique_id
        except: pass
        try: parent=self.parent.strHelper()
        except: pass
        try: children=''.join([s.strHelper() for s in self.sub_components])
        except: pass
        return '\n%s %s %s son of %s father to %s with MetaData %s'%(self.type.capitalize(),name,uid,parent,children,self.hwmetadata)

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



