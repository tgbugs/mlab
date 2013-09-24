from os import sep
from database.imports import *
from database.base import Base
from database.mixins import HasNotes, HasMetaData
from database.standards import URL_STAND

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

###-------------
###  DataSources
###-------------

#datasource examples:
#espX, espY
#NBQX_washin_start, concentration #by associating the data source with a reagent instead of a person... the data is there for both the acsf_id and all the drug information :), #FIXME unfortunately that leads to a massive proliferation of datasources :/, so we need to find a better way >_< since this is more along the lines of 'protocol metadata'

class DataSource(Base): #FIXME this could also be called 'DataStreams' or 'RawDataSource'?
    """used for doccumenting how data was COLLECTED not where it came from, may need to fix naming"""
    #lol this might also have metadata fuck, ie the calibrations might go here???!
    #definable by parent and having matching properties? nah, just keep it generic?
    #might be able to cut this out entirely?
    __tablename__='datasources'
    id=Column(Integer,primary_key=True)
    #I mean, sure once 'source' back propagates down it will be ok but wtf
    name=Column(String(20),nullable=False) #FIXME unforunately the one disadvantage of this setup is that there are no real constraints to prevent someone from forming an erroious link between types of data and where it comes from
    #FIXME if these are going to be sources for datafiles they need to accomodate lack of units...
    #FIXME where do we keep the calibration data ;_;
    #define some properties
    prefix=Column(String(2),ForeignKey('si_prefix.symbol'),nullable=False)#,unique=True)
    unit=Column(String(3),ForeignKey('si_unit.symbol'),nullable=False)#,unique=True)
    ds_calibration_rec=Column(Integer,ForeignKey('calibrationdata.id')) #FIXME TODO just need a way to match the last calibration to the metadata... shouldn't be too hard
    #expmetadata=relationship('ExpMetaData',backref=backref('datasource',uselist=False))
    #datafiles=relationship('DataFile',backref=backref('datasource',uselist=False)) #FIXME urmmmmmm fuck? this here or make a different set of datasources for data not stored in the database? well datafiles are produced by camplex and I suppose at some point I might pull data direct from it too so sure, that works out
    def strHelper(self):
        return '%s%s'%(self.prefix,self.unit)
    def __repr__(self):
        return '\n%s units %s%s'%(self.name,self.prefix,self.unit)


###-----------------------------------------------
###  MetaData tables (for stuff stored internally)
###-----------------------------------------------

#FIXME it seems like what I really need here is MetaData linked to datafiles instead of experiments??? think about the best way to do this
#FIXME need to come up with all my metadata classes, this one is really 'experiment metadata' I do NOT think that these need to have inheritance structures becasue the only thing that is similar is datetime
#FIXME in theory we *could* use a HasMetaData mixin ?
#TODO ideally it should be possible to use the experiment id or something to know what the metadata looks like, if not the experiment ID then SOME datasource profile or something
#AHHA! TODO datasource profiles are how we can make metadata rigorous or at least quickly parse metadata in the event that we did not keep the records

