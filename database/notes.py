from imports import *
from sqlalchemy                         import Text
from sqlalchemy.ext.declarative         import declared_attr
from sqlalchemy.ext.associationproxy    import association_proxy

from dateTimeFuncs import *

from database.main import Base
#all I want is a many-many relationship between targets and notes but that doesn't quite work ;_; Association per tble maybe?? that way we don't need a mixin

class NoteAssociation(Base): #turns out we want joined table inheritance... #I think I need multiple tables for this...
    __tablename__='note_association'
    id=Column(Integer, primary_key=True)
    discriminator=Column(String) #there should now be a single row per discrminator

    @classmethod
    def creator(cls, discriminator):
        return lambda notes:NoteAssociation(notes=notes,discriminator=discriminator)
    #parents backref from HasNotes but we don't have... any... HasNotes_id to link these things..., may need a primary join
    #FIXME this needs to become 'table per' for the association part I think :/ check the examples


class Note(Base):
    __tablename__='notes'
    association_id=Column(Integer,ForeignKey('note_association.id'))
    source_id=Column(Integer,ForeignKey('datasources.id'))
    text=Column(Text,nullable=False)
    dateTime=Column(DateTime,nullable=False) #FIXME get rid of this and replace it with the transaction logs make things really simple
    #lbRefs=Column(Integer,ForeignKey('labbook.id') #FIXME

    association=relationship('NoteAssociation',backref='notes')
    parents=association_proxy('association','parents')

    def __init__(self,text):
        self.text=text
        self.dateTime=datetime.utcnow() #enforce datetime consistency!
    def __repr__(self):
        return '\n%s %s %s\n%s\n\t"%s"'% (self.__class__.__name__, ''.join([a.discriminator for a in self.association]), ''.join([p.id for p in self.parents]), frmtDT(self.dateTime), self.text) #FIXME


class HasNotes(object): #FIXME
    @declared_attr
    def note_association_id(cls):
        pass
        #return Column(Integer,ForeignKey('note_association.id'))
        #return cls.__table__.c.get('note_association_id',Column(Integer, ForeignKey('note_association.id')))
    @declared_attr
    def note_association(cls):
        pass
        #discriminator=cls.__name__.lower()
        #cls.notes=association_proxy('note_association','notes',creator=NoteAssociation.creator(discriminator)) #i think the problem is with the creator..
        #return relationship('NoteAssociation',backref=backref('parents'))
    def addNote(string): #FIXME?
        pass


Base.metadata.create_all(engine)
