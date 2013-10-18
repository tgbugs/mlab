from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData
from database.standards import URL_STAND

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

###-------------
###  DataSources
###-------------

class DataSource():
    __tablename__='datasources'
    #it may be the case that we don't need this table
    #the mapping between MDS_ and DFS_ to these does not have to be 1:1
    #but it would be nice if this reflected that symmetry...
    #FIXME this is related to the problem with sub experiments and making those protocols doccumentable along with the .pro files or the like, they ammount to the same thing... but they don't need to be experiments in the same right because everything at the higher level is constant wrt them... and doccumented there at the higher level

class DataFileStructure():
    external_def_url=Column(String,ForeignKey('File.url'),primary_key=True)
    external_def_filename=Column(String,ForeignKey('File.filename'),primary_key=True)
    external_def_hash=None #TODO check to make sure that it hasn't changed since init, do a check if it has
    #hashing needs to be compatible with the need to modify values of certain files for rheobase etc without changing their structure
    channels=relationship('DataFileSource') #TODO this will be... many to many?
    num_chans=Column(Integer)


class MetaDataSource_Experiment_Assoc(): #shouldn't this be bound to whatever has the MetaData???
    experiment_id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)
    metadatasource_id=Column(Integer,ForeignKey('metadatasources.id'),primary_key=True)
    hardware_id=Column(Integer,ForeignKey('hardware.id'))
    relationship('Experiment',primaryjoin='Experiment.id==MetaDataSource_Experiment_Assoc.experiment_id')
    @validates('hardware_id') #basically if shit breaks half way through, new experiment
    def _wo(self, key, value): return self._write_once(key, value)
    

class DataFileSource_Experiment_Assoc(): #FIXME shouldn't this be bound to datafile
    experiment_id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)
    datafilesource=Column(Integer,ForeignKey('datafilesources.id'))
    hardware_id=Column(Integer,ForeignKey('hardware.id'))
    relationship('Experiment',primaryjoin='Experiment.id==MetaDataSource_Experiment_Assoc.experiment_id',
                backref='datafilesources')
    @validates('hardware_id') #basically if shit breaks half way through, new experiment
    def _wo(self, key, value): return self._write_once(key, value)




class NDArrayDataSource(): #fixme we'll worry about what imaging looks like later
    pass


class ArrayDataSource(): #FIXME this doesn't quite fit the problem I need to solve with binding channels to hardware to subjects
    #somehow these have starttimes instead of date times, because they are collected for a long time after and in fact may be collected at a time OTHER than when the record of them is made...
    __tablename__='arraydatasources'
    id=Column(Integer,primary_key=True)
    name=Column(String(20),nullable=False,unique=True)
    prefix=Column(String(2),ForeignKey('si_prefix.symbol')) #nullable can accomadate external datafiles
    unit=Column(String(3),ForeignKey('si_unit.symbol'))


class MetaDataSource(Base): #FIXME ScalarDataSource #may be combined into a VectorDataSource
    #FIXME TODO this can just be called 'DataSource' because it can reference array or scalar data
    #wheter I want a flag for marking scalar or array is another question, also the segments/as from neo...
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
    url=Column(String,ForeignKey('repository.url'),primary_key=True,autoincrement=False)
    mirrors=relationship('Repository',primaryjoin='foreign(Repository.parent_url)==File.url') #FIXME not causal!
    filename=Column(String,primary_key=True,autoincrement=False)
    creationDateTime=Column(DateTime,default=datetime.now)

    @property
    def filetype(self):
        return self.filename.split('.')[-1]
    @property
    def full_url(self):
        return self.url+self.filename
    ident=Column(String) #FIXME wtf was I going to do with this?
    __mapper_args__ = {
        'polymorphic_on':ident,
        'polymorphic_identity':'file',
    }

    def checkExists(self):
        URL_STAND.ping(self.full_url)

    def __init__(self,filename,url=None,creationDateTime=None):
        self.url=URL_STAND.urlClean(str(url)) #Repository.__str__ returns the url, so can just pass in repo :)
        self.filename=filename
        #if Repo:
            #if Repo.url:
                #self.url=Repo.url
                #TODO if it doesn't exist we should create it, thus the need for the updated urlClean
            #else:
                #raise AttributeError('RepoPath has no url! Did you commit before referencing the instance directly?')
        if not creationDateTime:
            URL_STAND.getCreationDateTime(self.full_url)
        else:
            self.creationDateTime=creationDateTime

    def strHelper(self,depth=0):
        return super().strHelper(depth,'filename')

    def __repr__(self):
        return '\n%s%s'%(self.url,self.filename)


