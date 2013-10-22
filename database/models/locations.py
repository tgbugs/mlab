from database.imports import *
from database.models.base import Base

class Location(Base):
    __tablename__='locations'
    id=Column(Integer,primary_key=True) #FIXME consider a natural primary key...
    type_id=None #TODO
    name=Column(String,nullable=False)
    parent_id=Column(Integer,ForeignKey('locations.id')) #why the fuck don't I know a word for 'super location'?
    sublocations=relationship('Location',primaryjoin='Location.id==Location.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))

class SubjectLocationChange(Base):
    id=Column(Integer,primary_key=True)
    dateTime=Column(DateTime, default=datetime.now)
    user_id=None
    action=None
    subject_id=Column(Integer, ForeignKey('subjects.id'))
    old_location_id=Column(Integer, ForeignKey('locations.id'))
    new_location_id=Column(Integer, ForeignKey('locations.id'))
