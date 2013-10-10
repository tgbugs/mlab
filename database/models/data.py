from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData
from database.standards import URL_STAND

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

###-------------
###  DataSources
###-------------

#datasource examples:
#espX, espY
#NBQX_washin_start, concentration #by associating the data source with a reagent instead of a person... the data is there for both the acsf_id and all the drug information :), #FIXME unfortunately that leads to a massive proliferation of datasources :/, so we need to find a better way >_< since this is more along the lines of 'protocol metadata'

class DataSource(Base): #TODO FIXME this should be DATFILESource
    """used for doccumenting where data (NOT metadata) came form, even if I generated it, this makes a distinction between data that I have complete control over and data that I get from another source such as clampex or jax"""
    #this also works for citeables
    __tablename__='datasources'
    id=Column(Integer,primary_key=True)
    name=Column(String(20),nullable=False)
    #TODO
    def strHelper(self,depth=0):
        #return '%s%s'%(self.prefix,self.unit)
        return super().strHelper(depth,'name')
    def __repr__(self):
        return '\n%s'%(self.name)


class MetaDataSource(Base):
    """used for doccumenting how data was COLLECTED not where it came from, may need to fix naming"""
    __tablename__='metadatasources'
    id=Column(Integer,primary_key=True)
    name=Column(String(20),nullable=False,unique=True)
    prefix=Column(String(2),ForeignKey('si_prefix.symbol'),default='')
    unit=Column(String(3),ForeignKey('si_unit.symbol'),nullable=False)
    mantissa=Column(Integer) #TODO
    #TODO calibration data should *probably* be stored on the hardware as a datafile or metadata and can be filtered by datetime against experiments
    def strHelper(self): #TODO this is where quantities can really pay off
        return '%s%s from %s'%(self.prefix,self.unit,self.name)
    def __repr__(self):
        return '\n%s units %s%s'%(self.name,self.prefix,self.unit)

###-----------------------------------------------
###  MetaData tables (for stuff stored internally)
###-----------------------------------------------

#all the rest of the metadata tables are in mixins
#for consistency all metadata tables should reside
#in the namespace of their parent table
#Thus DataFileMetaData is not exported via *


class DataFileMetaData(Base):
    __tablename__='datafiles_metadata'
    id=Column(Integer,primary_key=True)
    url=Column(String,nullable=False)
    filename=Column(String,nullable=False) #FIXME you know, using datafile.id would let it change naming w/o cascade...
    __table_args__=(ForeignKeyConstraint([url,filename],['datafile.url','datafile.filename']), {})
    metadatasource_id=Column(Integer,ForeignKey('metadatasources.id'),nullable=False) #TODO how to get this?
    dateTime=Column(DateTime,default=datetime.now)
    value=Column(Float(53),nullable=False)
    abs_error=Column(Float(53)) #TODO
    metadatasource=relationship('MetaDataSource')
    _write_once_cols='url','filename','metadatasource_id','dateTime','value','abs_error'
    def __init__(self,value,DataFile=None,MetaDataSource=None,abs_error=None,dateTime=None,metadatasource_id=None,url=None,filename=None):
        self.dateTime=dateTime
        self.url=url
        self.filename=filename
        self.metadatasource_id=metadatasource_id
        self.value=value
        self.abs_error=abs_error
        if DataFile:
            if DataFile.url:
                self.url=DataFile.url
                self.filename=DataFile.filename
            else:
                raise AttributeError
        self.AssignID(MetaDataSource)
    def __repr__(self):
        sigfigs=''
        error=''
        if self.sigfigs: sigfigs=self.sigfigs
        if self.abs_error != None: error='%s %s'%(_plusMinus,self.abs_error)
        return '%s %s %s %s %s'%(self.dateTime,self.value,self.datasource.strHelper(),sigfigs,error)

###-----------------------------------------------------------------------
###  DataFiles and repositories for data stored externally (ie filesystem)
###-----------------------------------------------------------------------

class Repository(Base):
    #TODO urllib parse, these will go elsewhere in the actual analysis code or something
    #TODO request.urlopen works perfectly for filesystem stuff
    #file:///C: #apparently chromium uses file:///C:
    #file:///D: are technically the base
    url=Column(String,primary_key=True) #use urllib.parse for this #since these are base URLS len 100 ok
    credentials_id=Column(Integer,ForeignKey('credentials.id')) 
    name=Column(String)
    blurb=Column(Text)
    assoc_program=Column(String(30)) #FIXME some of these should be automatically updated and check by the programs etc
    parent_url=Column(String,ForeignKey('repository.url')) #use urllib.parse for this #since these are base URLS len 100 ok
    mirrors=relationship('Repository',primaryjoin='Repository.parent_url==Repository.url')

    def getStatus(self):
        URL_STAND.ping(self.url)

    def validateFiles(self): #FIXME does this go here??! not really...
        return None

    #TODO, if we are going to store these in a database then the db needs to pass sec tests, but it is probably better than trying to secure them in a separate file, BUT we will unify all our secure credentials management with the same system
    #TODO there should be a default folder or 
    #access_manager=Column(String) #FIXME the credentials manager will handle this all by itself
    def __init__(self,url,credentials_id=None,name=None,assoc_program=None,parent_url=None):
        self.url=URL_STAND.urlClean(url)
        self.credentials_id=credentials_id
        self.assoc_program=assoc_program
        self.name=name
        URL_STAND.ping(self.url)
        self.parent_url=parent_url
    def __repr__(self):
        return super().__repr__('url')


