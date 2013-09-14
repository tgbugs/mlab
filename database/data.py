from database.imports import *
from datetime import datetime

from sqlalchemy                         import Float
from sqlalchemy                         import Text
from sqlalchemy                         import ForeignKeyConstraint
from sqlalchemy.ext.associationproxy    import association_proxy

from database.base import Base, HasNotes
from database.standards import URL_STAND
#from notes import HasNotes

###--------------------
###  Measurement tables, to enforce untils and things... it may look over normalized, but it means that every single measurement I take will have a datetime associated as well as units
###--------------------




        

class DataSource(Base): #FIXME this could also be called 'DataStreams' or 'RawDataSource'?
    """used for doccumenting how data was COLLECTED not where it came from, may need to fix naming"""
    #definable by parent and having matching properties? nah, just keep it generic?
    #might be able to cut this out entirely?
    __tablename__='datasources'
    id=Column(Integer,primary_key=True)
    #I mean, sure once 'source' back propagates down it will be ok but wtf
    name=Column(String,nullable=False) #FIXME unforunately the one disadvantage of this setup is that there are no real constraints to prevent someone from forming an erroious link between types of data and where it comes from
    #FIXME where do we keep the calibration data ;_;
    #define some properties
    prefix=Column(String,ForeignKey('si_prefix.symbol'),nullable=False)
    unit=Column(String,ForeignKey('si_unit.symbol'),nullable=False)
    ds_calibration_rec=Column(String,ForeignKey('calibrecs.id')) #FIXME TODO just need a way to match the last calibration to the metadata... shouldn't be too hard
    metadata=relationship('MetaData',backref=backref('datasource',uselist=False))
    datafiles=relationship('DataFile',backref=backref('datasource',uselist=False)) #FIXME urmmmmmm fuck? this here or make a different set of datasources for data not stored in the database? well datafiles are produced by camplex and I suppose at some point I might pull data direct from it too so sure, that works out

class Result(HasNotes, Base):
    __tablename__='results'
    datasource_id=None
    analysis_id=None
    output_id=None

class MetaData(Base):
    """This table is now extensible and I can add new dimensions to the data for any experiment whenever the fuck I feel like it :D, I could make a constrain to make sure that the number of dimesions I enter for an experiment is correct, but frankly that adds a ton of work every time I want to add a new variable to an experiment or something, this way commits of ANY single datapoint will not depend on all the other data being there too, might want to add a source id????"""
    #the reason we don't use this for everything is because adding slice and cell metadata as a new value is because those things are external objects that contain their OWN metadata
    #metadata in this table should not then have its own metadata that could be in this table
    id=None
    experiment_id=Column(Integer,ForeignKey('experiments.id'),primary_key=True)
    datasource_id=Column(Integer,ForeignKey('datasources.id'),nullable=False) #FIXME, should this be a primary key? it would mean that espX and espY would have to be considered different datasources..., BUT it would mean that any/every metadata entry would be tagged with a datasource
    dateTime=Column(DateTime,nullable=False) #FIXME is this a good enough fail safe if we somehow lost the ds?
    value=Column(Float(53),nullable=False)
    #abs_error=Column(Float(53)) #FIXME does this go here, I think for some cases it does might want to qualify it with an 'estimated error' since some of this will be human entered data... but this makes things less rigorous so... damn it

class OneDData(HasNotes, Base): #FIXME should be possible to add dimensions here without too much trouble, but keep it < 3d, stuff that is entered manually or is associated with an object
    #id=None #FIXME for now we are just going to go with id as primary_key since we cannot gurantee atomicity for getting datetimes :/
    #FIXME this should be a Base data class where each extra dimension adds another column
    #FIXME THEN it can be inherited by specific object/table pairs that record that kind of data
    #EXAMPLE: a WaterRecord row is a OneDData that also has a mouse_id and a type!
    dateTime=Column(DateTime,nullable=False) #FIXME tons of problems with using dateTime/TIMESTAMP for primary key :(
    #FIXME I am currently automatically generating datetime entries for this because I want the record of when it was put into the database, not when it was actually measured...
    #This behavior is more consistent and COULD maybe be used as a pk along with data source

    #SI_unit_symbol=Column(String,ForeignKey('si_unit.symbol'),nullable=False)
    #SI_unit_name=Column(String,ForeignKey('si_unit.name'),nullable=False) #FIXME damn it plurals fucking everything up, handle those elsewhere
    #SI_prefix=Column(String,ForeignKey('si_unit.symbol'),nullable=False) #FIXME make sure this works with '' for no prefix or that that is handled as expected
    #prefix=relationship('SI_PREFIX')
    #units=relationship('SI_UNIT')

    #ieee double, numpy float64, 52bits of mantissa with precision of 53bits
    source_id=Column(Integer,ForeignKey('datasources.id'),nullable=False) #backref FIXME
    value1=Column(Float(53),nullable=False) #FIXME make sure this is right; FIXME should this be nullable, see if there are use cases where None for a value instead of zero is useful?
    value2=Column(Float(53))
    value3=Column(Float(53))
    #somehow I think that there is a possibility that I will want to have a form of some kind where I have lots of measurements but 
    def __init__(self,value,SI_prefix,SI_unit,Source=None,source_id=None):
        self.dateTime=datetime.utcnow() #FIXME
        self.value=value
        self.SI_prefix=SI_prefix
        self.SI_unit=SI_unit
        self.source_id=source_id

        if Source:
            if Source.id:
                self.source_id=Source.id
            else:
                raise AttributeError('Source has no id! Did you commit before referencing the instance directly?')
    def __repr__(self):
        return '\n%s %s%s collected %s from %s'%(self.value,self.prefix,self.units,frmtDT(self.dateTime),self.source.strHelper())

