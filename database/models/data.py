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

class DataSource(Base): #TODO
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
    name=Column(String(20),nullable=False)
    prefix=Column(String(2),ForeignKey('si_prefix.symbol'),nullable=False)
    unit=Column(String(3),ForeignKey('si_unit.symbol'),nullable=False)
    ds_calibration_rec=Column(Integer,ForeignKey('calibrationdata.id')) #FIXME TODO just need a way to match the last calibration to the metadata... shouldn't be too hard
    def strHelper(self):
        return '%s%s'%(self.prefix,self.unit)
    def __repr__(self):
        return '\n%s units %s%s'%(self.name,self.prefix,self.unit)

###-----------------------------------------------
###  MetaData tables (for stuff stored internally)
###-----------------------------------------------

class CalibrationData(Base):
    id=Column(Integer, primary_key=True)
    #TODO base class for storing calibration data
    #examples:
    #voltage response curve for LED
    #esp grid calibration for esp300
    #FIXME there should be a way to join these to experiments directly
    #maybe with primaryjoin='and_(CalibrationData.datasource_id==MetaData.datasource_id,CalibrationData.dateTime < MetaData.dateTime, BUT only the most recent one of those...)' with a viewonly
    pass


###-----------------------------------------------------------------------
###  DataFiles and repositories for data stored externally (ie filesystem)
###-----------------------------------------------------------------------

class Repository(Base):
    #TODO urllib parse, these will go elsewhere in the actual analysis code or something
    #TODO request.urlopen works perfectly for filesystem stuff
    #file:///C: #apparently chromium uses file:///C:
    #file:///D: are technically the base
    url=Column(String(100),primary_key=True) #use urllib.parse for this #since these are base URLS len 100 ok
    credentials_id=Column(Integer,ForeignKey('credentials.id')) 
    blurb=Column(Text)
    paths=relationship('RepoPath',primaryjoin='RepoPath.url==Repository.url')
    #FIXME, move this to people/users because this is part of credentialing not data? move it to wherever I end up putting 'credential things' like users
    #TODO, if we are going to store these in a database then the db needs to pass sec tests, but it is probably better than trying to secure them in a separate file, BUT we will unify all our secure credentials management with the same system
    #TODO there should be a default folder or 
    #access_manager=Column(String) #FIXME the credentials manager will handle this all by itself
    def __init__(self,url,credentials_id=None):
        self.url=URL_STAND.baseClean(url)
        self.credentials_id=credentials_id
    def __repr__(self):
        return super().__repr__('url')


class RepoPath(Base): #FIXME this may be missing trailing /on path :x
    __tablename__='repopaths'
    #Assumption: repository MUST be the full path to the data, so yes, a single 'repository' might have 10 entries, but that single repository is just a NAME and has not functional purpose for storing/retrieving data
    #id=Column(Integer,primary_key=True,autoincrement=True) #to simplify passing repos? is this reasonable?
    name=Column(String)
    url=Column(String,ForeignKey('repository.url'),primary_key=True)
    path=Column(String,primary_key=True) #make this explicitly relative path?
    assoc_program=Column(String(30)) #FIXME some of these should be automatically updated and check by the programs etc
    verified=Column(Boolean,default=False) #TODO populated when the repopath has been verified to exist, should probably also check at startup for existence (will not check for datafiles)
    fullpath=Column(String)
    @hybrid_property
    def fullpath(self):
        return self.url+self.path
    relationship('DataFile',primaryjoin='DataFile.repopath_id==RepoPath.id',backref='repopath') #FIXME datafiles can be kept in multiple repos... #FIXME can you append to relationships?! test this
    #TODO how do we keep track of data duplication and backups!?!?!?
    blurb=Column(Text) #a little note saying what data is stored here, eg, abf files
    #TODO we MUST maintain synchrony between where external programs put files and where the database THINKS they put files, some programs may be able to have this specified on file creation, check the clxapi for example, note has to be done by hand for that one
    #FIXME should the REPO HERE maintain a list of files? the filesystem KNOWS what is there
    def __init__(self,Repo=None,path=None,url=None,assoc_program=None,name=None):
        self.url=URL_STAND.baseClean(url)
        self.assoc_program=assoc_program
        self.name=name
        if Repo:
            if Repo.url:
                self.url=Repo.url
            else:
                raise AttributeError('Repository has no url! Did you commit before referencing the instance directly?') #FIXME this should never trigger because url is a primary key and not an autoincrementing int...
        clean_path=URL_STAND.pathClean(path)
        #test to make sure the directory exists
        URL_STAND.test_url(self.url+clean_path) #FIXME may need a try in here
        self.path=clean_path
    def __repr__(self):
        return super().__repr__('fullpath')


