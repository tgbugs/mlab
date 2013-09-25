from database.imports import *
from database.base import Base
from database.mixins import HasNotes, IsMetaDataSource, IsDataSource, HasMetaData

#TODO could just make this a hardware table and maybe CHECK that the type matches?
#then just have another table for any specifics on that, could do the same for the reagents, since most of them are going to have links to urls and msdses or whatever the fuck

###-----------------------------------
###  Hardware inventory, aka rig parts
###-----------------------------------

#FIXME this is not the right way to link subject-data
class Hardware(HasMetaData, IsMetaDataSource, Base):
    __tablename__='hardware'
    id=Column(Integer,primary_key=True)     #this is going to be a hierarchical structure
    parent_id=Column(Integer,ForeignKey('hardware.id')) #sadly we can't make this nullable :( :( can still suggest sr
    #TODO I MUST have a way to track changes in the parent state so that datafiles will have the state when THEY were recorded...
    type=Column(String,ForeignKey('hardwaretype.type'),nullable=False)
    name=Column(String)
    unique_id=Column(String) #FIXME fuck
    model=Column(String)
    company=Column(String) #TODO oh look hooks into contacts
    #TODO figure out what if this is NOT going in the database and can thus go in metadata instead
    blueprint_id=Column(Integer,ForeignKey('citeable.id')) #TODO
    manual_id=Column(Integer,ForeignKey('citeable.id')) #TODO
    sub_components=relationship('Hardware',primaryjoin='Hardware.id==Hardware.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))

    def __init__(self,Type=None,Parent=None,type=None,Blueprint=None,parent_id=None,name=None,unique_id=None,blueprint_id=None,model=None,company=None,manual_id=None):
        self.type=type
        self.parent_id=parent_id
        self.name=name
        self.unique_id=unique_id
        self.blueprint_id=blueprint_id
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
        if Blueprint:
            if Blueprint.id:
                self.blueprint_id=Blueprint.id
            else:
                raise AttributeError('BP no id!')

    def strHelper(self,depth=0):
        ts='\t'*depth
        return '\n%s%s'%(ts,self.name)

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
        try: children=''.join([s.strHelper(1) for s in self.sub_components])
        except: pass
        return '\n%s %s %s son of %s father to %s\n\twith MetaData %s'%(self.type.capitalize(),name,uid,parent,children,''.join([m.strHelper(1) for m in self.metadata_]))

class RigHistory(Base): #this is nice, but it seems better to get the current rig state and pull the relevant data and put it in cell metadata
    id=Column(Integer,primary_key=True)
    dateTime=Column(DateTime,nullable=False) #FIXME should be timestamp
    user_id=None
    action=None
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False)
    old_parent=Column(Integer,ForeignKey('hardware.id'),nullable=False)
    new_parent=Column(Integer,ForeignKey('hardware.id'),nullable=False)
    @hybrid_property
    def delta(self):
        return self.old_parent-self.new_parent #this works better since the 'current' parents and all history will cancel eachother out and we will be left with the parent of that node on that date, +sum(delta) is the use

    #TODO proper way to query this seems to be??? to sum the deltas I think... when reconstructing the rig config for output I will need to use this table



###-------------------
###  Reagent inventory
###-------------------

class ReagentInventory(Base): #TODO HasCitables
    __tablename__='reagenttypes'
    """base table for all reagents, long run could probably could interface with and inventory, but we arent anywhere near there yet"""
    name=Column(String,primary_key=True)
    #FIXME citeables need to be like notes...
    document_id=Column(Integer,ForeignKey('citeable.id')) #recipe msds you name it
    #these are basically recipes or references to things I buy instead of make
    current_stock=relationship('Reagent') #FIXME this should give a count??? ala litter?
    #TODO reorder if current amount < x
    def __repr__(self):
        return super().__repr__('name')


class Reagent(Base): #TODO HasReagents??!
    """actual instances of reagents that are made"""
    __tablename__='reagents'
    id=Column(Integer,primary_key=True)
    reagent_id=Column(String,ForeignKey('reagenttypes.name'),nullable=False)
    creation_dateTime=Column(DateTime,default=datetime.now)
    done_dateTime=Column(DateTime)
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



