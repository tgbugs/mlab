import os, socket #FIXME do we really want to handle this here?
from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasProperties, HasMirrors, HasAnalysis
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
    name=Column(String,nullable=False,unique=True)
    docstring=Column(String,nullable=False) #pulled from __doc__ and repropagated probably should be a citeable?
    #ctrl_name=Column(String) #FIXME should these actually save the code or just the name?
    #getter_name=Column(String)
    #writer_name=Column(String) #should be somethinking like Experiment.MetaData or the like
    #collection_name=Column(String)
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'baseio',
    }

#TODO figure out the best way to manage these suckers in the database it is NOT how I am doing it right now
class Getter(DataIO): #TODO for all of these, may also want to diversify in case we dont need ALL THE THINGS?
    __tablename__='getters'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    ctrl_name=Column(String)
    function_name=Column(String)
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False)
    func_kwargs={}  #FIXME TODO
    __mapper_args__ = {'polymorphic_identity':'getter'}
    #def __init__(self,hardware_id=None,**kwargs):
        #self.hardware_id=int(hardware_id)
        #super().__init__(**kwargs)
class Setter(DataIO):
    __tablename__='setters'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    ctrl_name=Column(String)
    function_name=Column(String)
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False)
    func_kwargs={}
    __mapper_args__ = {'polymorphic_identity':'setter'}
    #def __init__(self,hardware_id=None,**kwargs):
        #self.hardware_id=int(hardware_id)
class Binder(DataIO):
    __tablename__='binders' #FIXME naming
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    __mapper_args__ = {'polymorphic_identity':'binder'}
class Reader(DataIO):
    __tablename__='readers'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    reader_name=Column(String,nullable=False) #FIXME should probably be reader type?
    __mapper_args__ = {'polymorphic_identity':'reader'}
class Writer(DataIO):
    __tablename__='writers'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    writer_name=Column(String,nullable=False) #FIXME should probably be reader type?
    writer_kwargs={} #FIXME hybrid type using with_variant for hstore and and pickle? can't query them direct...
    __mapper_args__ = {'polymorphic_identity':'writer'}
class Analyzer(DataIO):
    __tablename__='analyzers'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    __mapper_args__ = {'polymorphic_identity':'analyzer'}
class Checker(DataIO):
    __tablename__='checkers'
    id=Column(Integer,ForeignKey('dataio.id'),primary_key=True)
    __mapper_args__ = {'polymorphic_identity':'checker'}


class DataSetter(DataIO): #XXX depricated
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
    unit=Column(String(4),ForeignKey('si_unit.symbol'),nullable=False)
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
    def __init__(self,docstring=None,ctrl_name=None,function_name=None,func_kwargs=None,name=None,prefix=None,unit=None,mantissa=None,hardware_id=None):
        #TODO function_name and control name; aka fix the bloody underlying dataio structure in the database
        self.docstring=docstring #FIXME
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

class DataFileMetaData(Base): #XXX DEPRECATED
    __tablename__='datafiles_metadata'
    id=Column(Integer,primary_key=True)
    #url=Column(String,nullable=False)
    #filename=Column(String,nullable=False) #FIXME you know, using datafile.id would let it change naming w/o cascade...
    #__table_args__=(ForeignKeyConstraint([url,filename],['datafile.url','datafile.filename']), {}) #this wont work because a direct reference to datafile.url does not exist (CTI)
    datafile_id=Column(Integer,ForeignKey('datafile.id'),nullable=False) #TODO how to get this?
    metadatasource_id=Column(Integer,ForeignKey('metadatasources.id'),nullable=False) #TODO how to get this?
    dateTime=Column(DateTime,default=datetime.now)
    #value=Column(Float(53),nullable=False)
    #abs_error=Column(Float(53)) #TODO
    value=Column( Array(Float(53)) ,nullable=False) #TODO 
    abs_error=Column( Array(Float(53)) ) #TODO
    metadatasource=relationship('MetaDataSource')

    @validates('url','filename','metadatasource_id','dateTime','value','abs_error')
    def _wo(self, key, value): return self._write_once(key, value)

    def __init__(self,value,metadatasource_id=None,abs_error=None,dateTime=None,datafile_id=None,getter_id=None):
        raise DeprecationWarning
        #FIXME I think sqlalchemy is smart enough to add the metadata to the file without explicitly telling it
        #self.url=url
        #self.filename=filename
        try:
            self.metadatasource_id=int(metadatasource_id) #FIXME hack for now
        except:
            self.metadatasource_id=int(getter_id)
        self.value=value
        self.abs_error=abs_error
        self.dateTime=dateTime
        self.datafile_id
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

