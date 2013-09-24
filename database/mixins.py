from database.imports import *
from database.base import Base

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

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


class MetaData: #the way to these is via ParentClass.MetaData which I guess makes sense?
    dateTime=Column(DateTime,default=datetime.now)
    value=Column(Float(53),nullable=False)
    sigfigs=Column(Integer) #TODO
    abs_error=Column(Float(53)) #TODO
    def __init__(self,value,Parent=None,DataSource=None,datasource_id=None,sigfigs=None,abs_error=None,dateTime=None):
        self.dateTime=dateTime
        self.datasource_id=datasource_id
        self.value=value
        self.sigfigs=sigfigs
        self.abs_error=abs_error
        self.AssignID(Parent) #FIXME
        self.AssignID(DataSource)
    def __repr__(self):
        sigfigs=''
        error=''
        if self.sigfigs: sigfigs=self.sigfigs
        if self.abs_error != None: error='%s %s'%(_plusMinus,self.abs_error)
        return '\n%s %s %s %s %s'%(self.dateTime,self.value,self.datasource.strHelper(),sigfigs,error)


class HasMetaData: #looks like we want this to be table per related
    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData = type(
                '%sMetaData'%cls.__name__,
                (MetaData, Base,),
                {   '__tablename__':'%s_metadata'%cls.__tablename__,
                    'id':Column(Integer,primary_key=True),
                    '%s_id'%cls.__tablename__:Column(Integer, #FIXME nasty errors inbound
                        ForeignKey('%s.id'%cls.__tablename__)),
                    'datasource_id':Column(Integer,
                        ForeignKey('datasources.id')),
                    'datasource':relationship('DataSource'), #keep it one way
                }
        )
        return relationship(cls.MetaData) #FIXME may need a primaryjoin on this

        
class HasDataFiles:
    @declared_attr
    def datafiles(cls):
        datafile_association = Table('%s_df_assoc'%cls.__tablename__, cls.metadata,
            Column('datafile_url',String,primary_key=True),
            Column('datafile_path',String,primary_key=True),
            Column('datafile_filename',String,primary_key=True),
            ForeignKeyConstraint(['datafile_url','datafile_path','datafile_filename'],
                                 ['datafile.url','datafile.path','datafile.filename']),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__),
                   primary_key=True),
        )
        return relationship('DataFile', secondary=datafile_association,
            primaryjoin='{0}_df_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='and_(DataFile.url=={0}.datafile_url,DataFile.path=={0}.datafile_path,DataFile.filename=={0}.datafile_filename)'.format(cls.__tablename__+'_df_assoc.c'),
            backref=backref('%s'%cls.__tablename__),
        )

###--------------------
###  experiments mixins
###--------------------

class IsTerminal:
    #TODO mixin for terminal experiments to automatically log data of death for a mouse
    #@declared_attr
    def dod(cls):
        return  None


###-------------
###  Credentials??!?!
###-------------

class HasCredentials:
    #TODO I might be able to use a mixin to do logins, but this seems unlikely to work safely
    pass

###---------------
###  Has citeables
###---------------

class HasCiteables:
    @declared_attr
    def citeables(cls):
        cite_association = Table('%s_citeables'%cls.__tablename__,cls.metadata,
            Column('citeable_id', ForeignKey('citeable.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('Citeable', secondary=cite_association,backref=backref('%s_citer'%cls.__tablename__))
