from database.imports import *
from database.base import Base
from database.mixins import HasNotes
class _Result(HasNotes, Base):
    __tablename__='results'
    datasource_id=None
    analysis_id=None
    output_id=None

class OnlineAnalysis(Base):
    #TODO these should probably be mixins!???! or something per cell type halp!
    #should probably look like metadata tables
    pass

class OfflineAnalysis(Base):
    pass