class espPosition(OneDData): #oh look, 2d metadata! just as planned
    """table to hold all the esp positions that I collect, they can be associated to a cell, or to a stimulation event or whatever"""
    id=Column(Integer,ForeignKey('oneddata.id'),primary_key=True)
    #this needs an association table or a mixin for HasPosition or some shit ;_; ?? or 'HasData' or something...
    #x
    #y
    associated_object=Column(Integer) #bugger
    pass


class espCalibration(HasNotes, Base):
    pass
###------------
###  Doccuments
###------------

class person_to_project(Base):
    id=None
    person_id=Column(Integer,ForeignKey('people.id'),primary_key=True)
    project_id=Column(Integer,ForeignKey('project.id'),primary_key=True)
    #TODO add some nice info about what the person is doing on the project or some shit
    def __init__(self, Project=None, Person=None, project_id=None,person_id=None):
        self.project_id=project_id
        self.person_id=person_id
        if Project:
            if Project.id:
                self.project_id=Project.id
            else:
                raise AttributeError
        if Person:
            if Person.id:
                self.person_id=Person.id
            else:
                raise AttributeError

class Project(Base): #FIXME ya know this looks REALLY similar to a paper or a journal article
    #move to the 'data/docs' place?!??! because it is tehcnically a container for data not a table that will actively have data written to it, it is a one off reference
    #FIXME somehow experiment is dependent on this... which suggests that it doesn't quite belong in data
    lab=Column(String,nullable=False) #this is how we are going to replace the bloodly PI, and leave at the filter Role=='pi'
    #pi_id=Column(Integer,ForeignKey('people.id')) #FIXME need better options than fkc... need a check constraint on people.role=='PI', or really current role... because those could change and violate certain checks/constraints...??? maybe better just to leave it as a person
    #FIXME projects can have multiple PIs! damn it >_<, scaling this shit...
    iacuc_protocol_id=Column(Integer,ForeignKey('iacucprotocols.id'))
    blurb=Column(Text)

    #PI=relationship('Person',primaryjoin='and_(Project.pi_id==Person.id,Person.Rold=="pi")') #FIXME pi should also be in people list :/
    p2p_assoc=relationship('person_to_project',backref='projects')
    #FIXME do we really want write access here? viewonly=True might be useful?
    people=association_proxy('p2p_assoc','people') #people.append but make sure nothing wierd happends
    relationship
    def __init__(self,lab=None,iacuc_protocol_id=None,blurb=None):
        #self.pi_id=pi_id
        self.lab=lab
        self.iacuc_protocol_id=iacuc_protocol_id
        self.blurb=blurb
        #if PI:
            #if PI.id:
                #pi_id=PI.id
            #else:
                #raise AttributeError


class IACUCProtocols(Base): #note: probs can't store them here, but just put a number and a link (frankly no sense, they are kept in good order elsewere)
    pass

class Protocols(Base):
    pass

class Recipe(HasNotes, Base):
    id=Column(String,primary_key=True)
    #acsf
    #internal
    #sucrose

###-------------
###  Datasources/Datasyncs
###-------------



class Repository(Base):
    #TODO urllib parse, these will go elsewhere in the actual analysis code or something
    #TODO request.urlopen works perfectly for filesystem stuff
    #file:///C: #apparently chromium uses file:///C:
    #file:///D: are technically the base
    id=None
    url=Column(String,primary_key=True) #use urllib.parse for this
    credentials_id=Column(Integer,ForeignKey('credentials.id')) 
    blurb=Column(Text)
    paths=relationship('RepoPath',primaryjoin='RepoPath.repo_url==Repository.url')
    #FIXME, move this to people/users because this is part of credentialing not data? move it to wherever I end up putting 'credential things' like users
    #TODO, if we are going to store these in a database then the db needs to pass sec tests, but it is probably better than trying to secure them in a separate file, BUT we will unify all our secure credentials management with the same system
    #TODO there should be a default folder or 
    #access_manager=Column(String) #FIXME the credentials manager will handle this all by itself
    def __init__(self,url,credentials_id=None):
        self.url=URL_STAND.baseClean(url)
        self.credentials_id=credentials_id


