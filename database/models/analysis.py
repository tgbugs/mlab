from database.imports import *
from database.base import Base
from database.mixins import HasNotes
class _Result(HasNotes, Base):
    __tablename__='results'
    datasource_id=None
    analysis_id=None
    output_id=None



