from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasReagents, HasHardware, HasSubjects, HasReagentTypes, HasDataSources, HasMetaDataSources

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


class ExperimentType(HasReagentTypes, HasHardware, HasDataSources, HasMetaDataSources, Base):
    """this stores all the constant data about an experiment that will be done many times"""
    #TODO addition of new data does not trigger version bump but any changes to existing entries should
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(String(30),nullable=False)
    abbrev=Column(String)
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False)
    repository_url=Column(Integer,ForeignKey('repository.url')) #FIXME does this make any sense here?
    repository=relationship('Repository',uselist=False) #these *could* change before the experiments were done... that is trouble some... BUT we can always rename and casscade the change...
    methods_id=Column(Integer,ForeignKey('citeable.id'))

    experiments=relationship('Experiment',backref=backref('type',uselist=False))

    #TODO there are simpy too many datasources and metadata sources to access them directly every time from the whole list, therefore we will include them here to make finding them easy but not to constrain them...
    #FIXME datasources being tied directly to REAL hardware could be a problem ;_;
    #need a way to specify the types of data without being forced to add a new experiment type every time hardware changes or loose the record of the old hardware configuration...
    #RESPONSE: not actually a problem because atm sources are not tied directly to hardware and in theory I could just keep a history table for links between sources and hardware... or better yet just do that by linking data sources to hardware types and ha... fuck... integrety failures EVERYWHERE ;_;

    @property
    def reagents(self):
        return [rt.getCurrentLot() for rt in self.reagenttypes] #FIXME

    def __init__(self,name=None,abbrev=None,Project=None,Person=None,Repository=None,Methods=None,Hardware=[],ReagentTypes=[],MetaDataSources=[],project_id=None,person_id=None,repository_url=None,methods_id=None):
        self.name=name
        self.abbrev=abbrev
        self.project_id=project_id
        self.person_id=person_id
        self.methods_id=methods_id

        self.AssignID(Project)
        self.AssignID(Person)

        self.reagenttypes.extend(ReagentTypes)
        self.hardware.extend(Hardware)
        self.metadatasources.extend(MetaDataSources)

        if Methods:
            if Methods.id:
                self.methods_id=Methods.id
            else:
                raise AttributeError

    def __repr__(self):
        return super().__repr__()


class Experiment(HasMetaData, HasReagents, HasSubjects, Base):
    __tablename__='experiments'
    id=Column(Integer,primary_key=True)
    startDateTime=Column(DateTime,default=datetime.now())
    endDateTime=Column(DateTime) #TODO
    type_id=Column(Integer,ForeignKey('experimenttype.id'),nullable=False)

    def __init__(self,ExpType=None,Reagents=[],Subjects=[],type_id=None,startDateTime=None):
        self.startDateTime=startDateTime
        self.reagents.extend(Reagents)
        self.subjects.extend(Subjects)
        self.type_id=type_id
        if ExpType:
            if ExpType.id:
                self.type_id=ExpType.id
                self.reagents.extend(ExpType.reagents)
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