class Repository(HasMirrors, Base):
    id=Column(Integer,primary_key=True)
    url=Column(String,unique=True,nullable=False)
    hostname=Column(String)
    path=Column(String)
    credentials_id=Column(Integer,ForeignKey('credentials.id')) 
    name=Column(String)
    blurb=Column(Text)
    #parent_url=Column(String,ForeignKey('repository.url'))
    #mirrors=relationship('Repository',primaryjoin='Repository.==Repository.url') #TODO needs a self m-m
    #@property
    #def mirrors(self): #leverages off of selfmtm
        #return self.nodes

    def getStatus(self):
        URL_STAND.ping(self.url)

    def validateFiles(self): #FIXME does this go here??! not really...
        return None

    def __init__(self,url=None,credentials_id=None,name=None,assoc_program=None):
        self.url=URL_STAND.urlClean(url)
        self.hostname,self.path=URL_STAND.urlHostPath(self.url)
        URL_STAND.ping(self.url,is_file=False) #FIXME TODO probably need to check that we have write privs? esp if we want to save data collected using this system to track it eg for backups and stuff
        self.credentials_id=credentials_id
        self.assoc_program=assoc_program
        self.name=name

    def __str__(self):
        return self.url

    def __repr__(self):
        return super().__repr__('url')
    def strHelper(self,depth=0):
        return super().strHelper(depth=depth,attr='url')


class File(HasNotes, HasProperties, HasMetaData, Base, HasAnalysis): #REALLY GOOD NEWS: in windows terminal drag and drop produces filename! :D
    """class for interfacing with things stored outside the database, whether datafiles or citables or whatever"""
    #TODO references to a local file should be replaced with a reference to that computer so that on retrieval if the current computer does not match we can go find other repositories for the same file damn it this is going to be a bit complicated
    #ideally the failover version selection should be ordered by retrieval time and should be completely transparent
    #this does mean that files need to have m-m with repositories
    #TODO need verfication that the file is actually AT the repository
    #fuck, what order do I do this in esp for my backup code

    #TODO must hash all files on creation! use hashlib and stick the bastards in properties
    __tablename__='file'
    id=Column(Integer,primary_key=True)
    url=Column(String,ForeignKey('repository.url'),nullable=False)#this is the 'origin' url...#,primary_key=True) #TODO make it URLS??? maybe with hostnames?? single file multiple locations, that makes a damned lot of sense
    filename=Column(String,nullable=False)#,primary_key=True)
    __table_args__=(UniqueConstraint(url,filename), {}) #FIXME need a way to have multiple urls per filename that are ALL unique...
    #__table_args__=(UniqueConstraint(url,filename),{}) #TODO
    origin_repo=relationship('Repository',primaryjoin='foreign(Repository.url)==File.url',uselist=False,backref=backref('origin_files',uselist=True)) #this will hook in to the m-m group of repositories by a url to a single one of them
    #mirrors=relationship('Repository',primaryjoin='foreign(Repository.parent_url)==File.url') #FIXME not causal!
    @property
    def repositories(self):
        return self.origin_repo.mirrors #FIXME there is not a real link between the file and the repo going the other direction

    @property
    def local_repo(self):
        hostname=socket.gethostname() #FIXME posix vs... nt ;_;
        lrl=[r for r in self.repositories if r.hostname==hostname] #local repo list
        #print(lrl)
        if os.name == 'posix':
            lrl=[r for r in lrl if r.path[2] != ':'] #FIXME not the right way to discard windows paths >_<
        try:
            return lrl[0]
        except:
            return self.origin_repo #None #TODO I think this is correct, if there is no local repo we will handle that elsewhere
    @property
    def local_path(self):
        return self.local_repo.path+self.filename
            
    creationDateTime=Column(DateTime,default=datetime.now)
    ident=Column(String) #used for inheritance
    @property
    def filetype(self):
        return self.filename.split('.')[-1]
    @property
    def full_url(self):
        return self.url+self.filename #FIXME make this return the local repository for the file
    __mapper_args__ = {
        'polymorphic_on':ident,
        'polymorphic_identity':'file',
    }

    def checkExists(self): #TODO
        #URL_STAND.ping(self.full_url)
        printD('TURN ME BACK ON YOU IDIOT')

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

    def __eq__(self,other):
        a= type(other) == type(self)
        b= self.id == other.id
        return a and b

    def __gt__(self,other):
        return self.filename > other.filename
    def __lt__(self,other):
        return self.filename < other.filename

    def __neq__(self,other):
        a= type(other) != type(self)
        b= self.id != other.id
        return a or b

    def __hash__(self):
        return hash('%s%s'%(self.id,self.filename))

