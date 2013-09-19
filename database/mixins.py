from database.imports import *
from database.models import MetaData

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


class HasMetaData: #looks like we want this to be table per related
    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData = type(
                '%sMetaData'%cls.__name__,
                (MetaData),
                {   '__tablename__':'%s_metadata'%cls.__tablename__,
                    'id':None,
                    '%s_id'%'parent' : Column(Integer, #fuck :(
                        ForeignKey('%s.id'%cls.__tablename__),
                        primary_key=True,autoincrement=False)
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

