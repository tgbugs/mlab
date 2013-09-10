from datetime import datetime

from sqlalchemy                         import Float
from sqlalchemy                         import ForeignKeyConstraint

from database.main import Base
from notes import HasNotes

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

    SI_unit=Column(String,nullable=False)
    ForeignKeyConstraint('OneDData.SI_unit',['SI_UNIT.symbol','SI_UNIT.name'])
    SI_prefix=Column(String,nullable=False) #FIXME make sure this works with '' for no prefix or that that is handled as expected
    ForeignKeyConstraint('OneDData.SI_prefix',['SI_PREFIX.prefix','SI_PREFIX.symbol','SI_PREFIX.E']) #FIXME table names?

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

###-------------
###  Datasources/Datasyncs
###-------------

class Protocols(Base):
    pass

class Recipe(HasNotes, Base):
    id=Column(String,primary_key=True)
    #acsf
    #internal
    #sucrose

class Reposity(Base):
    #FIXME url should be full path
    url=Column(String) #make sure this can follow logical file:// or localhost://
    name=Column(String) #a little note saying what data is stored here, eg, abf files
    credentials_file=Column(String) #TODO this is going to be a massive security bit

class DataFile(Base):
    #TODO path, should the database maintain this???, yes
    #how to constrain/track files so they don't get lost??
    #well, it is pretty simple you force the user to add them, this prevents all kinds of problems down the road
    #and the constraint will be populated by the DataPath table, if I have 10,000 datafiles though, that could become a NASTY change
    #ideally we want this to be dynamic so that the DataPath can change and all the DataFile entries will learn about it
    #it might just be better to do it by hand so UPDATE doesn't swamp everything
    #the path cannot be the primary key of the datapath table AND accomodate path changes
    repo_id=Column(Integer, ForeignKey('repository.id'))
    filename=Column(String)
    extension=Column(String,Foreignkey('df_extensions.type'))
    metadata_id=Column(Integer,ForeignKey('metadata.id'))
    creation_DateTime=Column(DateTime,nullable=False) #somehow this seems like reproducing filesystem data... this, repo and metadata all seem like they could be recombined down... except that md has multiple datafiles?

    experiment_id=Column(Integer,ForeignKey('experiments.id'))


Base.metadata.create_all(engine)
