from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasReagents, HasHardware, HasSubjects, HasReagentTypes

###-------------------
###  Experiment tables
###-------------------

#experiments are things done on subjects (cells, mice, slices) they are referenced by the row containing the subjects, thus subject-exp is many-one, HOWEVER, for NON TERMINAL experiments the relationship could be many-many :/ #TODO

#TODO new experiment from experiment, so if there is an example experiment can just use that to propagate?? those are really functions that don't go in models

#FIXME do not add new experiments until you know what their parameters will be
#furthermore, I may try to get away with just using expmetadata and df metadata for everything
#using externally defined templates that know all the dimesions of the experiment
#the only thing I might need to add is calibraiton, but I think I can control THAT at the datasource
#ah balls, still have to have some way to track slices and cells :(
#WAIT! TODO just make it so we can add experiments to slices and /or cells! :D yay!
    
#TODO in theory what we want is for experiments to have a m-m on itself to convey logical connections, in which case a mating record is just an experiment.... HRM, think on this... we certainly want the m-m for logical depenece I think


class ExperimentType(HasReagentTypes, Base):
    #id=Column(Integer,primary_key=True) #FIXME
    id=Column(String(30),primary_key=True)
    abbrev=Column(String)
    def __init__(self,id=None,abbrev=None,ReagentTypes=[]):
        self.id=id
        self.abbrev=abbrev
        self.reagenttypes.extend(ReagentTypes)
    def __repr__(self):
        return super().__repr__()


class Experiment(HasMetaData, HasReagents, HasHardware, HasSubjects, Base):
    __tablename__='experiments'
    id=Column(Integer,primary_key=True)
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False)
    startDateTime=Column(DateTime,default=datetime.now())
    endDateTime=Column(DateTime) #TODO extremely useful for automatically moving to the next experiment... not that that is really an issue, but also nice for evaluating my performance
    methods_id=Column(Integer,ForeignKey('citeable.id'))
    type=Column(String(30),ForeignKey('experimenttype.id'),nullable=False)

    def __init__(self,Project=None,Person=None,ExpType=None,startDateTime=None,Methods=None,Hardware=[],Reagents=[],Subjects=[],project_id=None,person_id=None,type=None,methods_id=None):
        self.project_id=project_id
        self.person_id=person_id
        self.methods_id=methods_id
        self.startDateTime=startDateTime
        self.reagents.extend(Reagents) #TODO base experiment and then extend? or maybe a bit more complicated
        self.hardware.extend(Hardware)
        self.subjects.extend(Subjects)
        self.type=type

        self.AssignID(Project)
        self.AssignID(Person)
        if ExpType:
            if ExpType.id:
                self.type=ExpType.id
            else:
                raise AttributeError
        if Methods:
            if Methods.id:
                self.methods_id=Methods.id
            else:
                raise AttributeError

#TODO: figure out the base case for experiments (ie which subjects) for
#Slice Prep
#Patch
#IUEP
#ChrSom
#Histology
#WaterRecords
#TODO this does not need to be done right now, just make sure it will integrate easily
#do we keep weight's here or somehwere else, is there any other reason why a 'normal' mouse would need to be weighed? sure the mouse HAS a weight, but does that mean that the mouse table should be where we keep it? it changes too
#same argument applies to sex and how to deal with changes to that, and whether it is even worth noting
#somehow this reminds me that when weaning mice need to make sure that their cages get matched up properly... well, that's the users job
#id=None
#mouse_id=Column(Integer,ForeignKey('mouse.id'),primary_key=True)
#dateTime=Column(DateTime, primary_key=True) #NOTE: in this case a dateTime IS a valid pk since these are only updated once a day
#TODO lol the way this is set up now these classes should actually proabaly DEFINE metadata records at least for simple things like this where the only associated object is a mouse which by default experiment asssociates with, maybe I SHOULD move the mouse_id to class MouseExperiment?!?!?!


