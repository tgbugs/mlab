from database.imports import *
from database.models.base import Base

class Location(Base): #FIXME probably want this to be a HasLocation mixin...?
    __tablename__='locations'
    id=Column(Integer,primary_key=True) #FIXME consider a natural primary key...
    type_id=None #TODO
    name=Column(String,nullable=False)
    #dont think it is an issue to have rows first and then columns, could go either way
    #the nice thing is that I only have to add the locations I use instead of all of them at the same time
    #a bit different than if I were actually managing a mouse colony, but more flexible
    parent_id=Column(Integer,ForeignKey('locations.id')) #why the fuck don't I know a word for 'super location'?
    sublocations=relationship('Location',primaryjoin='Location.id==Location.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))
    #for cages, just row, column cagecard name
    subjects=relationship('Subject',primaryjoin='Subject.location_id==Location.id',backref=backref('location',uselist=False))

class SubjectLocationChange(Base):
    id=Column(Integer,primary_key=True)
    dateTime=Column(DateTime, default=datetime.now)
    user_id=None
    action=None
    subject_id=Column(Integer, ForeignKey('subjects.id'))
    old_location_id=Column(Integer, ForeignKey('locations.id'))
    new_location_id=Column(Integer, ForeignKey('locations.id'))