class File(Base):
    """class for interfacing with things stored outside the database, whether datafiles or citables or whatever"""
    #TODO references to a local file should be replaced with a reference to that computer so that on retrieval if the current computer does not match we can go find other repositories for the same file damn it this is going to be a bit complicated
    #ideally the failover version selection should be ordered by retrieval time and should be completely transparent
    #this does mean that files need to have m-m with repositories
    #TODO need verfication that the file is actually AT the repository
    #fuck, what order do I do this in esp for my backup code
    __tablename__='file'
    url=Column(String,primary_key=True,autoincrement=False)
    path=Column(String,primary_key=True,autoincrement=False)
    __table_args__=(ForeignKeyConstraint([url,path],['repopaths.url','repopaths.path']), {}) #FIXME this *could* be really fucking slow because they arent indexed, may need to revert these changes, ah well
    filename=Column(String,primary_key=True,autoincrement=False)
    creationDateTime=Column(DateTime,default=datetime.now)
    filetype=Column(String)
    @hybrid_property #FIXME this isn't really hybrid... ie it doesnt really need to be a column
    def filetype(self):
        return self.filename.split('.')[-1]
    @filetype.setter
    def filetype(self):
        raise AttributeError('readonly attribute, there should be a file name associate with this record?')
    ident=Column(String)
    __mapper_args__ = {
        'polymorphic_on':ident,
        'polymorphic_identity':'file',
    }
    def __init__(self,RepoPath=None,filename=None,url=None,path=None,creationDateTime=None):
        self.url=URL_STAND.baseClean(url)
        self.repo_path=URL_STAND.pathClean(path) #TODO use requests
        self.filename=filename
        self.creationDateTime=creationDateTime
        if RepoPath:
            if RepoPath.url:
                self.url=RepoPath.url
                self.path=RepoPath.path
            else:
                raise AttributeError('RepoPath has no url/path! Did you commit before referencing the instance directly?')
    def strHelper(self,depth=0):
        return super().strHelper(depth,'filename')
    def __repr__(self):
        return '\n%s%s%s%s'%(self.url,self.path,'/',self.filename)


class DataFile(File):
    __tablename__='datafile'
    url=Column(String,primary_key=True,autoincrement=False)
    path=Column(String,primary_key=True,autoincrement=False)
    filename=Column(String,primary_key=True,autoincrement=False)
    __table_args__=(ForeignKeyConstraint([url,path,filename],['file.url','file.path','file.filename']), {})
    datasource_id=Column(Integer,ForeignKey('datasources.id'),nullable=False) #FIXME make this many-many???!
    __mapper_args__={'polymorphic_identity':'datafile'}

    @declared_attr
    def metadata_(cls): #FIXME naming...
        class DataFileMetaData(Base):
            __tablename__='datafiles_metadata'
            id=Column(Integer,primary_key=True)
            url=Column(String,nullable=False)
            path=Column(String,nullable=False)
            filename=Column(String,nullable=False)
            __table_args__=(ForeignKeyConstraint([url,path,filename],['datafile.url','datafile.path','datafile.filename']), {})
            metadatasource_id=Column(Integer,ForeignKey('metadatasources.id'),nullable=False)
            dateTime=Column(DateTime,default=datetime.now)
            value=Column(Float(53),nullable=False)
            sigfigs=Column(Integer) #TODO
            abs_error=Column(Float(53)) #TODO
            metadatasource=relationship('MetaDataSource')
            def __init__(self,value,DataFile=None,MetaDataSource=None,metadatasource_id=None,url=None,path=None,filename=None,sigfigs=None,abs_error=None,dateTime=None):
                self.dateTime=dateTime
                self.url=url
                self.path=path
                self.filename=filename
                self.metadatasource_id=metadatasource_id
                self.value=value
                self.sigfigs=sigfigs
                self.abs_error=abs_error
                if DataFile:
                    if DataFile.url:
                        self.url=DataFile.url
                        self.path=DataFile.path
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

        cls.MetaData=DataFileMetaData
        return relationship(cls.MetaData)

    def __init__(self,RepoPath=None,filename=None,DataSource=None,url=None,path=None,datasource_id=None,Subjects=[], creationDateTime=None):
        super().__init__(RepoPath,filename,url,path,creationDateTime)
        self.datasource_id=datasource_id
        self.AssignID(DataSource)
        self.subjects.extend(Subjects)


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
    #the path cannot be the primary key of the datapath table AND accomodate path changes
    #TODO next problem: when do we actually CREATE the DataFile and how to we get the number right even if we discard the trial? well, we DONT discard the file, we just keep it, but we need to gracefully deal with deletions/renumbering so that if something goes wrong it will alert to user
    #RESPONSE: this record cannot be created until the file itself exists
    #repopath_id=Column(Integer,ForeignKey('repopaths.id'),primary_key=True,autoincrement=False) #FIXME this is what was causing errors previous commit, also decide if you want this or the both path and url
    #FIXME datafiles have substructure that requires more than one datasource ;_;
    #although, the easiest way to fix that is to just change this to allow for an arbitrary number of channels to be saved per datafile and link the datasources to those?
    #maybe base it on datafile type??? or configuration... but that is going to change for every fucking thing...
    #that stuff goes in the metadata, datasource here just means 'collection software' fucking conflation

