from database.models import MetaDataSource, Experiment, Subject
#TODO what I need is a link between datasources and the Controller classes, that should probably be defined... here? or somewhere? or fuck what damn it one class per metadata source???!

class MDSource:
    def __init__(self,Controller,MetaDataSource):
        self.ctrl=Controller
        self.sourceID=None #TODO use versioning track changes in pairings between sources and hardware
        #self.currentStateGetter
        self.MetaDataSource=MetaDataSource #bind to the source in the database TODO check correct pairing via sid
    def record(self,MetaDataTarget):
        value=self.getCurrentValue()
        sigfigs=self.getSigFigs()
        abs_error=self.getAbsError()
        Parent=None #FIXME
        MetaDataTarget(value,Parent,self.MetaDataSource,sigfigs=sigfigs,abs_error=abs_error)
        #TODO how to commit??!
    def getCurrentValue(self):
        return None
    def getSigFigs(self):
        return None
    def getAbsError(self):
        return None


class espX(MDSource):
    def getCurrentValue(self):
        return None
    def getSigFigs(self):
        return None
    def getAbsError(self):
        #TODO this is where online analysis based on calibration should go??? well we also need that somewhere else too...
        return None