class File(Base):
    """class for interfacing with things stored outside the database, whether datafiles or citables or whatever"""
    #TODO references to a local file should be replaced with a reference to that computer so that on retrieval if the current computer does not match we can go find other repositories for the same file damn it this is going to be a bit complicated
    #ideally the failover version selection should be ordered by retrieval time and should be completely transparent
    #this does mean that files need to have m-m with repositories
    #TODO need verfication that the file is actually AT the repository
    #fuck, what order do I do this in esp for my backup code
    __tablename__='file'
    url=Column(String,ForeignKey('repository.url'),primary_key=True,autoincrement=False)
    mirrors=relationship('Repository',primaryjoin='Repository.parent_url==File.url') #FIXME not causal!
    filename=Column(String,primary_key=True,autoincrement=False)
    creationDateTime=Column(DateTime,default=datetime.now)

    @property
    def filetype(self):
        return self.filename.split('.')[-1]
    ident=Column(String) #FIXME wtf was I going to do with this?
    __mapper_args__ = {
        'polymorphic_on':ident,
        'polymorphic_identity':'file',
    }

    def checkExists(self):
        pass

    def __init__(self,Repo=None,filename=None,url=None,creationDateTime=None):
        self.url=URL_STAND.urlClean(url)
        self.filename=filename
        self.creationDateTime=creationDateTime
        if Repo:
            if Repo.url:
                self.url=Repo.url
                #TODO if it doesn't exist we should create it, thus the need for the updated urlClean
            else:
                raise AttributeError('RepoPath has no url! Did you commit before referencing the instance directly?')

    def strHelper(self,depth=0):
        return super().strHelper(depth,'filename')

    def __repr__(self):
        return '\n%s%s'%(self.url,self.filename)


class DataFile(File): #TODO datafiles can only really belong to a single experiment, while subjects can belong to MANY experiments....
    __tablename__='datafile'
    url=Column(String,primary_key=True,autoincrement=False)
    filename=Column(String,primary_key=True,autoincrement=False)
    __table_args__=(ForeignKeyConstraint([url,filename],['file.url','file.filename']), {})
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False)
    datasource_id=Column(Integer,ForeignKey('datasources.id'),nullable=False)
    __mapper_args__={'polymorphic_identity':'datafile'}

    experiment=relationship('Experiment',backref='datafiles',uselist=False)

    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData=DataFileMetaData
        return relationship(cls.MetaData)

    def __init__(self,Repo=None,filename=None,Experiment=None,DataSource=None,url=None,experiment_id=None,datasource_id=None,Subjects=[], creationDateTime=None):
        super().__init__(Repo,filename,url,creationDateTime)
        self.datasource_id=datasource_id
        self.AssignID(DataSource)
        self.AssignID(Experiment)
        self.subjects.extend(Subjects) #TODO in the interface.py make it so that current subjects 'auto' fill?


class InDatabaseData(Base):
    id=Column(Integer, primary_key=True)
    #TODO, need something more flexible than metadata (amazingly) that can hold stuff like calibration data not stored elsewhere?? also if I ever transition away from external datafiles or if I want to use neoio immediately to convert abf files
    pass

## DataFile notes vvvvv

    #FIXME TODO if the server is not local then file:/// only has meaning for the computer that the data was originally stored on and that has to match :/
    #TODO google docs access does not go here because those could be writeable too
    #these should point to more or less static things outside the program, every revision should add a new datafile for consistency, store the diffs?
    #how to constrain/track files so they don't get lost??
    #well, it is pretty simple you force the user to add them, this prevents all kinds of problems down the road
    #and the constraint will be populated by the DataPath table, if I have 10,000 datafiles though, that could become a NASTY change
    #ideally we want this to be dynamic so that the DataPath can change and all the DataFile entries will learn about it
    #it might just be better to do it by hand so UPDATE doesn't swamp everything
    #TODO next problem: when do we actually CREATE the DataFile and how to we get the number right even if we discard the trial? well, we DONT discard the file, we just keep it, but we need to gracefully deal with deletions/renumbering so that if something goes wrong it will alert to user
    #RESPONSE: this record cannot be created until the file itself exists
    #FIXME datafiles have substructure that requires more than one datasource ;_;
    #although, the easiest way to fix that is to just change this to allow for an arbitrary number of channels to be saved per datafile and link the datasources to those?
    #maybe base it on datafile type??? or configuration... but that is going to change for every fucking thing...
    #that stuff goes in the metadata, datasource here just means 'collection software' fucking conflation

