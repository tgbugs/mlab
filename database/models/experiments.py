from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasReagents, HasHardware, HasReagentTypes, HasDataFileSources, HasMetaDataSources, HasMdsHwRecords, HasDfsHwRecords

###-------------------
###  Experiment tables
###-------------------

    
#TODO in theory what we want is for experiments to have a m-m on itself to convey logical connections, in which case a mating record is just an experiment.... HRM, think on this... we certainly want the m-m for logical depenece I think

#why experiment type instead of inheritance? because I don't want to force users to learn sqlalchemy, furthermore, doccumenting experiments in code defeats the purpose of saving all of this stuff in a database from a record keeping point of view
class ExperimentType(HasReagentTypes, HasDataFileSources, HasMetaDataSources, Base):
    """this stores all the constant data about an experiment that will be done many times"""
    #TODO logical relationships between experiments could be manifest here, but THAT is a project for another day
    #TODO addition of new data does not trigger version bump but any changes to existing entries should
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(String(30),nullable=False)
    abbrev=Column(String)
    #repository_url=Column(String,ForeignKey('repository.url')) #FIXME does this make any sense here?
    #repository=relationship('Repository',uselist=False) #these *could* change before the experiments were done... that is trouble some... BUT we can always rename and casscade the change...
    methods_id=Column(Integer,ForeignKey('citeable.id'))

    experiments=relationship('Experiment',backref=backref('type',uselist=False))

    @property
    def reagents(self):
        return [rt.currentLot for rt in self.reagenttypes] #FIXME

    def __init__(self,name=None,abbrev=None,Repository=None,Methods=None,ReagentTypes=[],MetaDataSources=[],repository_url=None,methods_id=None):
        self.name=name
        self.abbrev=abbrev
        self.methods_id=methods_id

        self.reagenttypes.extend(ReagentTypes)
        self.metadatasources.extend(MetaDataSources) #hardware is handled here now

        if Methods:
            if Methods.id:
                self.methods_id=Methods.id
            else:
                raise AttributeError

    def __repr__(self):
        return super().__repr__()


#TODO on a per-experiment basis I need bindings between hardware and metadatasources
#TODO AND I need a binding between datafiles/datafile channels and subjects
#in biology there are expeirments that generate data, or data and subjects, if they generate only subjects then they should probably have some data to go along with them or the science might be bad
class Experiment(HasMetaData, HasReagents, HasMdsHwRecords, HasDfsHwRecords, Base): #FIXME generation experiment!???!
    #TODO what/who is the REAL subject of experiment data? the procedure? the experimenter? the generated subjects? probably it is actually stuff that is used as a sanity check against the protocol... hrm... HRM
    __tablename__='experiments'
    id=Column(Integer,primary_key=True)
    type_id=Column(Integer,ForeignKey('experimenttype.id'),nullable=False)

    project_id=Column(Integer,ForeignKey('project.id'),nullable=False) #if i keep track of these at the level of experiment type then everything becomes problematic if I want to change the project or experiment or reuse stuff, but if I want to record WHO did the experiment as an experimental variable...
    #also the being of the experiment type is not defined by which project it is for but project_id is a nice  way to tie everything together...
    #maybe metadata for an experiment is who did it?
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False)

    startDateTime=Column(DateTime,default=datetime.now())
    endDateTime=Column(DateTime) #TODO

    @validates('type_id','endDateTime','startDateTime')
    def _wo(self, key, value): return _write_once(key, value)

    def setEndDateTime(self,dateTime=None):
        if not self.endDateTime: #FIXME I should be able to do this with validates
            if not dateTime:
                self.endDateTime=datetime.now()
            else:
                self.endDateTime=dateTime
        else:
            raise Warning('endDateTime has already been set!')

    def __init__(self,type_id,project_id=None,person_id=None,Reagents=[],Subjects=[],startDateTime=None):
        self.type_id=int(type_id)
        if project_id: #FIXME move to experiment type? if exptype is hierarchical can duplicate...
            self.project_id=(project_id)
        if person_id:
            self.person_id=int(person_id)

        self.startDateTime=startDateTime

        self.AssignID(Project)
        self.AssignID(Person)

        self.reagents.extend(Reagents)
        self.subjects.extend(Subjects)

        if ExpType:
            if ExpType.id:
                self.type_id=ExpType.id
                self.reagents.extend(ExpType.reagents)
            else:
                raise AttributeError

#TODO: figure out the base case for experiments (ie which subjects) for
#TODO this does not need to be done right now, just make sure it will integrate easily
#do we keep weight's here or somehwere else, is there any other reason why a 'normal' mouse would need to be weighed? sure the mouse HAS a weight, but does that mean that the mouse table should be where we keep it? it changes too
#same argument applies to sex and how to deal with changes to that, and whether it is even worth noting
#somehow this reminds me that when weaning mice need to make sure that their cages get matched up properly... well, that's the users job
#id=None
#mouse_id=Column(Integer,ForeignKey('mouse.id'),primary_key=True)
#dateTime=Column(DateTime, primary_key=True) #NOTE: in this case a dateTime IS a valid pk since these are only updated once a day
#TODO lol the way this is set up now these classes should actually proabaly DEFINE metadata records at least for simple things like this where the only associated object is a mouse which by default experiment asssociates with, maybe I SHOULD move the mouse_id to class MouseExperiment?!?!?!

class Protocol:
    def __init__(self,SubjectClass,order_list_of_things_to_do):
        #the problme is that we cant just use a list of names because everything isn't a datasource...
        #I guess they could be, but that would break stuff? maybe it wont?
        pass