#FIXME TODO DataFile is currently a standin for a 'protocol' which is what we really want so that data can flexibly be stored inside or outside the program this will be the "unit of data"?? the "segment" or set of segments... basically the neoio thing that is generated from a single protocol file and may in point of fact have different metadata for each sub segment, but that at least has it in a consistent and preictable way
class SubExperiment(): #FIXME
    datathing_id=None #the unit of data collection over which nothing recorded directly in the database varies
    #so a single image file in some cases, or a time serries of image files in another

#FIXME something is a bit off with HDFS


class SoftwareChannel(Base):
    """Closely related to MetaDataSource"""
    datafilesource_id=Column(Integer,ForeignKey,primary_key=True) #FIXME may need to generalize for nidaq?
    channel_id=Column(String(20),primary_key=True) #could be useful for out too...
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False) #muteable!
    #FIXME CRITICAL MUST implement something similar to the record keeping for MDS
    #because the hardware/swc association can and will change
    #the persistence for the Subject needs to come from the history table that gets recorded on a per experiment basis, this would allow a subject to have a single hardware_id and resolve the convlict of having to figure out which piece of hardware to use for analysis if for example, 2 different extracellular probes were used on the same animal on different days and inserted into the opposite locations


class DataFileSource(Base): #TODO stop and think about how this generalizes to other experiments, specifically imaging
    """Basic structure of a datafile based on the piece of software that writes it"""
    __tablename__='datafilesources'
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(String(20),nullable=False,unique=True)

    @declared_attr
    def channels(cls):
        cls.SoftwareChannels=SoftwareChannels
        return relationship(cls.SoftwareChannel)

    def strHelper(self,depth=0):
        #return '%s%s'%(self.prefix,self.unit)
        return super().strHelper(depth,'name')
    def __repr__(self):
        return '\n%s'%(self.name)


class DataFile(File): #TODO datafiles can only really belong to a single experiment, while subjects can belong to MANY experiments....
    __tablename__='datafile'
    url=Column(String,primary_key=True,autoincrement=False)
    filename=Column(String,primary_key=True,autoincrement=False)
    __table_args__=(ForeignKeyConstraint([url,filename],['file.url','file.filename']), {})
    datafilesource_id=Column(Integer,ForeignKey('datafiletype.id'),nullable=False)
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False)
    datafilesource=relationship('DataFileSource',uselist=False) #backref=backref('datafiles'),
    #FIXME datasources: they are equivalent to MDSes and can be channels!
    __mapper_args__={'polymorphic_identity':'datafile'}

    experiment=relationship('Experiment',backref='datafiles',uselist=False)

    @declared_attr #FIXME
    def __datafilesources(cls): #FIXME not sure this is what I want... the structure of the df should have it
        datafilesource_association = Table('datafile_dfs_assoc', cls.metadata,
            Column('datafilesource_id',ForeignKey('datafilesources.id'),primary_key=True),
            Column('datafile_url', String, primary_key=True),
            Column('datafile_filename', String, primary_key=True),
            ForeignKeyConstraint(['datafile_url','datafile_filename'],['datafile.url','datafile.filename'])
        )
        return relationship('DataFileSource',secondary=datafilesource_association,
            primaryjoin='and_({0}_dfs_assoc.c.{0}_url=={0}.c.url,{0}_dfs_assoc.c.{0}_filename=={0}.c.filename)'.format('datafile'),
            secondaryjoin='DataFileSource.id=={0}_dfs_assoc.c.datafilesource_id'.format('datafile'),
            backref=backref('datafile') #FIXME do we really want this?
        )


    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData=DataFileMetaData
        return relationship(cls.MetaData)

    def __init__(self,filename,url,datafilesource_id,experiment_id=None,Subjects=[], creationDateTime=None):
        super().__init__(Repo,filename,url,creationDateTime)
        self.datafilesource_id=datafilesource_id
        datafilesource_id=int(datafilesource_id)
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

