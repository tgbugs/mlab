from database.imports import *
from database.models.base import Base

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

###--------------
###  notes mixins
###--------------

class HasNotes: #FIXME this works ok, will allow the addition of the same note to anything basically
    @declared_attr
    def notes(cls):
        note_association = Table('%s_note_assoc'%cls.__tablename__, cls.metadata,
            Column('note_id',ForeignKey('notes.id'),primary_key=True),
            Column('%s_id'%cls.__tablename__,ForeignKey('%s.id'%cls.__tablename__), #FIXME .id may not be all?
                   primary_key=True)
        )
        return relationship('Note',secondary=note_association,
            primaryjoin='{0}_note_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='Note.id=={0}_note_assoc.c.note_id'.format(cls.__tablename__),
            backref=backref('parent_%s'%cls.__tablename__) #FIXME do we really want this?
        )

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


class IsMetaDataSource: #XXX I think this is depricated... ?
    #users, citeables, hardware, NO PEOPLE
    @declared_attr
    def datastreams(cls):
        datasource_association = Table('%s_metadatastreams'%cls.__tablename__, cls.metadata,
            Column('metadatasource_id', ForeignKey('metadatasources.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('MetaDataSource', secondary=datasource_association,backref=backref('%s_source'%cls.__tablename__)) #FIXME these should all be able to append to source!??! check the examples


class HasDataFileSources:
    @declared_attr
    def datafilesources(cls):
        datafilesource_association = Table('%s_dfs_assoc'%cls.__tablename__, cls.metadata,
            Column('datafilesource_id',ForeignKey('datafilesources.id'),primary_key=True),
            Column('%s_id'%cls.__tablename__,ForeignKey('%s.id'%cls.__tablename__), #FIXME .id may not be all?
                   primary_key=True)
        )
        return relationship('DataFileSource',secondary=datafilesource_association,
            primaryjoin='{0}_dfs_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='DataFileSource.id=={0}_dfs_assoc.c.datafilesource_id'.format(cls.__tablename__),
            backref=backref('%s'%cls.__tablename__) #FIXME do we really want this?
        )


class HasMetaDataSources:
    @declared_attr
    def metadatasources(cls):
        metadatasource_association = Table('%s_mds_assoc'%cls.__tablename__, cls.metadata,
            Column('metadatasource_id',ForeignKey('metadatasources.id'),primary_key=True),
            Column('%s_id'%cls.__tablename__,ForeignKey('%s.id'%cls.__tablename__), #FIXME .id may not be all?
                   primary_key=True)
        )
        return relationship('MetaDataSource',secondary=metadatasource_association,
            primaryjoin='{0}_mds_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='MetaDataSource.id=={0}_mds_assoc.c.metadatasource_id'.format(cls.__tablename__),
            backref=backref('%s'%cls.__tablename__) #FIXME do we really want this?
        )


class MetaData: #the way to these is via ParentClass.MetaData which I guess makes sense?
    dateTime=Column(DateTime,default=datetime.now)
    value=Column(Float(53),nullable=False)
    abs_error=Column(Float(53))
    @validates('parent_id','metadatasource_id','dateTime','value','abs_error')
    def _wo(self, key, value): return self._write_once(key, value)

    def __init__(self,value,Parent=None,MetaDataSource=None,metadatasource_id=None,abs_error=None,dateTime=None):
        self.dateTime=dateTime
        self.metadatasource_id=metadatasource_id
        self.value=value
        self.abs_error=abs_error
        self.AssignID(MetaDataSource)
        if Parent: #FIXME standardize table naming and id references ftlog
            if Parent.id:
                #setattr(self,'%s_id'%Parent.__tablename__,Parent.id)
                self.parent_id=Parent.id
            else:
                raise AttributeError
            
    def __int__(self):
        return int(self.value) #FIXME TODO think about this

    def __repr__(self):
        mantissa=''
        error=''
        if self.metadatasource.mantissa: mantissa='mantissa: %s'%self.metadatasource.mantissa
        if self.abs_error != None: error='%s %s'%(_plusMinus,self.abs_error)
        return '\n%s %s %s %s %s %s'%(self.parent_id,self.dateTime,self.value,self.metadatasource.strHelper(),mantissa,error) #TODO this is where quantities really pays off


class HasMetaData: #FIXME based on how I'm using this right now, the relationship should probably return a dictionary collection indexed by metadatasource_id and ordered by datetime???
    #I intentionally do not allow explicit groupings of metadata into higher dimensions, I don't think we will need that, but getting the alignment right for multiple multidimensional measurements will be a problem FIXME
    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData = type(
                '%sMetaData'%cls.__name__,
                (MetaData, Base,),
                {   '__tablename__':'%s_metadata'%cls.__tablename__,
                    'id':Column(Integer,primary_key=True),
                    'parent_id':Column(Integer, #FIXME nasty errors inbound
                        ForeignKey('%s.id'%cls.__tablename__),nullable=False),
                    'metadatasource_id':Column(Integer,
                        ForeignKey('metadatasources.id'),nullable=False),
                    'metadatasource':relationship('MetaDataSource'), #keep it one way
                    #'hardware_id':Column(Integer, #FIXME I *could* put this here but it seems like overkill?
                        #ForeignKey('hardware.id'),nullable=False), #since w/in experiment it wont change?
                 #conflict between desire for doccumentation and need for linkage when recording data
                 #this is the easiest solution but leads to massive data duplication
                }
        )
        return relationship(cls.MetaData) #FIXME may need a primaryjoin on this


class DFS_HW_BIND:
    #how to use to associate a cell to a channel:
    #the cell or subcompartment will have a hardware_id
    #join that hardware_id against the DFS_MW_BIND and then the datafile structure when unpacked must match
    #I should come up with a way to verify the match, even if it is very simple
    @validates('hardware_id') #basically if shit breaks half way through, new experiment
    def _wo(self, key, value): return self._write_once(key, value)
    def __init__(self,Parent=None,DataFileSource=None,Hardware=None,parent_id=None,datafilesource_id=None,hardware_id=None):
        self.parent_id=parent_id
        self.datafilesource_id=datafilesource_id
        self.hardware_id=hardware_id #FIXME probably need hardware=relationship()
        self.AssignID(DataFileSource)
        self.AssignID(Hardware)
        if Parent:
            if Parent.id:
                self.parent_id=Parent.id
            else:
                raise AttributeError



class HasDfsHwRecords: #we bind DFSes to hardware that collects that datafile property
    @declared_attr
    def dfs_hw_records(cls):
        cls.DfsHwRecord = type(
                '%s_DfsHwRecord'%cls.__name__,
                (DFS_HW_BIND, Base,),
                {   '__tablename__':'%s_dfshwrecord'%cls.__tablename__,
                    'parent_id':Column(Integer,
                        ForeignKey('%s.id'%cls.__tablename__),primary_key=True),
                    'datafilesource_id':Column(Integer,
                        ForeignKey('datafilesources.id'),primary_key=True),
                    'hardware_id':Column(Integer,
                        ForeignKey('hardware.id'))
                }
        )
        return relationship(cls.DfsHwRecord)


class MDS_HW_BIND:
    """Class that keeps a record of what hardware was used to record the metadata"""
    @validates('hardware_id') #basically if shit breaks half way through, new experiment
    def _wo(self, key, value): return self._write_once(key, value)
    def __init__(self,Parent=None,MetaDataSource=None,Hardware=None,parent_id=None,metadatasource_id=None,hardware_id=None):
        self.parent_id=parent_id
        self.metadatasource_id=metadatasource_id
        self.hardware_id=hardware_id #FIXME probably need hardware=relationship()
        self.AssignID(MetaDataSource)
        self.AssignID(Hardware)
        if Parent:
            if Parent.id:
                self.parent_id=Parent.id
            else:
                raise AttributeError


class HasMdsHwRecords: #use for experiments since subjects change too fast
    @declared_attr
    def mds_hw_records(cls):
        cls.MdsHwRecord = type(
                '%s_MdsHwRecord'%cls.__name__,
                (MDS_HW_BIND, Base,),
                {   '__tablename__':'%s_mdshwrecord'%cls.__tablename__,
                    'parent_id':Column(Integer,
                        ForeignKey('%s.id'%cls.__tablename__),primary_key=True),
                    'metadatasource_id':Column(Integer,
                        ForeignKey('metadatasources.id'),primary_key=True),
                    'hardware_id':Column(Integer,
                        ForeignKey('hardware.id'))
                }
        )
        return relationship(cls.MdsHwRecord)


class HasDataFiles:
    @declared_attr
    def datafiles(cls):
        datafile_association = Table('%s_df_assoc'%cls.__tablename__, cls.metadata,
            Column('datafile_url',String,primary_key=True),
            Column('datafile_filename',String,primary_key=True),
            ForeignKeyConstraint(['datafile_url','datafile_filename'],
                                 ['datafile.url','datafile.filename']),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__),
                   primary_key=True),
        )
        return relationship('DataFile', secondary=datafile_association,
            primaryjoin='{0}_df_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='and_(DataFile.url=={0}.datafile_url,DataFile.filename=={0}.datafile_filename)'.format(cls.__tablename__+'_df_assoc.c'),
            backref=backref('%s'%cls.__tablename__),
        )


class HasFiles:
    @declared_attr
    def files(cls):
        file_association = Table('%s_f_assoc'%cls.__tablename__, cls.metadata,
            Column('file_url',String,primary_key=True),
            Column('file_filename',String,primary_key=True),
            ForeignKeyConstraint(['file_url','file_filename'],
                                 ['file.url','file.filename']),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__),
                   primary_key=True),
        )
        return relationship('File', secondary=file_association,
            primaryjoin='{0}_f_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='and_(File.url=={0}.file_url,File.filename=={0}.file_filename)'.format(cls.__tablename__+'_f_assoc.c'),
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

###--------------
###  Has reagents
###--------------

class HasReagentTypes:
    @declared_attr
    def reagenttypes(cls):
        reagenttype_association = Table('%s_reagenttypes'%cls.__tablename__,cls.metadata,
            Column('reagenttype_id', ForeignKey('reagenttypes.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('ReagentType', secondary=reagenttype_association,backref=backref('%s_used'%cls.__tablename__))


class HasReagents:
    @declared_attr
    def reagents(cls):
        reagent_association = Table('%s_reagents'%cls.__tablename__,cls.metadata,
            Column('reagent_type_id', Integer, primary_key=True),
            Column('reagent_lot', Integer, primary_key=True), #FIXME
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True),
            ForeignKeyConstraint(['reagent_type_id','reagent_lot'],['reagents.type_id','reagents.lotNumber']))
        return relationship('Reagent', secondary=reagent_association,backref=backref('%s_used'%cls.__tablename__))

###--------------
###  Has hardware
###--------------

class HasHardware:
    @declared_attr
    def hardware(cls):
        hardware_association = Table('%s_hardware'%cls.__tablename__,cls.metadata,
            Column('hardware_id', ForeignKey('hardware.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('Hardware', secondary=hardware_association,backref=backref('%s_used'%cls.__tablename__))

###--------------
###  Has subjects
###--------------

class HasSubjects:
    @declared_attr
    def subjects(cls):
        subjects_association = Table('%s_subjects'%cls.__tablename__,cls.metadata,
            Column('subjects_id', ForeignKey('subjects.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('Subject', secondary=subjects_association,backref=backref('%s'%cls.__tablename__))
