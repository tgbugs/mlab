from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData
from database.standards import URL_STAND

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

class Protocol:
    pass

###----------------------------------
### The data interface for all things
###----------------------------------

class DataInterface: #TODO this should be a gateway for in database and database data that DOESNT persist
    """common interface for all data that get's passed on to analysis""" #FIXME move to analysis?
    #def __init__(self,source=None,scalar=None,array=None,prefix=None,unit=None,prefixunit=None,mantissa=None,hardware_id=None):
    def __init__(self,source=None,value=None,prefix=None,unit=None,prefixunit=None,mantissa=None,hardware_id=None):
        #TODO TODO if we just think of everything as a timeserries of scalars then imaging is a type of
            #time serries that has a particular structure imposed on the channels
            #the relationship between channels should be generalizeable
            #ideally based on either the experimental context and/or the spatial relation
            #the relationship between channels largely has to do with which objects we are trying to
            #associate them with and the corelated noise between them
            #for example ICA will naievely assign signals to sources
            #spatial structure is also important for electrode arrays and tetrodes, but only the _relative_
            #position AKA the indexing of the channels as long as that is consistent at each time step
            #then we're good to go

            #we tend to exploit our ability to hold change in our head to view multiple channels over time
            #specifically for data that has spatial structure

            #magnification, um/pixel stuff like that... are all that metadata...
            
            #How to preserve the spatial structure of the data...

        self.source=source #TODO this should be the original object that the thing came from
        #zero order tensor #how nearly everything is actually measured (2photon w/ scanning laser even)

        #criteria for higher order tensors
        #1) different hardware ID requried for tensors, the order of the fields must be by hardware/datasource id
        #TODO tuples will have to be blobbed for sqlite :/
        #TODO do we save the scalar source with all it's associated stuff, or do we doccument 
        #it is easier to stick stuff together at the point of collection, the question is how to doccument it and how to store it in a database without proliferating tables or having empty columns
        #ALTERNATELY, I could do this at analysis time and group by datasource with specific order and just allow for unordered collections of metadata that can be ordered at a later time during analysis
        #2) OR 

        #criteria for timeseries
        #1) same hardware with sample rate

        #criteria for sequence
        #1) same hardware with timestamp (FIXME vitally this may require clock synchronization or a record kept with the same clock as any data we wish to compare it with, eg voltage driving the led)

        #criteria for timeserries of tensors that may not have multiple hardware ids (imaging)
        #1) simultaneous collection, or a sample rate for a full collection of indexed data

        #criteria for tensors of timeserris (multiple voltage channles)
        #1) simultaneous or interleaved collection in time of each channel

        #making ten-time and time-ten interchangeable
        #they are the exact same thing, just the data representation is switched
        #FIXME the difference is that they are often subject to different kinds of correlated noise
        #they must have a sample rate or some way of tracking the time of each sample (covers sequential)

        #criteria for sequential data with timestamps THAT SHALL NOT BE CALLED DATA BUT RESULTS

        #the 'matrix' of the imaging data reflects the spatial arrangment of data collected SIMULTANEOUSLY (more or less) and thus meets the criteria for a 'vectorized' format, in this case a matrix or an order 2-tensor
        #the VALUES of that tensor have a dynamic range that may need to be dealt with :/

        #TODO practical considerations for making analysis easier VS tracking where numbers actually come from
    



###-------------
###  DataSources
###-------------

class DataIO(Base):
    __tablename__='dataio'
    id=Column(Integer,primary_key=True)
    type=Column(String)
    ctrl_name=Column(String) #FIXME should these actually save the code or just the name?
    getter_name=Column(String)
    writer_name=Column(String) #should be somethinking like Experiment.MetaData or the like
    collection_name=Column(String)
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'baseio',
    }

class Getter(DataIO):
    ctrl_name=Column(String)
    function_name=Column(String)
    kwargs={} 
class Setter(DataIO):
    ctrl_name=Column(String)
    function_name=Column(String)
    kwargs={}
class Reader(DataIO):
    pass
class Writer(DataIO):
    pass
class Analyzer(DataIO):
    pass
class Checker(DataIO):
    pass

class DataSetter(DataIO):
    __tablename__='datasetter'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    setter_name=Column(String) #only on certain subclasses?
    __mapper_args__ = {'polymorphic_identity':'dset'}


