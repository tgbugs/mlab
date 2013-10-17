from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes
class _Result(HasNotes, Base):
    __tablename__='results'
    id=Column(Integer,primary_key=True)
    datasource_id=None
    analysis_id=None
    output_id=None

class OnlineAnalysis(Base):
    id=Column(Integer,primary_key=True)
    #TODO these should probably be mixins!???! or something per cell type halp!
    #should probably look like metadata tables
    pass

class OfflineAnalysis(Base):
    id=Column(Integer,primary_key=True)
    pass


