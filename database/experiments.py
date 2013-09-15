from database.imports import *
from sqlalchemy                         import Float

from database.base import Base, HasNotes
#from notes import HasNotes

#experiment variables that are sub mouse, everything at and above the level of the mouse is also an experimental variable that I want to keep track of independently if possible
#this means that I MIGHT want to make them experimental variables so that I can automatically tag them with the experiment/s any one of them has been involved in? viewonly

#XXX I can turn this into a webapp really fucking easily, and all i need for paper/notetaking integration is the MOTHER FUCKING RAW XML YOU FUCKS

###-------------------
###  Experiment tables
###-------------------

class ExperimentVariable(Base):
    pass


class Slice(HasNotes, Base):
    id=None
    #id=Column(Integer,primary_key=True,autoincrement=False)
    mouse_id=Column(Integer,ForeignKey('mouse.id'),primary_key=True) #works with backref from mouse
    startDateTime=Column(DateTime,primary_key=True) #these two keys should be sufficient to ID a slice and I can use ORDER BY startDateTime and query(Slice).match(id=Mouse.id).count() :)
    #hemisphere
    #slice prep data can be querried from the mouse_id alone, since there usually arent two slice preps per mouse
    #positionAP

    cells=relationship('Cell',primaryjoin='Cell.slice_sdt==Slice.startDateTime',backref=backref('slice',uselist=False))


class StimulusEvent(HasNotes, Base): #VARIABLE
    #id=None
    mouse_id=None
    slice_id=None
    cell_id=None
    #this is part of the DATAFILE metadata because it is a variable in the experiment

class LED_stimulation(HasNotes, Base): #association linking an espPos to at Cell
    #id=None
    Column('esp_pos_id',Integer,ForeignKey('espposition.id'),primary_key=True) #from data.py
    Column('cell_id',Integer,ForeignKey('cell.id'),primary_key=True)
    
    LED_id=None #TODO table of LED types WITH CALIBRATION??
    stim_id=None

    dateTime=Column(DateTime,nullable=False)

    pos_z=None #from surface? standarize this please

cell_to_cell=Table('cell_to_cell', Base.metadata, 
                   Column('cell_1_id',Integer,ForeignKey('cell.id'),primary_key=True),
                   Column('cell_2_id',Integer,ForeignKey('cell.id'),primary_key=True)
                  )

class Cell(HasNotes, Base):
    #FIXME this Cell class is NOT extensible
    #probably should use inheritance
    #id=None #FIXME fuck it dude, wouldn't it be easier to just give them unqiue ids so we don't have to worry about datetime? or is it the stupid sqlite problem?
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False)
    slice_sdt=Column(Integer,ForeignKey('slice.startDateTime'),nullable=False) #FIXME NO DATETIME PRIMARY KEYS
    hs_id=Column(Integer,ForeignKey('headstage.id'),nullable=False)#,ForeignKey('headstages.id')) #FIXME critical
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False) #TODO we might be able to link cells to headstages and all that other shit more easily, keeping the data on the cell itself in the cell, tl;dr NORMALIZE!
    #hs_id=Column(Integer,ForeignKey('headstage.channel'),primary_key=True)#,ForeignKey('headstages.id')) #FIXME critical
    #hs_amp_serial=Column(Integer,ForeignKey('headstage.amp_serial'),primary_key=True)#,ForeignKey('headstages.id')) #FIXME critical
    startDateTime=Column(DateTime,nullable=False)

    wholeCell=None #FIXME these might should go in analysis??? no...
    loosePatch=None

    #mark=Column(String(1)) #marks are VERY unlikely to be reused, do not store in the database direcly handle getting cell position via them elsewhere
    esp_x=Column(Float) #FIXME positions need
    esp_y=Column(Float)
    pos_z_rel=Column(Float)

    #TODO abfFiles are going to be a many-many relationship here....
    abfFile_channel=None #FIXME this nd the headstage serials seems redundant but... wtf? I have to link them somehow

    breakInTime=None

    rheobase=None

    #exp_parts=relationship('Cell',primaryjoin='Cell.experiment_id==remote(Cell.experiment_id)',back_populates='exp_parts') #FIXME consider remote_side, sqlalchemy is schitzo, it wants remote or foreign
    cell_1=relationship('Cell',
                        secondary=cell_to_cell,
                        primaryjoin='Cell.id==cell_to_cell.c.cell_2_id',
                        secondaryjoin='Cell.id==cell_to_cell.c.cell_1_id',
                        backref='cell_2',
                        #viewonly=True #FIXME this shouldn't be needed, I follo the example exactly
                       )


    #exp_parts=relationship('Cell',backref=backref('exp_parts',remote_side[id]),back_populates='exp_parts') #FIXME consider remote_side, sqlalchemy is schitzo, it wants remote or foreign

    #FIXME how to do led stim linkage properly :/ it is a many to many... association??? or table? association between cell and stim position is probably best?
    
    #analysis_id=None #put the analysis in another table that will backprop here


