from sqlalchemy                     import Column
from sqlalchemy                     import Integer
from sqlalchemy.ext.declarative     import declarative_base, declared_attr

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

class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id=Column(Integer, primary_key=True)

    def strHelper(self,depth=0,attr='id'):
        tabs='\t'*depth
        return '\n%s%s %s'%(tabs,self.__class__.__name__,getattr(self,attr))
    def __repr__(self,attr='id'):
        return '\n%s %s'%(self.__class__.__name__,getattr(self,attr))

Base=declarative_base(cls=Base)

def init_db(engine):
    Base.metadata.create_all(engine, checkfirst=True)
    