'''
class ExpMetaData(Base): #FIXME we may not need this since 'Experiment' can directly link to other tables and it needs to be able to do this, I think it is worth the table proliferation, we may still want to use this for stuff like pharmacology???
    """This table is now extensible and I can add new dimensions to the data for any experiment whenever the fuck I feel like it :D, I could make a constrain to make sure that the number of dimesions I enter for an experiment is correct, but frankly that adds a ton of work every time I want to add a new variable to an experiment or something, this way commits of ANY single datapoint will not depend on all the other data being there too, might want to add a source id????"""
    #FIXME the proper way to interact with these tables for consistency is through another script that defines all the data that we are going to store
    #the reason we don't use this for everything is because adding slice and cell metadata as a new value is because those things are external objects that contain their OWN metadata
    #metadata in this table should not then have its own metadata that could be in this table
    id=None
    experiment_id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)
    datasource_id=Column(Integer,ForeignKey('datasources.id'),primary_key=True) #each datasource is a dimesion and each dimesion should be unique and identify the value
    dateTime=Column(DateTime,nullable=False) #FIXME is this a good enough fail safe if we somehow lost the ds?
    value=Column(Float(53),nullable=False)
    sigfigs=Column(Integer) #FIXME how would these be used? enforce truncation?
    #TODO need to find a way to standardize reporting uncertanity
    abs_error=Column(Float(53)) #FIXME does this go here, I think for some cases it does might want to qualify it with an 'estimated error' since some of this will be human entered data... but this makes things less rigorous so... damn it

class DFMetaData(Base): #FIXME this can just replace datafile!
    id=None
    datasource_id=Column(Integer,ForeignKey('datasources.id'),primary_key=True,autoincrement=False) #FIXME in theory no datafile should have two entries from the same datasource how I have this set up
    repoid=Column(Integer,primary_key=True,autoincrement=False)
    filename=Column(String,primary_key=True)
    dateTime=Column(DateTime,nullable=False)
    value=Column(Float(53),nullable=False)
    sigfigs=Column(Integer)
    abs_error=Column(Float(53))
    
    __table_args__=(ForeignKeyConstraint([repoid,filename],['datafile.repopath_id','datafile.filename']), {})


class CellMetaData(Base): #FIXME should this somehow be replaced by 'subjectMetaData'???
    id=None
    cell_id=Column(Integer,ForeignKey('cell.id'),primary_key=True,autoincrement=False) #FIXME in theory no datafile should have two entries from the same datasource how I have this set up
    datasource_id=Column(Integer,ForeignKey('datasources.id'),primary_key=True,autoincrement=False) #FIXME in theory no datafile should have two entries from the same datasource how I have this set up
    dateTime=Column(DateTime,nullable=False)
    value=Column(Float(53),nullable=False) #FIXME I wish this could be a mutable type?!?!!
    #TODO XXX GOOD NEWS! :D turns out for gfp +/- AND for genotypes on mice those are just boolean you turd, 0/1 in the float field and you are done
    sigfigs=Column(Integer)
    abs_error=Column(Float(53))


class HWMetaData(Base):
    #we could* store calibration files here???
    id=None
    hw_id=Column(Integer,ForeignKey('hardware.id'),primary_key=True)
    datasource_id=Column(Integer,ForeignKey('datasources.id'),primary_key=True)
    dateTime=Column(DateTime,nullable=False)
    value=Column(Float(53),nullable=False)
    sigfigs=Column(Integer)
    abs_error=Column(Float(53))

class PharmacologyData(Base): #TODO
    #consistency is achieve here by having another script that stores which drugs and the in and the out, maybe even another table??
    id=None
    experiment_id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)
    datasource_id=Column(Integer,ForeignKey('datasources.id'),nullable=False) #FIXME, should this be a primary key? it would mean that espX and espY would have to be considered different datasources..., BUT it would mean that any/every metadata entry would be tagged with a datasource
    drug_id=Column(Integer,ForeignKey('reagents.name'),primary_key=True)
    solution_id=Column(Integer,ForeignKey('solutions.id'),nullable=False)
    event_type=None
    event_datetime=None
    #FIXME pharmacology events and LED_stimulation are the same type of event/data, and the question is how and at what level we associate those...
'''


class CalibrationData(Base):
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
    id=None
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


class RepoPath(Base): #FIXME this may be missing trailing /on path :x
    __tablename__='repopaths'
    #Assumption: repository MUST be the full path to the data, so yes, a single 'repository' might have 10 entries, but that single repository is just a NAME and has not functional purpose for storing/retrieving data
    #id=Column(Integer,primary_key=True,autoincrement=True) #to simplify passing repos? is this reasonable?
    id=None
    name=Column(String)
    url=Column(String,ForeignKey('repository.url'),primary_key=True)
    path=Column(String,primary_key=True) #make this explicitly relative path?
    assoc_program=Column(String(30)) #FIXME some of these should be automatically updated and check by the programs etc
    verified=Column(Boolean,default=False) #TODO populated when the repopath has been verified to exist, should probably also check at startup for existence (will not check for datafiles)
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


