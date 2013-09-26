from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasDataFiles
from database.standards import frmtDT
from sqlalchemy.orm import mapper

#an attempt to simplify the the relationship of objects to data

#HAHA so it turns out you can just put all subjects in one table and it will all work out, you just add a 'type' column, and the interitance from parent to child just needs to verify that a certain row matches the type for that relationship, seems like a mess though
'''
class Subject(HasMetaData, HasDataFiles, Base):
    id=Column(Integer,primary_key=True)
    type=Column(String) #mouse rat cell etc.
    production_record_id=None #matingrecord/sliceprep
    unit_of_production=None #litter/slice


'''
