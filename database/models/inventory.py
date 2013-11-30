from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasCiteables, HasTreeStructure, HasExperiments, HasProperties

###-----------------------------------
###  Hardware inventory, aka rig parts
###-----------------------------------


class HardwareType(Base):
    id=Column(String(30),primary_key=True)
    description=Column(Text)
    hardware=relationship('Hardware',backref=backref('type',uselist=False)) #primaryjoin='HardwareType.id==Hardware.type_id',
    def __init__(self,id=None,description=None):
        self.id=id
        self.description=description
    def __str__(self):
        return '%s'%self.id
    def __repr__(self):
        return '\n%s\n%s%s'%(self.id, self.description, ''.join([thing.strHelper(1) for thing in self.hardware]))


class Hardware(HasMetaData, HasExperiments, HasCiteables, HasTreeStructure, Base): #FIXME unique_id back to the base? ehhhh???? tradeoffs
    #TODO implement something like has ontogeny for has tools and require an experiment
    #even if it is just sanity checking stuff there will be a record of stuff like the pull protocol
    #FIXME well, ideally you just want to keep track of when it changes because it is technically a protocol
    #which should remain fixed, even though protocols could be considered data the idea is to use them to
    #constrain variance and variability...
    __tablename__='hardware'
    id=Column(Integer,primary_key=True)
    name=Column(String,unique=True,nullable=False) #FIXME unique or not unique? also pk? or move to properties
    type_id=Column(String,ForeignKey('hardwaretype.id'),nullable=False) #FIXME this should be like keywords the point is to make life easier not to put up walls
    parent_id=Column(Integer,ForeignKey('hardware.id')) #FIXME pipettes are hardware made by hardware using a certain protocol, looks similar to an experiment and so physical hierarchy and generative heirarchy are different, 
    properties=Column(DictType)
    tools=None #relationship('Hardware') #TODO many to one used w/ blueprint to make stuff, WARNING this approach is almost certainly overly complicated and should be scrapped #FIXME super cool, when you have a mutable tree structure then you CAN have ontogeny and part-whole between the same types of objects... does raise the issue that experiments are starting to look awefully similar to protocols in the sense that when pulling pipettes there isn't really any... wait, yes there is, the exact parameteres of the puller on that day... sweet!
    children=relationship('Hardware',primaryjoin='Hardware.id==Hardware.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))

    #moved all these to properties, unique_id, model, manufactuere

    def __init__(self,type_id=None,parent_id=None,name=None,Citeables=(),Properties={}):
        self.type_id=str(type_id)
        if self.parent_id is not None:
            self.parent_id=int(parent_id)
        self.name=name
        self.citeables.extend(Citeables)
        self.properties=Properties

    def strHelper(self,depth=0):
        ts='\t'*depth
        return '%s%s'%(ts,self.name)

    def __repr__(self):
        name=None
        parent=None
        children=None
        try: name=self.name
        except: pass
        try: parent=self.parent.strHelper()
        except: pass
        try: children=''.join([s.strHelper(1) for s in self.children])
        except: pass
        return '\n%s %s son of %s father to %s\n\twith Properties %s\n\tand MetaData\n%s'%(self.type_id.capitalize(),name,parent,children,self.properties,'\n'.join([m.strHelper(1) for m in self.metadata_]))


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
    formula=Column(String,unique=True) #iupac
    abbrev=Column(String,unique=True)
    molarMass=None #FIXME should this be metadata?
    #TODO: usage rate

    @property
    def unusedLots(self):
        return [lot for lot in self.lots if not lot.endDateTime]

    @property
    def currentLot(self): #assuming oldest first
        if self.unusedLots:
            return sorted(self.unusedLots, key=lambda lot: lot.startDateTime)[0] #oldest not used, might also try in place if it doesnt matter
        else:
            #raise Warning('You don\'t have any unused lots left! Did you forget to make them?!')
            print('You don\'t have any unused lots left! Did you forget to make them?!')
            return None

    def __repr__(self):
        return super().__repr__('name')


#TODO how to use experiments on reagents to optimize a solution/procedure
class Reagent(HasMetaData, HasExperiments, Base): #TODO HasReagents??!
    """actual instances of reagents that are made"""
    __tablename__='reagents'
    id=Column(Integer,primary_key=True) #this can function as a lot number
    type_id=Column(Integer,ForeignKey('reagenttypes.id'),nullable=False)
    startDateTime=Column(DateTime,default=datetime.now)
    endDateTime=Column(DateTime)
    type=relationship('ReagentType',backref='lots',uselist=False) #FIXME
    #TODO reorder/remake if current amount < x
    #reagentmetadata=relationship('ReaMetaData',primaryjoin='ReagentLot.id==ReaMetaData.reagent_id',backref='reagent') #FIXME make this a m-m self referential association ? this won't let me keep track of the individual lots of stuff I use to make a solution or a stock though... think about that
    def __init__(self,type_id=None,lotNumber=None,startDateTime=None,endDateTime=None):
        self.type_id=int(type_id)
        self.startDateTime=startDateTime
        self.endDateTime=endDateTime

###----------------------------------------------
###  Ingredient association table to make recipes
###----------------------------------------------

class Ingredient(Base): #FIXME make this versioned
    #TODO figure out how to query this to make a full on recipe... probably via recipe in ReagentType...
        #the full recipe should proceed with steps and take the value from the scale
    #TODO track history such that any changes to a recipe are recorded and the original recipe stays associated
    #HALP HOW DO I DO THAT? versioned tables??? seems reasonabled
    __tablename__='ingredients'
    reagent_id=Column(Integer,ForeignKey('reagenttypes.id'),primary_key=True)
    product_id=Column(Integer,ForeignKey('reagenttypes.id'),primary_key=True)
    finalValue=Column(Float(53)) #TODO enforce use of molarity or %weight...
    finalPrefix=Column(Unicode(2),ForeignKey('si_prefix.symbol'),nullable=False)
    finalUnits=Column(Unicode(3),ForeignKey('si_unit.symbol'),nullable=False)
    product=relationship('ReagentType',primaryjoin='ReagentType.id==Ingredient.product_id',backref=backref('ingredients')) #FIXME this isnt quite right, need an association proxy
    reagent=relationship('ReagentType',primaryjoin='ReagentType.id==Ingredient.reagent_id') #if really want to see what this is used in can add backref but not needed atm
    def __init__(self,product_id=None,reagent_id=None,finalValue=None,finalPrefix=None,finalUnit=None):
        self.product_id=int(product_id)
        self.reagent_id=int(reagent_id)
        self.finalValue=finalValue
        self.finalPrefix=finalPrefix
        self.finalUnit=finalUnit
