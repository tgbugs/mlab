from database.imports import *
from sqlalchemy                         import Float
from sqlalchemy                         import ForeignKeyConstraint

from database.base import Base, HasNotes
#from notes import HasNotes

#experiment variables that are sub mouse, everything at and above the level of the mouse is also an experimental variable that I want to keep track of independently if possible
#this means that I MIGHT want to make them experimental variables so that I can automatically tag them with the experiment/s any one of them has been involved in? viewonly

#XXX I can turn this into a webapp really fucking easily, and all i need for paper/notetaking integration is the MOTHER FUCKING RAW XML YOU FUCKS

###-------------------
###  Experiment tables
###-------------------

"""
class LED_stimulation(HasNotes, Base): #association linking an espPos to at Cell
    #id=None
    Column('esp_pos_id',Integer,ForeignKey('espposition.id'),primary_key=True) #from data.py
    Column('cell_id',Integer,ForeignKey('cell.id'),primary_key=True)
    
    LED_id=None #TODO table of LED types WITH CALIBRATION??
    stim_id=None

    dateTime=Column(DateTime,nullable=False)

    pos_z=None #from surface? standarize this please
"""
class IsTerminal:
    #TODO mixin for terminal experiments to automatically log data of death for a mouse
    #@declared_attr
    def dod(cls):
        return  None

class Experiment(Base): #FIXME there is in fact a o-m on subject-experiment, better fix that, lol jk, it is fixed ish :)
    __tablename__='experiments'
    id=Column(Integer,primary_key=True)
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False)
    startDateTime=Column(DateTime,nullable=False)
    protocol_id=Column(Integer,ForeignKey('citeable.id'))
    expmetadata=relationship('ExpMetaData',primaryjoin='Experiment.id==ExpMetaData.experiment_id') #this needs to be here for when there are things like slice experiments that have metadata instead of objects, you *could* put the metadata on the mouse and I will have to think about that, but it really seems like I am storing data on the experiment itself not on an object
    exp_type=Column(String(20),nullable=False)
    __mapper_args__ = {
        'polymorphic_on':exp_type,
        'polymorphic_identity':'experiment',
    }
    def __init__(self,Project=None,Person=None,Mouse=None,project_id=None,person_id=None,mouse_id=None,protocol_id=None,startDateTime=None):
        self.project_id=project_id
        self.person_id=person_id
        self.protocol_id=protocol_id
        self.startDateTime=startDateTime

        self.AssignID(Project)
        self.AssignID(Person)
        """
        if Project:
            if Project.id:
                self.project_id=Project.id
            else:
                raise AttributeError
        if Person:
            if Person.id:
                self.person_id=Person.id
            else:
                raise AttributeError
        """
#INSIGHT! things that are needed to make query structure work, eg acsf_id and the like do not go in metadata, metadata is really the api for analysis, so anything not direcly used in analysis should not go in metadata

'''
class Experiment(Base): #FIXME are experiments datasources? type experiment or something? or should the data from each experiment be IN the xperiment? ;_; I though we decided that the experiment points to all the data... and then the metadata is stored somehwere else again, such as a table inheriting from Data1 maybe? seems like a good idea
    """Base class to link all experiment metadata tables to DataFile tables"""
    #need this to group together the variables
    #this is the base table where each row is one experimental condition or data point, we could call it an experiment since 'Slice Experiment' would be a subtype with its own additional data
    __tablename__='experiments'
    #FIXME shitfuck, I want this to be metadata but that means I need a new unit for each new cell/pair of cells because they are the subjects in this case ;_;

    id=Column(Integer,primary_key=True)
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False) #FIXME problmes with corrispondence, make sure the person is on the project??? CHECK
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False) #this is here to provide context for the exp

    #TODO terminal experiments should automatically add date of death, since for slice prep for example I do sort of record that

    startDateTime=Column(DateTime,nullable=False)
    protocol_id=Column(Integer,ForeignKey('citeable.id'))

    expmetadata=relationship('ExpMetaData',primaryjoin='Experiment.id==ExpMetaData.experiment_id')
    datafiles=relationship('DataFile',primaryjoin='Experiment.id==DataFile.experiment_id',backref=backref('experiment',uselist=False))
    exp_type=Column(String(20),nullable=False)

    __mapper_args__ = {
        'polymorphic_on':exp_type,
        'polymorphic_identity':'experiment',
        #'with_polymorphic':'*' #FIXME we don't really need this on but it wasnt the source of the slowdown
    }
    def __init__(self,Project=None,Person=None,Mouse=None,project_id=None,person_id=None,mouse_id=None,protocol_id=None,startDateTime=None):
        #super.__init__() #:( doesnt work :(
        #self.dateTime=datetime.utcnow() #FIXME PLEASE COME UP WITH A STANDARD FOR THIS
        self.project_id=project_id
        self.person_id=person_id
        self.mouse_id=mouse_id
        self.protocol_id=protocol_id
        self.startDateTime=startDateTime
        if Project:
            if Project.id:
                self.project_id=Project.id
            else:
                raise AttributeError
        if Person:
            if Person.id:
                self.person_id=Person.id
            else:
                raise AttributeError
        if Mouse:
            if Mouse.id:
                self.mouse_id=Mouse.id
            else:
                raise AttributeError

    #TODO every time a collect an data file of any type and it is determined to be legit (by me) then it should all be stored
    #the experiment is basically the 'dataobject' that links the phenomena studied to the data about it(them)
'''