class RepoPath(Base):
    __tablename__='repopaths'
    #Assumption: repository MUST be the full path to the data, so yes, a single 'repository' might have 10 entries, but that single repository is just a NAME and has not functional purpose for storing/retrieving data
    id=Column(Integer,primary_key=True,autoincrement=True) #to simplify passing repos? is this reasonable?
    repo_url=Column(String,ForeignKey('repository.url'))#,primary_key=True) FIXME
    path=Column(String)#,primary_key=True) #make this explicitly relative path?
    assoc_program=Column(String) #FIXME some of these should be automatically updated and check by the programs etc
    relationship('DataFile',backref='repository_path') #FIXME datafiles can be kept in multiple repos...
    #TODO how do we keep track of data duplication and backups!?!?!?
    blurb=Column(Text) #a little note saying what data is stored here, eg, abf files
    #TODO we MUST maintain synchrony between where external programs put files and where the database THINKS they put files, some programs may be able to have this specified on file creation, check the clxapi for example, note has to be done by hand for that one
    #FIXME should the REPO HERE maintain a list of files? the filesystem KNOWS what is there
    def __init__(self,Repo=None,repo_url=None,path=None,assoc_program=None,name=None):
        self.repo_url=URL_STAND.baseClean(repo_url)
        self.assoc_program=assoc_program
        self.name=name
        if Repo:
            if Repo.url:
                self.repo_url=Repo.url
            else:
                raise AttributeError('Repository has no url! Did you commit before referencing the instance directly?') #FIXME this should never trigger because url is a primary key and not an autoincrementing int...
        clean_path=URL_STAND.pathClean(path)
        #test to make sure the directory exists
        URL_STAND.test_url(self.repo_url+clean_path) #FIXME may need a try in here
        self.path=clean_path


class DataFile(Base): #FIXME make sure that this class looks a whole fucking lot like MetaData
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
    #Assumption: repository ID's refer to a single filesystem folder where there cannot be duplicate names
    #repo_url=Column(Integer,ForeignKey('repository.url'),primary_key=True)
    #repo_path=Column(Integer, ForeignKey('repopaths.path'), primary_key=True)
    #with two above can direcly get the file from this record without having to do any cross table magic...
    repopath_id=Column(Integer,ForeignKey('repopaths.id'),primary_key=True) #FIXME this is what was causing errors previous commit, also decide if you want this or the both path and url
    filename=Column(String,primary_key=True)
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False) #TODO think about how to associate these with other experiments? well, even a random image file will have an experiment... or should or be the only thing IN an experiment
    #creation_DateTime=Column(DateTime,nullable=False) #somehow this seems like reproducing filesystem data... this, repo and metadata all seem like they could be recombined down... except that md has multiple datafiles?
    creation_DateTime=Column(DateTime,nullable=False) #somehow this seems like reproducing filesystem data... this, repo and metadata all seem like they could be recombined down... except that md has multiple datafiles?
    #analysis_DateTime
    #FIXME a bunch of these DateTimes should be TIMESTAMP? using the python implementation is more consistent?
    @property
    def filetype(self):
        return self.filename.split('.')[-1]
    @filetype.setter
    def filetype(self):
        raise AttributeError('readonly attribute, there should be a file name associate with this record?')
    #metadata_id=Column(Integer,ForeignKey('metadata.id')) #FIXME what are we going to do about this eh?
    def __init__(self,RepoPath=None,Experiment=None, repopath_id=None, repo_url=None,repo_path=None,experiment_id=None,filename=None):
        #self.repo_url=URL_STAND.baseClean(repo_url)
        #self.repo_path=URL_STAND.pathClean(repo_path)
        self.repopath_id=repopath_id
        self.filename=filename
        self.experiment_id=experiment_id
        self.creation_DateTime=datetime.utcnow()
        if RepoPath:
            if RepoPath.id:
                #printD(RepoPath.id)
                self.repopath_id=RepoPath.id
            else:
                raise AttributeError('RepoPath has no id! Did you commit before referencing the instance directly?')
        if Experiment:
            if Experiment.id:
                #printD(Experiment.id)
                self.experiment_id=Experiment.id
            else:
                raise AttributeError('Experiment has no id! Did you commit before referencing the instance directly?')


