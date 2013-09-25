from database.imports import *
from database.standards import frmtDT

#from database.base import Base
Base=object
#all I want is a many-many relationship between targets and notes but that doesn't quite work ;_; Association per tble maybe?? that way we don't need a mixin

class NoteAssociation(Base): #turns out we want joined table inheritance... #I think I need multiple tables for this...
    __tablename__='note_association'
    id=Column(Integer, primary_key=True)
    discriminator=Column(String(30)) #there should now be a single row per discrminator

    @classmethod
    def creator(cls, discriminator):
        return lambda notes:NoteAssociation(notes=notes,discriminator=discriminator)
    #parents backref from HasNotes but we don't have... any... HasNotes_id to link these things..., may need a primary join
    #FIXME this needs to become 'table per' for the association part I think :/ check the examples
    #__table_args__['extend_existing']=True
    __table_args__ = {'extend_existing':True}


class Note(Base):
    __tablename__='notes'
    id=Column(Integer,primary_key=True)
    association_id=Column(Integer,ForeignKey('note_association.id'))
    source_id=Column(Integer,ForeignKey('datasources.id'))
    text=Column(Text,nullable=False)
    dateTime=Column(DateTime,nullable=False) #FIXME get rid of this and replace it with the transaction logs make things really simple
    #lbRefs=Column(Integer,ForeignKey('labbook.id') #FIXME

    association=relationship('NoteAssociation',backref='notes')
    parents=association_proxy('association','parents')
    __table_args__ = {'extend_existing':True}
    #__table_args__['extend_existing']=True

    def __init__(self,text):
        self.text=text
        self.dateTime=datetime.utcnow() #enforce datetime consistency!
    def __repr__(self):
        return '\n%s %s %s\n%s\n\t"%s"'% (self.__class__.__name__, ''.join([a.discriminator for a in self.association]), ''.join([p.id for p in self.parents]), frmtDT(self.dateTime), self.text) #FIXME