#FIXME do not add new experiments until you know what their parameters will be
#furthermore, I may try to get away with just using expmetadata and df metadata for everything
#using externally defined templates that know all the dimesions of the experiment
#the only thing I might need to add is calibraiton, but I think I can control THAT at the datasource
#ah balls, still have to have some way to track slices and cells :(
#WAIT! TODO just make it so we can add experiments to slices and /or cells! :D yay!


class SlicePrep(Experiment): #TODO this is probably an experiment...
    """ Notes on the dissection and slice prep"""
    __tablename__='sliceprep'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    mouse_id=Column(Integer,ForeignKey('mouse.id')) #works with backref from mouse
    chamber_id=Column(Integer,ForeignKey('hardware.id'))
    sucrose_id=Column(String,ForeignKey('reagents.name'),nullable=False) #FIXME metadata??!
    #expmetadata=relationship('ExpMetaData') #FIXME For stuff like 'ketxyl volume'? vs explicit columns?!?!
    slices=relationship('Slice',primaryjoin='SlicePrep.id==foreign(Slice.prep_id)',backref=backref('prep',uselist=False))
    mouse=relationship('Mouse',primaryjoin='SlicePrep.mouse_id==Mouse.id',backref=backref('prep',uselist=False))

    __mapper_args__={'polymorphic_identity':'slice prep'}

    def __init__(self,Project=None,Person=None,Mouse=None,project_id=None,person_id=None,mouse_id=None,protocol_id=None,startDateTime=None,sucrose_id=None): #FIXME
        self.project_id=project_id
        self.person_id=person_id
        self.protocol_id=protocol_id
        self.startDateTime=startDateTime
        self.sucrose_id=sucrose_id
        self.mouse_id=mouse_id

        self.AssignID(Project)
        self.AssignID(Person)
        self.AssignID(Mouse)

#INSIGHT! things that are needed to make query structure work, eg acsf_id and the like do not go in metadata, metadata is really the api for analysis, so anything not direcly used in analysis should not go in metadata

#TODO FIXME need to dissociate PROCEDURE from DATA, the CONDITIONS for that day are DIFFERENT from the actual individual experimetns
class Patch(Experiment):
    """Ideally this should be able to accomadate ALL the different kinds of slice experiment???"""
    __tablename__='patch'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)

    #experimental conditions
    #TODO transition these to refer to the individual lot
    acsf_id=Column(String,ForeignKey('reagents.name'),nullable=False) #need to come up with a way to constrain
    internal_id=Column(String,ForeignKey('reagents.name'),nullable=False) #FIXME hopefully I won't run out of internal or have to switch batches!???! well, that suggests that the exact batch might not be releveant here but instead could be check by date some other way

    cells=relationship('Cell',primaryjoin='Patch.id==foreign(Cell.experiment_id)',backref=backref('experiment',uselist=False))

    #pharmacology
    #TODO might should add a pharmacology data table similar to the metadata table but with times?

    __mapper_args__ = {'polymorphic_identity':'slice'}


class ChrSomWholeCell(Patch): #FIXME could do a 'HasLedStim' or something?
    __tablename__='chrsomsliceexperiment'
    id=Column(Integer,ForeignKey('patch.id'),primary_key=True,autoincrement=False)
    led_id=Column(Integer,ForeignKey('hardware.id'))
    __mapper_args__ = {'polymorphic_identity':'chr_som_slice'}

"""
class _HistologyExperiment(Experiment):
    __tablename__='histologyexperiment'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    __mapper_args__ = {'polymorphic_identity':'histology'}


class _IUEPExperiment(Experiment):
    __tablename__='iuepexperiment'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    #dam=realationship('Mouse') #FIXME maybe don't need this, since the mouse will backprop anyway
    matingrecord_id=Column(Integer,ForeignKey('matingrecord.id'))
    mice=relationship('Mouse',primaryjoin='IUEPExperiment.mouse_id==foreign(Mouse.dam_id)',backref=backref('iuep',uselist=False)) #FIXME somehow mouse could also have a @hybrid_property of 'est age at iuep...'
    __mapper_args__ = {'polymorphic_identity':'iuep'}

class _WaterRecord(Experiment):
    __tablename__='waterrecords'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    #TODO this does not need to be done right now, just make sure it will integrate easily
    #do we keep weight's here or somehwere else, is there any other reason why a 'normal' mouse would need to be weighed? sure the mouse HAS a weight, but does that mean that the mouse table should be where we keep it? it changes too
    #same argument applies to sex and how to deal with changes to that, and whether it is even worth noting
    #somehow this reminds me that when weaning mice need to make sure that their cages get matched up properly... well, that's the users job
    #id=None
    #mouse_id=Column(Integer,ForeignKey('mouse.id'),primary_key=True)
    #dateTime=Column(DateTime, primary_key=True) #NOTE: in this case a dateTime IS a valid pk since these are only updated once a day
    #TODO lol the way this is set up now these classes should actually proabaly DEFINE metadata records at least for simple things like this where the only associated object is a mouse which by default experiment asssociates with, maybe I SHOULD move the mouse_id to class MouseExperiment?!?!?!

#
#organism mixins??? no, bad way to do it, still haven't figured out the good way
"""
