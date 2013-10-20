from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData
from database.standards import URL_STAND

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

class Protocol:
    pass


###-------------
###  DataSources
###-------------

class MetaDataSource(Base): #FIXME naming
    """used for doccumenting how data was COLLECTED not where it came from, may need to fix naming"""
    __tablename__='metadatasources'
    id=Column(Integer,primary_key=True)
    name=Column(String(20),nullable=False,unique=True)
    prefix=Column(String(2),ForeignKey('si_prefix.symbol'),default='')
    unit=Column(String(3),ForeignKey('si_unit.symbol'),nullable=False)
    mantissa=Column(Integer) #TODO
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False) #this shall be muteable
    @validates('name','prefix','unit') #FIXME
    def _wo(self, key, value): return self._write_once(key, value)
    def strHelper(self): #TODO this is where quantities can really pay off
        return '%s%s from %s'%(self.prefix,self.unit,self.name)
    def __repr__(self):
        return '\n%s units %s%s'%(self.name,self.prefix,self.unit)
    def __init__(self,name=None,prefix=None,unit=None,mantissa=None,hardware_id=None):
        self.name=name
        self.prefix=prefix
        self.unit=unit
        self.mantissa=mantissa
        self.hardware_id=int(hardware_id)


class SoftwareChannel(Base):
    """Closely related to MetaDataSource"""
    datafilesource_id=Column(Integer,ForeignKey('datafilesources.id'),primary_key=True) #FIXME generalize for nidaq?
    channel_id=Column(String(20),primary_key=True) #handles input and output?
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False) #muteable!
    def __int__(self):
        return self.datafilesource_id
    def __str__(self):
        return self.channel_id


class DataFileSource(Base): #TODO think about how generalizing to other experiments, specifically imaging
    """Basic structure of a datafile based on the piece of software that writes it"""
    __tablename__='datafilesources'
    id=Column(Integer,primary_key=True) #FIXME switch over to name for pk?
    name=Column(String(20),nullable=False,unique=True) #FIXME these could get really fucking complicated...
    extension=Column(String(32),nullable=False) #FIXME technically unlimited but WTF m8

    @declared_attr
    def channels(cls):
        cls.SoftwareChannel=SoftwareChannel
        return relationship(cls.SoftwareChannel)

    def strHelper(self,depth=0):
        return super().strHelper(depth,'name')
    def __repr__(self):
        return '\n%s'%(self.name)

###-----------------------------------------------
###  MetaData tables (for stuff stored internally)
###-----------------------------------------------

#all the rest of the metadata tables are in mixins
#for consistency all metadata tables should reside
#in the namespace of their parent table
#Thus DataFileMetaData is not exported via *


class DataFileMetaData(Base): #FIXME naming
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

    @validates('url','filename','metadatasource_id','dateTime','value','abs_error')
    def _wo(self, key, value): return self._write_once(key, value)

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
    url=Column(String,primary_key=True)
    credentials_id=Column(Integer,ForeignKey('credentials.id')) 
    name=Column(String)
    blurb=Column(Text)
    parent_url=Column(String,ForeignKey('repository.url'))
    mirrors=relationship('Repository',primaryjoin='Repository.parent_url==Repository.url')

    def getStatus(self):
        URL_STAND.ping(self.url)

    def validateFiles(self): #FIXME does this go here??! not really...
        return None

    def __init__(self,url=None,credentials_id=None,name=None,assoc_program=None,parent_url=None):
        self.url=URL_STAND.urlClean(url)
        self.credentials_id=credentials_id
        self.assoc_program=assoc_program
        self.name=name
        URL_STAND.ping(self.url)
        self.parent_url=parent_url

    def __str__(self):
        return self.url

    def __repr__(self):
        return super().__repr__('url')


class File(Base): #REALLY GOOD NEWS: in windows terminal drag and drop produces filename! :D
    """class for interfacing with things stored outside the database, whether datafiles or citables or whatever"""
    #TODO references to a local file should be replaced with a reference to that computer so that on retrieval if the current computer does not match we can go find other repositories for the same file damn it this is going to be a bit complicated
    #ideally the failover version selection should be ordered by retrieval time and should be completely transparent
    #this does mean that files need to have m-m with repositories
    #TODO need verfication that the file is actually AT the repository
    #fuck, what order do I do this in esp for my backup code
    __tablename__='file'
    url=Column(String,ForeignKey('repository.url'),primary_key=True)
    mirrors=relationship('Repository',primaryjoin='foreign(Repository.parent_url)==File.url') #FIXME not causal!
    filename=Column(String,primary_key=True)
    creationDateTime=Column(DateTime,default=datetime.now)
    @property
    def filetype(self):
        return self.filename.split('.')[-1]
    @property
    def full_url(self):
        return self.url+self.filename
    __mapper_args__ = {
        'polymorphic_on':ident,
        'polymorphic_identity':'file',
    }

    def checkExists(self): #TODO
        URL_STAND.ping(self.full_url)

    def __init__(self,filename,url=None,creationDateTime=None):
        self.url=URL_STAND.urlClean(str(url))
        self.filename=filename

        if not creationDateTime: #FIXME implementation not complete
            URL_STAND.getCreationDateTime(self.full_url)
        else:
            self.creationDateTime=creationDateTime

    def strHelper(self,depth=0):
        return super().strHelper(depth,'filename')

    def __repr__(self):
        return '\n%s%s'%(self.url,self.filename)


class DataFile(File): #data should be collected in the scope of an experiment
    __tablename__='datafile'
    url=Column(String,primary_key=True,autoincrement=False)
    filename=Column(String,primary_key=True,autoincrement=False)
    __table_args__=(ForeignKeyConstraint([url,filename],['file.url','file.filename']), {})
    datafilesource_id=Column(Integer,ForeignKey('datafilesources.id'),nullable=False)
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False)
    datafilesource=relationship('DataFileSource',uselist=False) #backref=backref('datafiles'),
    __mapper_args__={'polymorphic_identity':'datafile'}

    experiment=relationship('Experiment',backref='datafiles',uselist=False)

    @validates('_filename')#TODO verify that datafile isnt being fed garbage filenames by accident!
    def _fileextension_matchs_dfs(self, key, value): #FIXME... aint loaded...
        dfe=self.datafilesource.extension
        assert filename[-3:]==dfe, 'file extension does not match %s'%dfe
        return value

    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData=DataFileMetaData
        return relationship(cls.MetaData)

    def __init__(self,filename,url,datafilesource_id,experiment_id=None,Subjects=[], creationDateTime=None):
        super().__init__(filename,url,creationDateTime)
        datafilesource_id=int(datafilesource_id)
        if experiment_id is not None:
            self.experiment_id=experiment_id
        self.subjects.extend(Subjects) #TODO in the interface.py make it so that current subjects 'auto' fill?


class InDatabaseData(Base): #TODO
    id=Column(Integer, primary_key=True)

