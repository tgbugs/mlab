from database.imports import *
from database.base import Base
from database.mixins import HasNotes, HasMetaData

###-------------------
###  Experiment tables
###-------------------

#experiments are things done on subjects (cells, mice, slices) they are referenced by the row containing the subjects, thus subject-exp is many-one, HOWEVER, for NON TERMINAL experiments the relationship could be many-many :/ #TODO

#FIXME do not add new experiments until you know what their parameters will be
#furthermore, I may try to get away with just using expmetadata and df metadata for everything
#using externally defined templates that know all the dimesions of the experiment
#the only thing I might need to add is calibraiton, but I think I can control THAT at the datasource
#ah balls, still have to have some way to track slices and cells :(
#WAIT! TODO just make it so we can add experiments to slices and /or cells! :D yay!

#INSIGHT! things that are needed to make query structure work, eg acsf_id and the like do not go in metadata, metadata is really the api for analysis, so anything not direcly used in analysis should not go in metadata

#TODO FIXME need to dissociate PROCEDURE from DATA, the CONDITIONS for that day are DIFFERENT from the actual individual experimetns
#TODO handling multiple subjects is NOT handled EXPLICITLY here, links between methods and subject type are probably probably not in the domain of things we should enforce

class Experiment(HasMetaData, Base): #FIXME there is in fact a o-m on subject-experiment, better fix that, lol jk, it is fixed ish :)
    __tablename__='experiments'
    id=Column(Integer,primary_key=True)
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False)
    startDateTime=Column(DateTime,nullable=False)
    methods_id=Column(Integer,ForeignKey('citeable.id'))
    #expmetadata=relationship('ExpMetaData',primaryjoin='Experiment.id==ExpMetaData.experiment_id') #this needs to be here for when there are things like slice experiments that have metadata instead of objects, you *could* put the metadata on the mouse and I will have to think about that, but it really seems like I am storing data on the experiment itself not on an object
    exp_type=Column(String(20),nullable=False)
    __mapper_args__ = {
        'polymorphic_on':exp_type,
        'polymorphic_identity':'experiment',
    }
    def __init__(self,Project=None,Person=None,Methods=None,project_id=None,person_id=None,methods_id=None,startDateTime=None):
        self.project_id=project_id
        self.person_id=person_id
        self.methods_id=methods_id
        self.startDateTime=startDateTime

        self.AssignID(Project)
        self.AssignID(Person)
        if Methods:
            if Methods.id:
                self.methods_id=Methods.id
            else:
                raise AttributeError


class SlicePrep(Experiment): #it works better to have this first because I can create a sliceprep object and THEN pick the mouse :)
    """ Notes on the dissection and slice prep"""
    __tablename__='sliceprep'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    chamber_id=Column(Integer,ForeignKey('hardware.id'))
    sucrose_id=Column(String,ForeignKey('reagents.name'),nullable=False) #FIXME metadata??!
    #expmetadata=relationship('ExpMetaData') #FIXME For stuff like 'ketxyl volume'? vs explicit columns?!?!
    slices=relationship('Slice',primaryjoin='SlicePrep.id==foreign(Slice.prep_id)',backref=backref('prep',uselist=False))
    mouse=relationship('Mouse',primaryjoin='SlicePrep.id==foreign(Mouse.experiment_id)',backref=backref('prep',uselist=False),uselist=False) #FIXME mice *should* be able to be part of more than one experiment for some types damn it

    __mapper_args__={'polymorphic_identity':'slice prep'}

    #TODO 'MakeSlice????'

    def __init__(self,Project=None,Person=None,Methods=None,project_id=None,person_id=None,methods_id=None,startDateTime=None,sucrose_id=None): #FIXME
        super().__init__(Project=Project,Person=Person,Methods=Methods,project_id=project_id,person_id=person_id,methods_id=methods_id,startDateTime=startDateTime)
        self.sucrose_id=sucrose_id


class Patch(Experiment): #FIXME should this be a o-o with slice prep???
    """Ideally this should be able to accomadate ALL the different kinds of slice experiment???"""
    __tablename__='patch'
    id=Column(Integer,ForeignKey('experiments.id'),primary_key=True,autoincrement=False)
    #mouse_id=Column(Integer,ForeignKey('mouse.id')) #FIXME
    #slice_id=None #FIXME shit, do I put this here??!?!!! THINK THINK THINK
    #experimental conditions
    #TODO transition these to refer to the individual lot
    acsf_id=Column(String,ForeignKey('reagents.name'),nullable=False) #need to come up with a way to constrain
    internal_id=Column(String,ForeignKey('reagents.name'),nullable=False) #FIXME hopefully I won't run out of internal or have to switch batches!???! well, that suggests that the exact batch might not be releveant here but instead could be check by date some other way

    cells=relationship('Cell',primaryjoin='Patch.id==foreign(Cell.experiment_id)',backref=backref('experiment',uselist=False))
    #mouse=relationship('Mouse',primaryjoin='Patch.mouse_id==Mouse.id',backref=backref('prep',uselist=False)) #FIXME super over connected :/

    #pharmacology
    #TODO might should add a pharmacology data table similar to the metadata table but with times?

    __mapper_args__ = {'polymorphic_identity':'slice'}
    
    def __init__(self,Prep=None,acsf=None,Internal=None,Methods=None,Project=None,Person=None,project_id=None,person_id=None,prep_id=None,acsf_id=None,internal_id=None,methods_id=None,startDateTime=None):
        super().__init__(Person=Person,Methods=Methods,project_id=project_id,person_id=person_id,methods_id=methods_id,startDateTime=startDateTime)
        self.acsf_id=acsf_id
        self.internal_id=internal_id
        if Prep:
            if Prep.id:
                self.project_id=Prep.project_id
                self.person_id=Prep.person_id #FIXME different person could prep vs patch
            else:
                raise AttributeError
        if acsf:
            if acsf.name:
                self.acsf_id=acsf.name
            else:
                raise AttributeError
        if Internal:
            if Internal.name:
                self.internal_id=Internal.name
            else:
                raise AttributeError



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

"""
