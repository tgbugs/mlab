from database.imports import *
from sqlalchemy                         import Float

from database.base import Base, HasNotes
#from notes import HasNotes

#experiment variables that are sub mouse, everything at and above the level of the mouse is also an experimental variable that I want to keep track of independently if possible
#this means that I MIGHT want to make them experimental variables so that I can automatically tag them with the experiment/s any one of them has been involved in? viewonly


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

    dateTime=None

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

class Experiment(Base):
    """Base class to link all experiment metadata tables to DataFile tables"""
    #need this to group together the variables
    #this is the base table where each row is one experimental condition or data point, we could call it an experiment since 'Slice Experiment' would be a subtype with its own additional data
    __tablename__='experiments'

    id=Column(Integer,primary_key=True)
    project_id=Column(Integer,nullable=False) #FIXME I suppose in a strange world experiments can belong to two projects damn it...
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False)
    #subject_id=Column(Integer,nullable=False)
    #ForeignKeyConstraint('Experiment.subject_id',['mouse.id','organism.id','cellCulture.id'])
    dateTime=Column(DateTime,nullable=False)
    protocol_id=Column(Integer,ForeignKey('protocols.id'))
    datafiles=relationship('DataFile',backref=backref('experiment',uselist=False))
    experimenter_id=Column(Integer,ForeignKey('people.id')) #FIXME problmes with corrispondence
    constants=None
    exp_type=Column(String,nullable=False)
    #nope, we're just going to have some data duplication, because each datafile will have to say 'ah yes, I was associated with this cell, this esp position etc'
    #variables=None #FIXME these go in metadata, unforunately there is something that varies every time, but THAT should be stored somewhere OTHER than the main unit of analysis on a set of datafiles???
    __mapper_args__ = {
        'polymorphic_on':exp_type,
        'polymorphic_identity':'experiment',
        #'with_polymorphic':'*'
    }

    #TODO every time a collect an data file of any type and it is determined to be legit (by me) then it should all be stored
    #the experiment is basically the 'dataobject' that links the phenomena studied to the data about it(them)
    #turns out that the 'datafile' IS the normalized place to link all these things together, 


class SliceExperiment(Experiment):
    """Ideally this should be able to accomadate ALL the different kinds of slice experiment???"""
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)

    acsf_id=Column(Integer,ForeignKey('solution.id'),nullable=False) #need to come up with a way to constrain
    #acsf_id #to prevent accidents split teh acsf and internal into different tables to allow for proper fk constraints? NO, not flexible enough
    #internal_id

    #pharmacology

    #abffile

    __table_args__ = {'extend_existing':True}
    __mapper_args__ = {'polymorphic_identity':'acute slice'}

class HistologyExperiment(Experiment):
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)
    __table_args__ = {'extend_existing':True}
    __mapper_args__ = {'polymorphic_identity':'histology'}


class IUEPExperiment(Experiment):
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)
    __table_args__ = {'extend_existing':True}
    __mapper_args__ = {'polymorphic_identity':'iuep'}
