from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes
from database.models import DataIO
class Result(Base):
    __tablename__='results'
    id=Column(Integer,primary_key=True)
    datasource_id=None
    inputs=None #TODO how do we chracterize the 'getter' for this... there must be a better way!
    analysis_id=None
    output=None #whatever the output(s) and whatever the format number table, graph etc


class AnalysisRecord(): #XXX pretty sure I don't need this, simply too many possible analyses... maybe at some point I'll be able to abstract inputs so that they can be directly linked to data, but since lots of the access for analysis is going to depend on a HUGE number of variables and perspectives that task seems daunting at the moment
    analysis_id=Column(Integer,ForeignKey('analysis.id'),primary_key=True)
    result_id=Column(Integer,ForeignKey('results.id'),primary_key=True)
    steprecords=None #??? halp!? list of the steps that generated the values?
    #at the moment steprecord doesnt keep track of the value! it keeps track of the writeTarget...
    #that is silly >_<


class Analysis(DataIO): #primarily for data which also has times associated
    __tablename__='analysis'
    #this should be a dataio right???!!! yeah I think it fits properly because it is going to go get numbers from somewhere else according to some specification and the requirements will be handled by the step
    #TODO it would be nice if Step could automatically figure out what analysis needed since analysis is a bit different from a simple datasource in that it has MULTIPLE datasources :/
        #TODO deal with steps that have multiple datasources specifically Analysis steps
        #or check for a match between the two??
        #forcing the user to write the same thing twice sucks
    #FIXME analysis shouldn't need a getter? or are there simply too many possible relations that we are better off treating queries as getters and just doccumenting which values we actually retrieved thereafter?
    id=Column(Integer,primary_key=True)
    dataios=relationship('DataIO') #TODO THIS is useful because it gives some basic idea of where stuff came from, the 'AnalysisRecord' will be a bit more complicated
    version=Column(Integer,nullable=False)
    code=Column(Text) #halp wat
    analysis_function=None
    __mapper_args__ = {'polymorphic_identity':'analysis'}



class OnlineAnalysis():
    id=Column(Integer,primary_key=True)
    #TODO these should probably be mixins!???! or something per cell type halp!
    #should probably look like metadata tables


class OfflineAnalysis():
    id=Column(Integer,primary_key=True)
    pass


class DateTimeAnalysis(): #do we need this, if analysis steps depend on other steps completeling successfully we can just get ANY data/sideeffects from those steps
    id=Column(Integer,primary_key=True)
    #also can be used for
    #things related to performance and evaluating success rates
    #basically science science
    #identifying steps with high failure rates etc
    #places for optimization