class SlicePrep(HasNotes, Base):
    """ Notes on the dissection and slice prep"""
    id=Column(Integer,ForeignKey('mouse.id'),primary_key=True) #works with backref from mouse
    #chamber_type
    #sucrose_id
    #sucrose reference to table of solutions

class IsTerminal:
    #TODO mixin for terminal experiments to automatically log data of death for a mouse
    #@declared_attr
    def dod(cls):
        return  None


class Experiment(Base): #FIXME are experiments datasources? type experiment or something? or should the data from each experiment be IN the xperiment? ;_; I though we decided that the experiment points to all the data... and then the metadata is stored somehwere else again, such as a table inheriting from Data1 maybe? seems like a good idea
    """Base class to link all experiment metadata tables to DataFile tables"""
    #need this to group together the variables
    #this is the base table where each row is one experimental condition or data point, we could call it an experiment since 'Slice Experiment' would be a subtype with its own additional data
    __tablename__='experiments'

    id=Column(Integer,primary_key=True)
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False) #FIXME problmes with corrispondence, make sure the person is on the project??? CHECK
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False) #FIXME there are too many subjects to keep them all in one table, could use a check to make sure that the subject id matches the experiment type? actually, joined table inheritance might work, but it adds another column to all the organisms ;_; derp, we'll worry about that when the time comes

    #TODO terminal experiments should automatically add date of death, since for slice prep for example I do sort of record that

    startDateTime=Column(DateTime,nullable=False)
    protocol_id=Column(Integer,ForeignKey('protocols.id'))

    expmetadata=relationship('MetaData',primaryjoin='Experiment.id==MetaData.experiment_id')
    datafiles=relationship('DataFile',primaryjoin='Experiment.id==DataFile.experiment_id',backref=backref('experiment',uselist=False))
    exp_type=Column(String,nullable=False)

    __mapper_args__ = {
        'polymorphic_on':exp_type,
        'polymorphic_identity':'experiment',
        #'with_polymorphic':'*' #FIXME we don't really need this on but it wasnt the source of the slowdown
    }
    def __init__(self,Project=None,Person=None,Mouse=None,project_id=None,person_id=None,mouse_id=None,protocol_id=None,dateTime=None):
        #super.__init__() #:( doesnt work :(
        #self.dateTime=datetime.utcnow() #FIXME PLEASE COME UP WITH A STANDARD FOR THIS
        self.project_id=project_id
        self.person_id=person_id
        self.mouse_id=mouse_id
        self.protocol_id=protocol_id
        self.dateTime=dateTime
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


class SliceExperiment(Experiment):
    """Ideally this should be able to accomadate ALL the different kinds of slice experiment???"""
    __tablename__='sliceexperiment'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)

    #acsf_id=Column(Integer,ForeignKey('solution.id'),nullable=False) #need to come up with a way to constrain
    #acsf_id #to prevent accidents split teh acsf and internal into different tables to allow for proper fk constraints? NO, not flexible enough
    #internal_id

    #pharmacology
    #TODO might should add a pharmacology data table similar to the metadata table but with times?

    __mapper_args__ = {'polymorphic_identity':'slice'}


class HistologyExperiment(Experiment):
    __tablename__='histologyexperiment'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    __mapper_args__ = {'polymorphic_identity':'histology'}


class IUEPExperiment(Experiment):
    __tablename__='iuepexperiment'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    #dam=realationship('Mouse') #FIXME maybe don't need this, since the mouse will backprop anyway
    matingrecord_id=Column(Integer,ForeignKey('matingrecord.id'))
    mice=relationship('Mouse',primaryjoin='IUEPExperiment.mouse_id==foreign(Mouse.dam_id)',backref=backref('iuep',uselist=False)) #FIXME somehow mouse could also have a @hybrid_property of 'est age at iuep...'
    __mapper_args__ = {'polymorphic_identity':'iuep'}

class WaterRecord(Experiment):
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

#organism mixins??? no, bad way to do it, still haven't figured out the good way
class MouseExperiment: 
    #@declared_attr
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False) #FIXME add 'mouse experiment type for further inheritance???'
