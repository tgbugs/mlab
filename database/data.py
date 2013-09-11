from database.imports import *
from datetime import datetime

from sqlalchemy                         import Float
from sqlalchemy                         import Text
from sqlalchemy                         import ForeignKeyConstraint

from database.base import Base, HasNotes
from database.standards import URL_STAND
#from notes import HasNotes

###--------------------
###  Measurement tables, to enforce untils and things... it may look over normalized, but it means that every single measurement I take will have a datetime associated as well as units
###--------------------

class Datasource(HasNotes, Base):
    __tablename__='datasources'
    source_class=Column(String)
    ForeignKeyConstraint('Datasource.source_class',['people.id','users.id','datafile.id'])
    data1=relationship('OneDData',backref=backref('source',uselist=False))
    #FIXME 

class Result(HasNotes, Base):
    __tablename__='results'
    datasource_id=None
    analysis_id=None
    output_id=None


class OneDData(HasNotes, Base): #FIXME should be possible to add dimensions here without too much trouble, but keep it < 3d, stuff that is entered manually or is associated with an object
    #id=None #FIXME for now we are just going to go with id as primary_key since we cannot gurantee atomicity for getting datetimes :/
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

class espPosition(OneDData):
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

class Project(Base): #FIXME ya know this looks REALLY similar to a paper or a journal article
    #move to the 'data/docs' place?!??! because it is tehcnically a container for data not a table that will actively have data written to it, it is a one off reference
    PI=Column(Integer,ForeignKey('people.id')) #FIXME need better options than fkc...
    people=relationship('Person',backref='projects') #FIXME m-m
    protocol_number=Column(Integer,ForeignKey('iacucprotocols.id'))
    blurb=Column(Text)


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
    paths=relationship('RepoPath',primaryjoin='Repopath.repository==Repository.url')
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
    id=Column(Integer,unique=True,autoincrement=True) #to simplify passing repos? is this reasonable?
    repo_url=Column(String,ForeignKey('repository.url'),primary_key=True)
    path=Column(String,primary_key=True) #make this explicitly relative path?
    assoc_program=Column(String) #FIXME some of these should be automatically updated and check by the programs etc
    relationship('DataFile',backref='repository_path') #FIXME datafiles can be kept in multiple repos...
    #TODO how do we keep track of data duplication and backups!?!?!?
    blurb=Column(Text) #a little note saying what data is stored here, eg, abf files
    #TODO we MUST maintain synchrony between where external programs put files and where the database THINKS they put files, some programs may be able to have this specified on file creation, check the clxapi for example, note has to be done by hand for that one
    #FIXME should the REPO HERE maintain a list of files? the filesystem KNOWS what is there
    def __init__(self,Repo=None,repository_url=None,path=None,assoc_program=None,name=None):
        self.repo_url=URL_STAND.baseClean(repository)
        #test to make sure the directory exists
        clean_path=URL_STAND.pathClean(path)
        URL_STAND.test_url(self.repository_url+clean_path) #FIXME may need a try in here
        self.path=clean_path
        self.assoc_program=assoc_program
        self.name=name
        if Repository:
            if Repository.url:
                self.repo_url=Repository.url
            else:
                raise AttributeError('Repository has no url! Did you commit before referencing the instance directly?')


class DataFile(Base):
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
    repo_url=Column(Integer,ForeignKey('repository.url'),PrimaryKey=True)
    repo_path=Column(Integer, ForeignKey('repopaths.path'), PrimaryKey=True)
    filename=Column(String,PrimarKey=True)
    experiment_id=Column(Integer,ForeignKey('experiments.id')) #FIXME WHEN DO WE LINK THIS??!?!?!?
    creation_DateTime=Column(DateTime,nullable=False) #somehow this seems like reproducing filesystem data... this, repo and metadata all seem like they could be recombined down... except that md has multiple datafiles?
    #FIXME a bunch of these DateTimes should be TIMESTAMP? using the python implementation is more consistent?
    @property
    def filetype(self):
        return self.filename.split('.')[-1]
    @filetype.setter
    def filetype(self):
        raise AttributeError('readonly attribute, there should be a file name associate with this record?')
    #metadata_id=Column(Integer,ForeignKey('metadata.id')) #FIXME what are we going to do about this eh?
    def __init__(self,RepoPath=None,repo_url=None,repo_path=None,filename=None,experitment_id=None):
        self.repo_url=repo_url
        self.repo_path=repo_path
        self.filename=filename
        self.experiment_id=experiment_id
        self.creation_DateTime=datetime.utcnow()
        if RepoPath:
            if RepoPath.id:
                self.repopath_id=RepoPath.id