class DataFile(File): #data should be collected in the scope of an experiment
    __tablename__='datafile'
    id=Column(Integer,ForeignKey('file.id'),primary_key=True)
    #url=Column(String)#,primary_key=True,autoincrement=False)
    #filename=Column(String)#,primary_key=True,autoincrement=False)
    #__table_args__=(ForeignKeyConstraint([url,filename],['file.url','file.filename']), {})
    datafilesource_id=Column(Integer,ForeignKey('datafilesources.id'),nullable=False)
    datafilesource=relationship('DataFileSource',uselist=False) #backref=backref('datafiles'),
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False)

    mddictlist=Column( PickleType ) #FIXME nasty stopgap for storing the mcc state ;_;, not only that but it is a one off, can't append

    __mapper_args__={'polymorphic_identity':'datafile'}

    experiment=relationship('Experiment',backref='datafiles',uselist=False)

    #TODO protocol??? it would def be nice to filter by them...

    @property
    def position(self):
        try: 
            return [ d.value for d in self.metadata_ if d.metadatasource.name=='getPos' ][0] #FIXME getPos is a terrible way to name this >_< and not extensible
        except:
            return None

    @property
    def distances(self):
        if not self.position:
            return {}
        def norm(cell,file):
            a2=(cell[0]-file[0])**2
            b2=(cell[1]-file[1])**2
            return (a2+b2)**.5
        #dists=[]
        dists={} #FIXME return a dict with subject ids as keys?
        for subject in self.subjects:
            #if subject.type=='cell' #TODO?
            if not hasattr(subject,'position'):
                continue
            elif not subject.position:
                continue
            else:
                dists[subject.id]=norm(subject.position,self.position)
        return dists

    @validates('_filename')#TODO verify that datafile isnt being fed garbage filenames by accident!
    def _fileextension_matchs_dfs(self, key, value): #FIXME... aint loaded...
        dfe=self.datafilesource.extension
        assert filename[-3:]==dfe, 'file extension does not match %s'%dfe
        return value

    #@declared_attr #XXX deprecated
    #def metadata_(cls): #FIXME naming... 
        #cls.MetaData=DataFileMetaData
        #return relationship(cls.MetaData)

    def __init__(self,filename=None,url=None,datafilesource_id=None,experiment_id=None,Subjects=(),creationDateTime=None): #FIXME kwargs vs args? kwargs should exist internally for the purposes of doccumentation, args should be used in the interface for when I don't want to type something over and over
        super().__init__(filename,url,creationDateTime)
        self.datafilesource_id=int(datafilesource_id)
        self.url=URL_STAND.urlClean(str(url)) #FIXME nasty bug with repos
        self.filename=filename
        #if experiment_id is not None:
        self.experiment_id=int(experiment_id) #enforcing the idea that datafiles must have experiments
        self.subjects.extend(Subjects) #TODO in the interface.py make it so that current subjects 'auto' fill?


class InDatabaseData(Base): #TODO
    id=Column(Integer, primary_key=True)