class DataFile(HasMetaData, Base):
    #TODO path, should the database maintain this???, yes
    #how to constrain/track files so they don't get lost??
    #well, it is pretty simple you force the user to add them, this prevents all kinds of problems down the road
    #and the constraint will be populated by the DataPath table, if I have 10,000 datafiles though, that could become a NASTY change
    #ideally we want this to be dynamic so that the DataPath can change and all the DataFile entries will learn about it
    #it might just be better to do it by hand so UPDATE doesn't swamp everything
    #the path cannot be the primary key of the datapath table AND accomodate path changes
    #TODO next problem: when do we actually CREATE the DataFile and how to we get the number right even if we discard the trial? well, we DONT discard the file, we just keep it, but we need to gracefully deal with deletions/renumbering so that if something goes wrong it will alert to user
    #RESPONSE: this record cannot be created until the file itself exists
    id=None
    #repopath_id=Column(Integer,ForeignKey('repopaths.id'),primary_key=True,autoincrement=False) #FIXME this is what was causing errors previous commit, also decide if you want this or the both path and url
    #FIXME datafiles have substructure that requires more than one datasource ;_;
    #although, the easiest way to fix that is to just change this to allow for an arbitrary number of channels to be saved per datafile and link the datasources to those?
    #maybe base it on datafile type??? or configuration... but that is going to change for every fucking thing...
    #that stuff goes in the metadata, datasource here just means 'collection software' fucking conflation
    url=Column(String,primary_key=True,autoincrement=False)
    path=Column(String,primary_key=True,autoincrement=False)
    __table_args__=(ForeignKeyConstraint([url,path],['repopaths.url','repopaths.path']), {}) #FIXME this *could* be really fucking slow because they arent indexed, may need to revert these changes, ah well
    filename=Column(String,primary_key=True,autoincrement=False) #urp! on ext3 255 max for EACH /asdf/
    datasource_id=Column(Integer,ForeignKey('datasources.id'),nullable=False)
    creationDateTime=Column(DateTime,default=datetime.now) #somehow this seems like reproducing filesystem data... this, repo and metadata all seem like they could be recombined down... except that md has multiple datafiles?

    #FUCK this is a many to many >_< BUT I can to a similar thing as I did for metadata!
    #FIXME 'has datafiles' is not isomorphic with subjects >_<

    @declared_attr
    def metadata_(cls): #FIXME naming...
        class DataFileMetaData(Base):
            __tablename__='datafiles_metadata'
            id=Column(Integer,primary_key=True)
            url=Column(String,nullable=False)
            path=Column(String,nullable=False)
            filename=Column(String,nullable=False)
            __table_args__=(ForeignKeyConstraint([url,path,filename],['datafile.url','datafile.path','datafile.filename']), {})
            datasource_id=Column(Integer,ForeignKey('datasources.id'),nullable=False)
            dateTime=Column(DateTime,default=datetime.now)
            value=Column(Float(53),nullable=False)
            sigfigs=Column(Integer) #TODO
            abs_error=Column(Float(53)) #TODO
            datasource=relationship('DataSource')
            def __init__(self,value,DataFile=None,DataSource=None,datasource_id=None,url=None,path=None,filename=None,sigfigs=None,abs_error=None,dateTime=None):
                self.dateTime=dateTime
                self.url=url
                self.path=path
                self.filename=filename
                self.datasource_id=datasource_id
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
                self.AssignID(DataSource)
            def __repr__(self):
                sigfigs=''
                error=''
                if self.sigfigs: sigfigs=self.sigfigs
                if self.abs_error != None: error='%s %s'%(_plusMinus,self.abs_error)
                return '%s %s %s %s %s'%(self.dateTime,self.value,self.datasource.strHelper(),sigfigs,error)

        cls.MetaData=DataFileMetaData
        return relationship(cls.MetaData)


    #analysis_DateTime
    #FIXME a bunch of these DateTimes should be TIMESTAMP? using the python implementation is more consistent?
    @hybrid_property #FIXME this isn't really hybrid...
    def filetype(self):
        return self.filename.split('.')[-1]
    @filetype.setter
    def filetype(self):
        raise AttributeError('readonly attribute, there should be a file name associate with this record?')
    def __init__(self,RepoPath=None,filename=None,DataSource=None,url=None,path=None,datasource_id=None,Cells=[], creationDateTime=None): #FIXME Cells should be 'thing that has DataFiles...'
        #self.url=URL_STAND.baseClean(repo_url)
        #self.repo_path=URL_STAND.pathClean(repo_path)
        self.url=url
        self.path=path
        self.filename=filename
        self.creationDateTime=creationDateTime
        self.datasource_id=datasource_id
        #self.AssignID(Experiment) #FIXME should be subject instead?!?!
        self.AssignID(DataSource)
        self.patchcell.extend(Cells) #TODO listlike #FIXME there's going to be a row for every bloody thing with HasDataFiles
        #FIXME can I have an in-database check to make sure that pairs of cells match CellPairs???
        if RepoPath:
            if RepoPath.url:
                self.url=RepoPath.url
                self.path=RepoPath.path
            else:
                raise AttributeError('RepoPath has no url/path! Did you commit before referencing the instance directly?')
    def strHelper(self,depth=0):
        return super(depth,'filename')
    def __repr__(self):
        return '\n%s%s%s%s'%(self.url,self.path,os.sep,self.filename)


class InDatabaseData(Base):
    #TODO, need something more flexible than metadata (amazingly) that can hold stuff like calibration data not stored elsewhere?? also if I ever transition away from external datafiles or if I want to use neoio immediately to convert abf files
    pass

