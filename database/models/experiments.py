from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasReagents, HasHardware, HasReagentTypes, HasDataFileSources, HasMetaDataSources, HasMdsHwRecords, HasDfsHwRecords

###-------------------
###  Experiment tables
###-------------------

class ExperimentType(HasReagentTypes, HasDataFileSources, HasMetaDataSources, Base):
    """this stores all the constant data about an experiment that will be done many times"""
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(String(30),nullable=False)
    abbrev=Column(String)
    methods_id=Column(Integer,ForeignKey('citeable.id'))

    experiments=relationship('Experiment',backref=backref('type',uselist=False))

    @property
    def reagents(self):
        return [rt.currentLot for rt in self.reagenttypes] #FIXME


    def __init__(self,name=None,abbrev=None,methods_id=None,ReagentTypes=[],MetaDataSources=[]):
        self.name=name
        self.abbrev=abbrev
        if methods_id is not None:
            self.methods_id=int(methods_id)

        self.reagenttypes.extend(ReagentTypes)
        self.metadatasources.extend(MetaDataSources)

    def __repr__(self):
        return super().__repr__()


class Experiment(HasMetaData, HasReagents, HasMdsHwRecords, HasDfsHwRecords, Base):
    __tablename__='experiments'
    id=Column(Integer,primary_key=True)
    type_id=Column(Integer,ForeignKey('experimenttype.id'),nullable=False)

    #FIXME do these go here?
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False)

    startDateTime=Column(DateTime,default=datetime.now())
    endDateTime=Column(DateTime)

    @validates('type_id','person_id','endDateTime','startDateTime')
    def _wo(self, key, value): return self._write_once(key, value)

    def setEndDateTime(self,dateTime=None):
        if not self.endDateTime: #FIXME I should be able to do this with validates
            if not dateTime:
                self.endDateTime=datetime.now()
            else:
                self.endDateTime=dateTime
        else:
            raise Warning('endDateTime has already been set!')

    def __init__(self,type_id=None,project_id=None,person_id=None,Reagents=[],Subjects=[],startDateTime=None,endDateTime=None):
        self.type_id=int(type_id)
        if project_id: #FIXME move to experiment type? if exptype is hierarchical can duplicate...
            self.project_id=int(project_id)
        if person_id:
            self.person_id=int(person_id)

        self.startDateTime=startDateTime
        self.endDateTime=endDateTime

        self.reagents.extend(Reagents)
        self.subjects.extend(Subjects)

