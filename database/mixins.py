from database.imports import *
from database.base import Base

###--------------
###  notes mixins
###--------------

class HasNotes: #FIXME
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

###-------------
###  data mixins
###-------------

class IsDataSource:
    #users, citeables, hardware, NO PEOPLE
    @declared_attr
    def datastreams(cls):
        datasource_association = Table('%s_datastreams'%cls.__tablename__, cls.metadata,
            Column('datasource_id', ForeignKey('datasources.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('DataSource', secondary=datasource_association,backref=backref('%s_source'%cls.__tablename__)) #FIXME these should all be able to append to source!??! check the examples


class MetaData: #damnit I want this in data, oh well
    dateTime=Column(DateTime,nullable=False)
    value=Column(Float(53),nullable=False)
    sigfigs=Column(Integer)
    abs_error=Column(Float(53))
    def __init__(self,Parent=None,DataSource=None,parent_id=None,datasource_id=None,value=None,sigfigs=None,abs_error=None):
        self.parent_id=parent_id
        self.datasource_id=datasource_id
        self.dateTime=datetime.utcnow() #FIXME this logs when the md was entered
        self.value=value
        self.sigfigs=sigfigs
        self.abs_error=abs_error
        self.AssignID(Parent)
        self.AssignID(DataSource)
    def repr(self):
        return '%s %s %s %s %s %s'%(self.parent_id,self.dateTime,self.value,self.datasource,self.sigfigs,self.abs_error)


class HasMetaData: #looks like we want this to be table per related
    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData = type(
                '%sMetaData'%cls.__name__,
                (MetaData, Base,),
                {   '__tablename__':'%s_metadata'%cls.__tablename__,
                    'id':None,
                    '%s_id'%'parent' : Column(Integer, #fuck :(
                        ForeignKey('%s.id'%cls.__tablename__),
                        primary_key=True,autoincrement=False),
                    'datasource_id':Column(Integer,
                        ForeignKey('datasources.id'),
                        primary_key=True,autoincrement=False),
                    'datasource':relationship('DataSource',
                        backref=backref('%s_metadata'%cls.__tablename__))
                }
        )
        return relationship(cls.MetaData) #FIXME may need a primaryjoin on this


        
###--------------------
###  experiments mixins
###--------------------

class IsTerminal:
    #TODO mixin for terminal experiments to automatically log data of death for a mouse
    #@declared_attr
    def dod(cls):
        return  None

