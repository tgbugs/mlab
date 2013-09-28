from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, IsMetaDataSource, IsDataSource, HasMetaData, HasCiteables

#TODO could just make this a hardware table and maybe CHECK that the type matches?
#then just have another table for any specifics on that, could do the same for the reagents, since most of them are going to have links to urls and msdses or whatever the fuck

###-----------------------------------
###  Hardware inventory, aka rig parts
###-----------------------------------

#FIXME this is not the right way to link subject-data

class HardwareType(Base):
    type=Column(String(30),primary_key=True)
    description=Column(Text)

    things=relationship('Hardware',primaryjoin='HardwareType.type==Hardware.type')
    #def __init__(self,type):
        #self.type=type
    def __repr__(self):
        return '\n%s\n%s%s'%(self.type, self.description, ''.join([thing.strHelper(1) for thing in self.things]))


class Hardware(HasMetaData, HasCiteables, IsMetaDataSource, Base): #FIXME figure out what to do about calibration data :/ should that be its own experiment? probably not, there is no subject... I really think it goes under datasources??!? maybe? the fucking datafile would need to have multiple datasources to allow for calibration o f the LED stim  or something since the LED itself is not a datasource the photodiode might be
    #NOTE: verdict, pipettes shall be hardware, but their values will be in Cell metadata
    __tablename__='hardware'
    id=Column(Integer,primary_key=True)     #this is going to be a hierarchical structure
    parent_id=Column(Integer,ForeignKey('hardware.id')) #sadly we can't make this nullable :( :( can still suggest sr
    #TODO I MUST have a way to track changes in the parent state so that datafiles will have the state when THEY were recorded...
    type=Column(String,ForeignKey('hardwaretype.type'),nullable=False)
    name=Column(String)
    unique_id=Column(String) #FIXME fuck, serial numbers
    model=Column(String) # item numbers for repeated use stuff (sorta like a reagent... :/)
    manufacturer=Column(String) #TODO oh look hooks into contacts
    #TODO figure out what if this is NOT going in the database and can thus go in metadata instead
    blueprint_id=Column(Integer,ForeignKey('citeable.id')) #TODO
    manual_id=Column(Integer,ForeignKey('citeable.id')) #TODO
    sub_components=relationship('Hardware',primaryjoin='Hardware.id==Hardware.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))

    def __init__(self,Type=None,Parent=None,type=None,Blueprint=None,parent_id=None,name=None,unique_id=None,blueprint_id=None,model=None,manufacturer=None,manual_id=None):
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

class ReagentType(HasCiteables, Base):
    __tablename__='reagenttypes'
    """base table for all reagents, long run could probably could interface with and inventory, but we arent anywhere near there yet"""
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(String,unique=True)
    iupac=Column(String,unique=True)
    abbrev=Column(String,unique=True)
    molarMass=None #FIXME should this be metadata?
    #TODO: usage rate
    def __repr__(self):
        return super().__repr__('name')


class Reagent(Base): #TODO HasReagents??!
    """actual instances of reagents that are made"""
    __tablename__='reagents'
    type_id=Column(Integer,ForeignKey('reagenttypes.id'),primary_key=True)
    lotNumber=Column(Integer,primary_key=True) #XXX this is a sqlite specific problem >_<
    creationDateTime=Column(DateTime,default=datetime.now)
    doneDateTime=Column(DateTime)
    type=relationship('ReagentType',backref='lots',uselist=False) #FIXME
    #TODO reorder/remake if current amount < x
    #reagentmetadata=relationship('ReaMetaData',primaryjoin='ReagentLot.id==ReaMetaData.reagent_id',backref='reagent') #FIXME make this a m-m self referential association ? this won't let me keep track of the individual lots of stuff I use to make a solution or a stock though... think about that
    def __init__(self,Type=None,lotNumber=None,creationDateTime=None,doneDateTime=None,type_id=None):
        self.type_id=type_id
        #self.lotNumber=lotNumber
        self.creationDateTime=creationDateTime
        self.doneDateTime=doneDateTime
        if Type:
            if Type.id:
                self.type_id=Type.id
            else:
                raise AttributeError

###----------------------------------------------
###  Ingredient association table to make recipes
###----------------------------------------------

class Ingredient(Base): #this is actually an association table
    #TODO figure out how to query this properly... probably via recipe in ReagentType...
    __tablename__='ingredients'
    reagent_id=Column(Integer,ForeignKey('reagenttypes.id'),primary_key=True)
    product_id=Column(Integer,ForeignKey('reagenttypes.id'),primary_key=True)
    finalValue=Column(Float(53)) #TODO enforce use of molarity or %weight...
    finalPrefix=Column(Unicode(2),ForeignKey('si_prefix.symbol'),nullable=False)
    finalUnits=Column(Unicode(3),ForeignKey('si_unit.symbol'),nullable=False)
    product=relationship('ReagentType',primaryjoin='ReagentType.id==Ingredient.product_id',backref=backref('ingredients'))
    reagent=relationship('ReagentType',primaryjoin='ReagentType.id==Ingredient.reagent_id') #if really want to see what this is used in can add backref but not needed atm
    #FIXME do we want the reference to the ingredient to be obvious, or do we want to just make a recipe reference in the product row
    def __init__(self,Product=None,Reagent=None,finalValue=None,finalPrefix=None,finalUnit=None,product_id=None,reagent_id=None):
        self.product_id=product_id
        self.reagent_id=reagent_id
        self.finalValue=finalValue
        self.finalPrefix=finalPrefix
        self.finalUnit=finalUnit
        if Product:
            if Product.id:
                self.product_id=Product.id
            else:
                raise AttributeError
        if Reagent:
            if Reagent.id:
                self.reagent_id=Reagent.id
            else:
                raise AttributeError


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