class MetaDataSource(DataIO): #FIXME naming #all raw data collect w/o sample rate goes here
    """used for doccumenting how data was COLLECTED not where it came from, may need to fix naming"""
    __tablename__='metadatasources'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    name=Column(String(20),nullable=False,unique=True)
    prefix=Column(String(2),ForeignKey('si_prefix.symbol'),default='')
    unit=Column(String(3),ForeignKey('si_unit.symbol'),nullable=False)
    mantissa=Column(Integer) #TODO
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False) #this shall be muteable
    prefix_data=relationship('SI_PREFIX',uselist=False) #FIXME don't do this myself, use pint/quanitites
    unit_data=relationship('SI_UNIT',uselist=False) #FIXME don't do this myself, use pint/quanitites
    __mapper_args__ = {'polymorphic_identity':'mds'}
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


###-----------------------------------------------------------
###  external data... somehow different in terms of process...
###-----------------------------------------------------------

class SoftwareChannel(DataIO):
    """Closely related to MetaDataSource"""
    __tablename__='softwarechannel'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    datafilesource_id=Column(Integer,ForeignKey('datafilesources.id'),nullable=False) #FIXME gnralize for nidaq?
    channel_id=Column(String(20),nullable=False) #handles input and output?
    __table_args__=(UniqueConstraint(datafilesource_id,channel_id),{})
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False) #muteable!
    __mapper_args__ = {'polymorphic_identity':'swc'}
    def __int__(self):
        return self.datafilesource_id
    def __str__(self):
        return self.channel_id


class DataFileSource(DataIO): #TODO think about how generalizing to other experiments, specifically imaging
    """Basic structure of a datafile based on the piece of software that writes it"""
    __tablename__='datafilesources'
    #id=Column(Integer,primary_key=True) #FIXME switch over to name for pk?
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    name=Column(String(20),nullable=False,unique=True) #FIXME these could get really fucking complicated...
    extension=Column(String(32),nullable=False) #FIXME technically unlimited but WTF m8
    __mapper_args__ = {'polymorphic_identity':'dfs'}

    @declared_attr
    def channels(cls):
        cls.SoftwareChannel=SoftwareChannel
        return relationship(cls.SoftwareChannel,foreign_keys=SoftwareChannel.datafilesource_id)

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

    def __init__(self,value,metadatasource_id=None,abs_error=None,dateTime=None,DataFile=None,url=None,filename=None):
        #FIXME I think sqlalchemy is smart enough to add the metadata to the file without explicitly telling it
        self.url=url
        self.filename=filename
        self.metadatasource_id=int(metadatasource_id)
        self.value=value
        self.abs_error=abs_error
        self.dateTime=dateTime
        if DataFile:
            if DataFile.url:
                self.url=DataFile.url
                self.filename=DataFile.filename
            else:
                raise AttributeError
    def __repr__(self):
        mantissa=''
        error=''
        if self.metadatasource.mantissa: mantissa='mantissa: %s'%self.metadatasource.mantissa
        if self.abs_error != None: error='%s %s'%(_plusMinus,self.abs_error)
        return '\n%s%s %s %s %s %s %s'%(self.url,self.filename,self.dateTime,self.value,self.metadatasource.strHelper(),mantissa,error) #TODO quantities/pint

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
        URL_STAND.ping(self.url) #FIXME TODO probably need to check that we have write privs? esp if we want to save data collected using this system to track it eg for backups and stuff
        self.parent_url=parent_url

    def __str__(self):
        return self.url

    def __repr__(self):
        return super().__repr__('url')
    def strHelper(self,depth=0):
        return super().strHelper(depth=depth,attr='url')



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
    ident=Column(String) #used for inheritance
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
        #URL_STAND.ping(self.full_url)
        print('TURN ME BACK ON YOU IDIOT')

    def __init__(self,filename=None,url=None,creationDateTime=None): #args could be useful... for conveying nullable=False or primary_key...
        self.url=URL_STAND.urlClean(str(url))
        self.filename=filename
        #self.checkExists() #XXX come up with a better way to test fake file paths
            

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
    datafilesource=relationship('DataFileSource',uselist=False) #backref=backref('datafiles'),
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False)
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

    def __init__(self,filename=None,url=None,datafilesource_id=None,experiment_id=None,Subjects=(),creationDateTime=None): #FIXME kwargs vs args? kwargs should exist internally for the purposes of doccumentation, args should be used in the interface for when I don't want to type something over and over
        super().__init__(filename,url,creationDateTime)
        self.datafilesource_id=int(datafilesource_id)
        #if experiment_id is not None:
        self.experiment_id=int(experiment_id) #enforcing the idea that datafiles must have experiments
        self.subjects.extend(Subjects) #TODO in the interface.py make it so that current subjects 'auto' fill?


class InDatabaseData(Base): #TODO
    id=Column(Integer, primary_key=True)
