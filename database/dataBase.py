#Base file for creating the tables that I will use to store all my (meta)data


#TODO therefore we need a 'convert local to utc for storage'
#TODO start moving stuff out of here that we don't use to define the tables
#TODO watch out for sqlite_autoincriment=True needed when using composite keys!
#TODO going to need the 'PRAGMA foreign_keys=ON' ???
#TODO I can just store the bloody python code used to calculate the values in another column... >_<, that will allow for consistnecy check even if code changes
#TODO install git you asshole
#TODO aleks says overnormalization is just stuipd for this?

#TODO conform to MINI, NIF ontologies?, or odML terminiologies?

#TODO autogenerate ALL THE DATES based on startDateTime
#table of projected dates which has: estimated and actual pairs for each one
#but we don't really need that information stored because we can just generate it

#TODO
### Create an IsLoggable class or the like to manage logging changes to fields
#see: http://stackoverflow.com/questions/141612/database-structure-to-track-change-history
#TODO transaction log will have a first entry for...
#internal doccumentation of the creation date may not be needed if I have refs to transactions

#TODO transfer logs for mice can now be done and incorporated directly with the system for weening etc

#TODO reimplement notes so that they can apply to multiple things like I do with classDOB, but check the overhead, join inheritance might work
#make sure to set the 'existing table' option or something?


from datetime import datetime,timedelta #ALL TIMES ARE UTC WITH tzinfo=None, CONVERT LATER

#IEEE DOUBLE and numpy float64 have the same format, 1 bit sign, 11 bits exponent, 52 bits mantissa
from sqlalchemy                         import Table, Column, Boolean, Integer, Float, String, Text, DateTime, Date, ForeignKey, ForeignKeyConstraint, CheckConstraint, create_engine, event
from sqlalchemy.orm                     import relationship, backref, Session
from sqlalchemy.ext.declarative         import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy    import association_proxy
from sqlalchemy.engine                  import Engine

#import sys
#sys.path.append('T:/db/Dropbox/mlab/code/')

from tomsDebug                          import TDB

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict

#some global variables that are used here and there that would be magic otherwise
plusMinus='\u00B1'

###---------------------------------------------------------------
###  Datetime and timedelta functions to be reused for consistency
###---------------------------------------------------------------

def frmtDT(dateTime,formatString='%Y/%m/%d %H:%M:%S',localtime=False):
    if localtime:
        return 'the dt run through some function that converts UTC to whatever the current local timezone is polled from the system' #FIXME
    return datetime.strftime(dateTime,formatString)

def timeDeltaIO(tdORfloat):
    try:
        return tdORfloat.total_seconds()
    except:
        try:
            return timedelta(seconds=tdORfloat)
        except TypeError:
            raise TypeError('That wasn\'t a float OR a timedelta, what the hell are you feeding the poor thing!?')



class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id=Column(Integer, primary_key=True)

    def strHelper(self,depth=0,attr='id'):
        tabs='\t'*depth
        return '\n%s%s %s'%(tabs,self.__class__.__name__,getattr(self,attr))
    def __repr__(self,attr='id'):
        return '\n%s %s'%(self.__class__.__name__,getattr(self,attr))

Base=declarative_base(cls=Base) #make an instance of the base class


#all I want is a many-many relationship between targets and notes but that doesn't quite work ;_; Association per tble maybe?? that way we don't need a mixin

class NoteAssociation(Base): #turns out we want joined table inheritance... #I think I need multiple tables for this...
    __tablename__='note_association'
    id=Column(Integer, primary_key=True)
    discriminator=Column(String) #there should now be a single row per discrminator

    @classmethod
    def creator(cls, discriminator):
        return lambda notes:NoteAssociation(notes=notes,discriminator=discriminator)
    #parents backref from HasNotes but we don't have... any... HasNotes_id to link these things..., may need a primary join
    #FIXME this needs to become 'table per' for the association part I think :/ check the examples


class Note(Base):
    __tablename__='notes'
    association_id=Column(Integer,ForeignKey('note_association.id'))
    source_id=Column(Integer,ForeignKey('datasources.id'))
    text=Column(Text,nullable=False)
    dateTime=Column(DateTime,nullable=False) #FIXME get rid of this and replace it with the transaction logs make things really simple
    #lbRefs=Column(Integer,ForeignKey('labbook.id') #FIXME

    association=relationship('NoteAssociation',backref='notes')
    parents=association_proxy('association','parents')

    def __init__(self,text):
        self.text=text
        self.dateTime=datetime.utcnow() #enforce datetime consistency!
    def __repr__(self):
        return '\n%s %s %s\n%s\n\t"%s"'% (self.__class__.__name__, ''.join([a.discriminator for a in self.association]), ''.join([p.id for p in self.parents]), frmtDT(self.dateTime), self.text) #FIXME


class HasNotes(object): #FIXME
    @declared_attr
    def note_association_id(cls):
        pass
        #return Column(Integer,ForeignKey('note_association.id'))
        #return cls.__table__.c.get('note_association_id',Column(Integer, ForeignKey('note_association.id')))
    @declared_attr
    def note_association(cls):
        pass
        #discriminator=cls.__name__.lower()
        #cls.notes=association_proxy('note_association','notes',creator=NoteAssociation.creator(discriminator)) #i think the problem is with the creator..
        #return relationship('NoteAssociation',backref=backref('parents'))
    def addNote(string): #FIXME?
        pass

###---------------
###  People tables
###---------------

class User(Base):
    __tablename__='users'
    #because why the fuck not...
    pass

class Person(HasNotes, Base):
    __tablename__='people'
    PrefixName=Column(String) #BECAUSE FUCK YOU
    FirstName=Column(String)
    MiddleName=Column(String)
    LastName=Column(String)
    #Gender=Column(String,ForeignKey('sex.id')) #LOL
    Gender=Column(String)
    ForeignKeyConstraint('Person.sex',['sex.name','sex.symbol','sex.abbrev'])
    Birthdate=Column(Date) #this is here to match the odML, I actually think it is stupid to have, but whatever
    #Role=Column(String,ForeignKey('role.id'))
    Role=Column(String)
    neurotree_id=Column(Integer) #for shits and gigs
    experiments=relationship('Experiment',backref='investigator') #SOMETHING SOMETHING ACCESS CONTROL


###----------------------
###  cages and cage racks
###----------------------

class CageRack(Base):
    id=Column(Integer,primary_key=True)
    row=Column(Integer,primary_key=True,autoincrement=False)
    col=Column(String,primary_key=True,autoincrement=False)
    cage_id=Column(Integer,ForeignKey('cage.id'))


class Cage(Base):
    #the cool bit is that I can actually do all of these before hand if I print out my cage cards and get them prepped
    id=Column(Integer,primary_key=True, autoincrement=False) #cage card numbers
    location=relationship('CageRack',backref=backref('cage',uselist=False),uselist=False)
    mice=relationship('Mouse',primaryjoin='Mouse.cage_id==Cage.id',backref=backref('cage',uselist=False))
    litter=relationship('Litter',primaryjoin='Litter.cage_id==Cage.id',backref=backref('cage',uselist=False))

###----------
###  Reagents
###----------

class Recipe(HasNotes, Base):
    id=Column(String,primary_key=True)
    #acsf
    #internal
    #sucrose

class Stock(HasNotes, Base):
    id=None
    recipe_id=Column(String,ForeignKey('recipe.id'),primary_key=True)
    mix_dateTime=Column(DateTime,primary_key=True) #this is a mix date time so it will do for a primary key FIXME not if I make 5 stocks at once and try to enter them at the same time

class Solution(HasNotes, Base): #using an id for the one since so much to pass along
    recipe_id=Column(String,ForeignKey('recipe.id'),primary_key=True) #sometimes it is easier to have an ID column if other tables need access
    mix_dateTime=Column(DateTime,unique=True) #this is a mix date time so it will do for a primary key
    osmolarity=Column(Integer,ForeignKey('oneddata.id'),unique=True) #FIXME NOW we need units :/ and HOW do we deal with THAT

    stock_id=Column(Integer,ForeignKey('stock.mix_dateTime'))

###--------------------
###  Measurement tables, to enforce untils and things... it may look over normalized, but it means that every single measurement I take will have a datetime associated as well as units
###--------------------

class Datasource(HasNotes, Base):
    __tablename__='datasources'
    source_class=Column(String)
    ForeignKeyConstraint('Datasource.source_class',['people.id','users.id'])
    data1=relationship('OneDData',backref=backref('source',uselist=False))

class OneDData(HasNotes, Base):
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
    value=Column(Float(53),nullable=False) #FIXME make sure this is right; FIXME should this be nullable, see if there are use cases where None for a value instead of zero is useful?
    #somehow I think that there is a possibility that I will want to have a form of some kind where I have lots of measurements but 
    def __init__(self,value,SI_prefix,SI_unit,Source=None,source_id=None):
        self.dateTime=datetime.utcnow()
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






###-----------------------------------------------------
###  MOUSE Defintions for mouse tables and relationships TODO this datamodel could be replicated for pretty much any model organism?
###-----------------------------------------------------

class DOB(Base): #FIXME class DATETHING???  to keep all the dates with specific 
    """Clean way to propagate dobs to litters and mice"""
    dateTime=Column(DateTime,nullable=False) #on my core i7 4770k I get a mean of 1996 sdt of 329 calls of datetime.utcnow() with a unique timestamp, heavy rightward skew
    absolute_error=Column(Float(precision=53)) #note: it is safe to store any timedelta less than a couple of years and still retain microseconds at full precision
    #estimated=Column(DateTime) #transaction thingy for later

    matingRecord=relationship('MatingRecord',primaryjoin='MatingRecord.dob_id==DOB.id',backref=backref('dob',uselist='False')) #FIXME need to force match litter/mr dob...
    printD('I get here')
    litter=relationship('Litter',primaryjoin='Litter.dob_id==DOB.id',backref=backref('dob',uselist=False)) #attempt to enforce one litter per DOB?
    mice=relationship('Mouse',primaryjoin='Mouse.dob_id==DOB.id',backref=backref('dob',uselist=False))

    def __init__(self,dateTime,absolute_error=None):
        self.dateTime=dateTime
        try:
            self.absolute_error=timeDeltaIO(timedelta)
        except:
            self.absolute_error=None

    def strHelper(self,depth=0):
        tabs='\t'*depth
        return '\n%sDOB %s %s %s'%(tabs,frmtDT(self.dateTime),plusMinus,self.absolute_error)
    def __repr__(self):
        return '\nDOB %s %s %s'%(frmtDT(self.dateTime),plusMinus,self.absolute_error)


class Mouse(HasNotes, Base):
    #in addition to the id, keep track of some of the real world ways people refer to mice!
    eartag=Column(Integer)
    tattoo=Column(Integer)
    num_in_lit=Column(Integer)  #for mice with no eartag or tattoo, numbered in litter, might replace this with mouse ID proper?
    name=Column(String)  #words for mice

    #cage and location information
    cage_id=Column(Integer,ForeignKey('cage.id')) #the cage card number

    #sex=Column(String,ForeignKey('sex.id'),nullable=False)
    sex=Column(String,nullable=False)
    ForeignKeyConstraint('Mouse.sex',['sex.name','sex.symbol','sex.abbrev'])
    #relationship('Breeder',primaryjoin='',backref=backref())
    genotype=Column(String) #use the numbers that jax uses????
    strain_id=Column(String,ForeignKey('strain.id')) #FIXME populating the strain ID probably won't be done in table? but can set rules that force it to match the parents, use a query, or a match or a condition on a join to prevent accidents? well, mouse strains could change via mute

    #geology
    litter_id=Column(Integer, ForeignKey('litter.id')) #mice dont HAVE to have litters
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire')) #FIXME test the sire_id=0 hack may not work on all schemas?
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam'))


    #dates and times
    dob_id=Column(Integer, ForeignKey('dob.id'),nullable=False) #backref FIXME data integrity problem, dob_id and litter.dob_id may not match if entered manually...
    dod=Column(DateTime)

    #breeding records
    breedingRec=relationship('Breeder',primaryjoin='Mouse.id==Breeder.id',backref=backref('mouse',uselist=False),uselist=False)

    #things that not all mice will have but that are needed for data to work out
    experiments=relationship('Experiment',backref='mouse')
    slices=relationship('Slice',backref=backref('mouse',uselist=False))
    cells=relationship('Cell',backref=backref('mouse',uselist=False))


    def __init__(self,Litter=None, litter_id=None,sire_id=None,dam_id=None, dob_id=None,DOB=None, eartag=None,tattoo=None,num=None,name=None, sex=None,genotype=None,strain_id=None, cage_id=None, dod=None, notes=[]):
        self.notes=notes

        self.eartag=eartag
        self.tattoo=tattoo
        self.num=num
        self.name=name

        self.cage_id=cage_id

        self.sex=sex
        self.genotype=genotype #FIXME this is a bit more complicated :/ needs +/- etc
        self.strain_id=strain_id

        self.litter_id=litter_id
        self.sire_id=sire_id
        self.dam_id=dam_id

        self.dob_id=dob_id  #FIXME there seems to be an evetuality where litter.dob_id and mouse.dob_id don't match... that won't be actively caught on insert
        self.dod=dod

        #autofill the ids from a parent object
        if Litter:
            if Litter.id:
                self.litter_id=Litter.id
                self.sire_id=Litter.sire_id
                self.dam_id=Litter.dam_id
                self.dob_id=Litter.dob_id
                #self.genotype=Litter.sire.mouse.genotype+Litter.dam.mouse.genotype
                if Litter.cage_id:
                    self.cage_id=Litter.cage_id
            else:
                raise AttributeError('Litter has no id! Did you commit before referencing the instance directly?')
        elif DOB:
            if DOB.id:
                self.dob_id=DOB.id
            else:
                raise AttributeError('DOB has no id! Did you commit before referencing the instance directly?')
    
    def __repr__(self):
        base=super().__repr__()
        try:
            litter=self.litter.strHelper(1)
        except:
            litter='\n\tLitter None'
        try:
            breedingRec=self.breedingRec.strHelper(1)
        except:
            breedingRec='\n\tBreedingRec None'

        return base+'%s %s %s'%(self.dob.strHelper(1),litter,breedingRec)


class Breeder(HasNotes, Base):
    id=Column(Integer,ForeignKey('mouse.id'),primary_key=True,autoincrement=False)
    #sex=Column(String,ForeignKey('sex.id'),nullable=False) #FIXME ah balls, didn't workout...
    sex=Column(String,nullable=False) #FIXME ah balls, didn't workout...
    ForeignKeyConstraint('Breeder.sex',['SEX.name','SEX.abbrev','SEX.symbol'])

    __mapper_args__ = {
        'polymorphic_on':sex,
        'polymorphic_identity':'breeder',
        'with_polymorphic':'*'
    }

    def __init__(self,id=None,Mouse=None,sex=None,notes=[]):
        self.notes=notes
        self.id=id
        self.sex=sex
        if Mouse:
            if Mouse.id:
                self.id=Mouse.id
                self.sex=Mouse.sex
            else:
                raise AttributeError('Mouse has no id! Did you commit before referencing the instance directly?')

    def strHelper(self,depth=0):
        base=super().strHelper(depth,'id')
        return base+'%s'%(self.mouse.strHelper(depth+1))

    def __repr__(self):
        base=super().__repr__('id')
        return base+'%s %s %s\n'%(self.mouse.strHelper(1),''.join([mr.strHelper(1) for mr in self.matingRecords]),''.join([lit.strHelper(1) for lit in self.litters]))


class Sire(Breeder):
    #__tablename__=None #used to force single table inheritance, note: exclude_properties is not needed here
    id=Column(Integer,ForeignKey('breeder.id'),primary_key=True,autoincrement=False)
    #sex=Column(String,nullable=False) #FIXME ah balls, didn't workout...
    #CheckConstraint() #FIXME god damn it this won't work the way I have my sex table set up... I need two constraints there... and so will have to split out male and female >_<

    matingRecords=relationship('MatingRecord',backref='sire')
    litters=relationship('Litter',backref='sire')
    offspring=relationship('Mouse',primaryjoin='Sire.id < foreign(Mouse.id)',backref=backref('sire',uselist=False),viewonly=True)

    __mapper_args__ = {'polymorphic_identity':'m'}


class Dam(Breeder):
    #__tablename__=None #used to force single table inheritance, note: exclude_properties is not needed here #turns out STI is good in one dir, but for other constraints it sucks :/
    id=Column(Integer,ForeignKey('breeder.id'),primary_key=True,autoincrement=False)

    matingRecords=relationship('MatingRecord',backref='dam')
    litters=relationship('Litter',backref='dam')
    offspring=relationship('Mouse',primaryjoin='Dam.id < foreign(Mouse.id)',backref=backref('dam',uselist=False),viewonly=True)

    __mapper_args__ = {'polymorphic_identity':'f'}


class MatingRecord(HasNotes, Base):
    id=Column(Integer,autoincrement=True) #WTF?! getting erros from this due to having it set as a primary key?!?!?
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire'),primary_key=True) #backref
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam'),primary_key=True) #backref
    startDateTime=Column(DateTime,nullable=False)#,primary_key=True) #FIXME fucking strings
    stopTime=Column(DateTime)
    est_e0=Column(DateTime) #FIXME this shit will error
    e0_err=Column(Float(53))

    @property
    def e0_err(self):
        return (self.stopTime-self.startDateTime)/2
    @e0_err.setter
    def e0_err(self):
        raise AttributeError('readonly attribute, set a stopTime if you want this')
        
    @property
    def est_e0(self):
        return self.startDateTime+self.e0_err #standard: sticks this right in the middle of the interval
    @est_e0.setter
    def est_e0(self):
        raise AttributeError('readonly attribute, set a stopTime if you want this')
    
    dob_id=Column(Integer,ForeignKey('dob.id'))
    
    litter=relationship('Litter',primaryjoin='and_(MatingRecord.sire_id==foreign(Litter.sire_id),MatingRecord.dam_id==foreign(Litter.dam_id),MatingRecord.dob_id==foreign(Litter.dob_id))',uselist=False,backref=backref('matingRecord',uselist=False))
    #litter=relationship('Litter',primaryjoin='and_(MatingRecord.sire_id==foreign(Litter.sire_id),MatingRecord.dam_id==foreign(Litter.dam_id),MatingRecord.startDateTime==foreign(Litter.mr_sdt))',uselist=False,backref=backref('matingRecord',uselist=False)) FIXME this is where the dates being strings is a problem, REALLY can't use them as primary keys :(
    
    def __init__(self,sire_id=None,Sire=None,dam_id=None,Dam=None,startDateTime=None,stopTime=None,notes=[]):
        self.notes=notes
        self.startDateTime=startDateTime
        self.stopTime=stopTime

        self.sire_id=sire_id
        self.dam_id=dam_id

        if Sire and Dam:
            if Sire.id and Dam.id:
                self.sire_id=Sire.id
                self.dam_id=Dam.id
            else:
                raise AttributeError('Sire or Dam has no id! Did you commit before referencing the instance directly?')
        elif Dam:
            if Dam.id:
                self.dam_id=Dam.id
            else:
                raise AttributeError('Dam has no id! Did you commit before referencing the instance directly?')

    def strHelper(self,depth=0):
        base=super().strHelper(depth,'est_e0')
        return base+'%s %s'%(self.sire.strHelper(depth+1),self.dam.strHelper(depth+1))

    def __repr__(self):
        base=super().__repr__('est_e0')
        try:
            litter='\n\tLitter %s %s'%(self.litter.id,self.litter.dob.strHelper(2))
        except:
            litter='\n\tLitter None'
        return base+'%s %s %s'%(self.sire.strHelper(1),self.dam.strHelper(1),litter)


class Litter(HasNotes, Base):
    #could to id=None here too...
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire'),nullable=False) #can have mice w/o litters, but no litters w/o mice
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam'),nullable=False)
    mr_id=Column(DateTime, ForeignKey('matingrecord.id'),unique=True) #FIXME could be the source?
    #mr_sdt=Column(DateTime, ForeignKey('matingrecord.startDateTime'),unique=True) #FIXME could be the source?
    dob_id=Column(Integer,ForeignKey('dob.id'),nullable=False)

    cage_id=Column(Integer, ForeignKey('cage.id'))


    name=Column(String) #the name by which I shall write upon their cage cards!

    #FIXME use @declared_attr to define size
    @property
    def size(self):
        return len(self.members.count)

            
    def make_members(self,number):
        """Method to generate new members of a given litter that can then be added to the database"""
        return [Mouse(Litter=self,sex='u') for i in range(number)]

    #FIXME generate these from a query/select on _mouse.litter_id==self.id??
    #pupps=Column(Integer) #aka total at first count
    #male=Column(Integer)
    #female=Column(Integer)
    #unknown=Column(Integer)

    #mUsed=Column(Integer)
    #fUsed=Column(Integer)
    #uUsed=Column(Integer)
    #FIXME those don't go here, I will enter a number in the interfacing program when a litter is counted and the offspring will be automatically updated

    members=relationship('Mouse',primaryjoin='Mouse.litter_id==Litter.id',backref=backref('litter',uselist=False)) #litter stores the members and starts out with ALL unknown each mouse has its own entry

    def __init__(self, mr_id=None, MatingRecord=None, sire_id=None, Sire=None, dam_id=None, Dam=None, dob_id=None, DOB=None, name=None, cage_id=None, notes=[]):
        self.notes=notes
        self.dob_id=dob_id
        self.name=name

        self.cage_id=cage_id

        #self.mr_sdt=mr_sdt
        self.mr_id=mr_id
        self.sire_id=sire_id
        self.dam_id=dam_id

        if DOB:
            if DOB.id:
                self.dob_id=DOB.id
            else:
                raise AttributeError('DOB has no id! Did you commit before referencing the instance directly?')

        if MatingRecord:
            if MatingRecord.startDateTime:
                #self.dob_id=MatingRecord.dob_id #FIXME
                #self.mr_sdt=MatingRecord.startDateTime #FIXME it may be more efficient to just have MR id's...? well... not really actually
                self.mr_id=MatingRecord.id
                self.dam_id=MatingRecord.dam_id
                self.sire_id=MatingRecord.sire_id
            else:
                raise AttributeError('MatingRecord has no id! Did you commit before referencing the instance directly?')
        elif Sire and Dam:
            if Sire.id and Dam.id:
                self.sire_id=Sire.id
                self.dam_id=Dam.id
            else:
                raise AttributeError('Sire or Dam has no id! Did you commit before referencing the instance directly?')
        elif Dam:
            if Dam.id:
                self.dam_id=Dam.id
            else:
                raise AttributeError('Dam has no id! Did you commit before referencing the instance directly?')
    

    def strHelper(self,depth=0):
        base=super().strHelper(depth)
        try:
            sire=self.sire.strHelper(depth+1)
        except:
            sire='\n\tSire Unknown'
        return base+'%s %s'%(sire,self.dam.strHelper(depth+1))

    def __repr__(self):
        base=super().__repr__()
        try:
            sire=self.sire.strHelper(depth+1)
        except:
            sire='\n\tSire Unknown'
        try:
            matingRecord='\n\tMatingRecord %s\n\t\tstartDateTime %s'%(self.matingRecord.id,frmtDT(self.matingRecord.startDateTime))
        except:
            matingRecord='\n\tMatingRecord None'
        return base+'%s %s %s'%(sire,self.dam.strHelper(1),matingRecord)


#experiment variables that are sub mouse, everything at and above the level of the mouse is also an experimental variable that I want to keep track of independently if possible
#this means that I MIGHT want to make them experimental variables so that I can automatically tag them with the experiment/s any one of them has been involved in? viewonly

###-------------------
###  Experiment tables
###-------------------

class ExperimentVariable(Base):
    pass


class Experiment(Base):
    experimenter_id=Column(Integer,ForeignKey('people.id')) #FIXME problmes with corrispondence
    mouse_id=Column(Integer,ForeignKey('mouse.id')) #this cannot be used as a primary key


class Amplifier(Base): #used for enforcing data integrity for cells
    __tablename__='amplifiers'
    id=None
    type=Column(String)
    serial=Column(Integer,primary_key=True) #this should be sufficient for everything I need
    headstages=relationship('Headstage',primaryjoin='Amplifier.serial==Headstage.amp_serial',backref=backref('amp',uselist=False))


class Headstage(HasNotes,Base): #used for enforcing data integrity for cells
    #using the id here because it actually requires fewer columns it seems? also adding the serial every time can be a bitch... need a way to double check to make sure though
    channel=Column(Integer,primary_key=True)
    amp_serial=Column(Integer,ForeignKey('amplifiers.serial'),primary_key=True)
    relationship('Cell',backref=backref('headstage',uselist=False))
    

class Slice(HasNotes, Base):
    id=None
    #id=Column(Integer,primary_key=True,autoincrement=False)
    mouse_id=Column(Integer,ForeignKey('mouse.id'),primary_key=True) #works with backref from mouse
    startDateTime=Column(DateTime,primary_key=True) #these two keys should be sufficient to ID a slice and I can use ORDER BY startDateTime and query(Slice).match(id=Mouse.id).count() :)
    #hemisphere
    #slice prep data can be querried from the mouse_id alone, since there usually arent two slice preps per mouse
    #positionAP

    cells=relationship('Cell',primaryjoin='Cell.slice_sdt==Slice.startDateTime',backref=backref('slice',uselist=False))


class Cell(HasNotes, Base):
    id=None
    mouse_id=Column(Integer,ForeignKey('mouse.id'),primary_key=True)
    slice_sdt=Column(Integer,ForeignKey('slice.startDateTime'),primary_key=True)
    hs_id=Column(Integer,ForeignKey('headstage.id'),primary_key=True)#,ForeignKey('headstages.id')) #FIXME critical
    #hs_id=Column(Integer,ForeignKey('headstage.channel'),primary_key=True)#,ForeignKey('headstages.id')) #FIXME critical
    #hs_amp_serial=Column(Integer,ForeignKey('headstage.amp_serial'),primary_key=True)#,ForeignKey('headstages.id')) #FIXME critical
    startDateTime=Column(DateTime,primary_key=True)

    #TODO abfFiles are going to be a many-many relationship here....
    abfFile_channel=None #FIXME this nd the headstage serials seems redundant but... wtf? I have to link them somehow

    breakInTime=None

    rheobase=None
    
    #analysis_id=None #put the analysis in another table that will backprop here


class SlicePrep(HasNotes, Base):
    """ Notes on the dissection and slice prep"""
    id=Column(Integer,ForeignKey('mouse.id'),primary_key=True) #works with backref from mouse
    #chamber_type
    #sucrose_id
    #sucrose reference to table of solutions

class SliceExperiment(HasNotes, Base):
    """Ideally this should be able to accomadate ALL the different kinds of slice experiment???"""
    #with abf files and stuff like that O_O
    #this is coterminus with abffile but keeping it separate will allow for other filetypes more easily

    acsf_id=Column(Integer,ForeignKey('solution.id'),nullable=False) #need to come up with a way to constrain
    #acsf_id #to prevent accidents split teh acsf and internal into different tables to allow for proper fk constraints? NO, not flexible enough
    #internal_id

    #pharmacology

    #abffile


class IUEP(HasNotes, Base):
    dam_id=Column(Integer,ForeignKey('dam.id'),nullable=False)
    dam=relationship('Dam',backref=('iuep'))

class ExperimentType(Base):
    #polymorphic type
    pass
    

###-------------
###  Datasources
###-------------

class AbfFile(HasNotes, Base):
    id=Column(String,primary_key=True) #filename without the extension FIXME this is a problem?
    #all the rigstate should just be put here?!?!? ya probably that makes the most sense
    sliceExperiemnt_id=Column(Integer,ForeignKey('sliceexperiment.id'))

###----------------------------
###  Populate Constraint tables
###----------------------------

def populateConstraints(session):
    #all names, prefixes, symbols, and Es from wikipedia
    #http://en.wikipedia.org/wiki/SI_base_unit
    #http://en.wikipedia.org/wiki/SI_derived_units
    #http://en.wikipedia.org/wiki/Units_accepted_for_use_with_SI

    #FIXME make auto unit conversions for DA?
    #FIXME need some way to implement sets of units? bugger
    SI_UNITS=(
        #name, symbol
        ('meter','m'),
        ('meters','m'),

        ('gram','g'), #and now I see why they have kg as the base...
        ('grams','g'),

        ('liter','L'),
        ('liters','L'),

        ('mole','mol'),
        ('moles','mol'),

        ('molarity','M'),
        ('molar','M'),
        ('molality','_m'), #FIXME
        ('molal','_m'), #FIXME

        ('kelvin','K'),

        ('degree Celcius','\u00B0C'), #degrees = U+00B0
        ('degrees Celcius','\u00B0C'),
        ('degree Celcius','~oC'), #Tom also accepts using the digraph for the degree symbol...
        ('degrees Celcius','~oC'),

        ('candela','ca'),
        ('candelas','ca'),

        ('lumen','lm'),
        ('lumens','lm'),

        ('lux','lx'),

        ('second','s'),
        ('seconds','s'),

        ('hertz','Hz'),

        ('minute','min'),
        ('minutes','min'),

        ('hour','h'),
        ('hours','h'),

        ('day','d'),
        ('days','d'),

        ('radian','rad'),
        ('radians','rad'),

        ('steradian','sr'),
        ('steradians','sr'),

        ('newton','N'),
        ('newtons','N'),

        ('pascal','Pa'),
        ('pascals','Pa'),

        ('joule','J'),
        ('joules','J'),

        ('watt','W'),
        ('watts','W'),

        ('ampere','A'),
        ('amperes','A'),
        ('amp','A'),
        ('amps','A'),

        ('coulomb','C'),
        ('coulombs','C'),

        ('volt','V'),
        ('volts','V'),

        ('farad','F'),
        ('farads','F'),

        ('ohm','\u03A9'), #unicode=U+03A9, this is upper case greek and should be used instead of 2126
        ('ohms','\u03A9'),

        ('ohm','R'), #R also accepted as per the note on wikipedia and some brit standard
        ('ohms','R'),

        ('siemens','S'),

        ('weber','Wb'),
        ('webers','Wb'),

        ('tesla','T'),
        ('teslas','T'),

        ('henry','H'),
        ('henrys','H'),


        ('becquerel','Bq'),
        ('becquerels','Bq'),

        ('gray','Gy'),
        ('grays','Gy'),

        ('sievert','Sv'),
        ('sieverts','Sv'),

        ('katal','kat'),
        ('katals','kat'),
        
        ('decibel','dB'),
        ('decibels','dB'),
    )
    NON_SI_UNITS=(
        #name, symbol
        ('osmole','Osm'), #total moles of solute contributing to osmotic pressure
        ('osmoles','Osm'),

        ('degree','\u00B0'), #unicode for the symbol is U+00B0
        ('degrees','\u00B0'),
        ('degree','~o'), #also accepted
        ('degrees','~o'),
    )
    SI_PREFIXES=(
                    #prefix, symbol, E
                    ('yotta','Y',24),
                    ('zetta','Z',21),
                    ('exa','E',18),
                    ('peta','P',15),
                    ('tera','T',12),
                    ('giga','G',9),
                    ('mega','M',6),
                    ('kilo','k',3),
                    ('hecto','h',2),
                    ('deca','da',1),
                    ('','',0),
                    ('deci','d',-1),
                    ('centi','c',-2),
                    ('milli','m',-3),
                    #('micro','\u03BC',-6,), #unicode=U+03BC  #FIXME terminal haveing problemms
                    ('micro','u',-6,), #also unoffically used
                    ('nano','n',-9),
                    ('pico','p',-12),
                    ('femto','f',-15),
                    ('atto','a',-18),
                    ('zepto','z',-21),
                    ('yocto','y',-24)
                )

    SEXES=(
            ('male','m','\u2642'), #U+2642
            ('female','f','\u2640'), #U+2640
            ('unknown','u','\u26AA'), #using unicode U+26AA for this
        )

    session.add_all([SI_PREFIX(prefix=prefix,symbol=symbol,E=E) for prefix,symbol,E in SI_PREFIXES])
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in SI_UNITS])
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in NON_SI_UNITS])
    session.add_all([SEX(name=name,abbrev=abbrev,symbol=symbol) for name,abbrev,symbol in SEXES])
    return session.commit()

###----------------------------------------------------------------
###  Helper classes/tables for mice (normalization and constraints)
###----------------------------------------------------------------

class SI_PREFIX(Base): #Yes, these are a good idea because they are written once, and infact I can enforce viewonly=True OR even have non-root users see those tables as read only
    id=None
    symbol=Column(String(2),primary_key=True)
    prefix=Column(String(5))
    E=Column(Integer)
    relationship('OneDData',backref('prefix')) #FIXME makesure this doesn't add a column!
    def __repr__(self):
        return '%s'%(self.symbol)
    

class SI_UNIT(Base):
    id=None
    symbol=Column(String(3),primary_key=True) #FIXME varchar may not work
    name=Column(String(15),primary_key=True) #this is also a pk so we can accept plurals :)
    #conversion??
    relationship('OneDData',backref('units')) #FIXME make sure this doen't add a column
    def __repr__(self):
        return '%s'%(self.symbol)

class SEX(Base):
    """Static table for sex"""
    id=None
    symbol=Column(String(1)) #the actual symbols
    name=Column(String(14),primary_key=True,autoincrement=False) #'male','female','unknown' #FIXME do I need the autoincrement 
    abbrev=Column(String(1)) #'m','f','u'

class Strain(Base): #TODO
    #FIXME class for strain IDs pair up with the shorthand names that I use and make sure mappings are one to one
    #will be VERY useful when converting for real things
    #FIXME: by reflection from jax??? probably not
    pass

###----------
###  Test it!
###----------

def makeObjects(session):
    import numpy as np
    sex_seed=np.random.choice(2,100,.52)
    base_sex=np.array(list('m'*100))
    sex_arr=base_sex[sex_seed==0]='f'
    
    #make some notes
    notes=map(str,range(50))


    urdob=DOB(datetime.strptime('0001-1-1 00:00:00','%Y-%m-%d %H:%M:%S'))
    session.add(urdob)
    session.commit()

    #make mice to be sires and dams
    session.add_all([Mouse(eartag=i+300,sex='f',DOB=urdob) for i in range(2)])
    session.add_all([Mouse(eartag=i+200,sex='m',DOB=urdob) for i in range(2)])
    session.commit()

    #session.add_all([[m.notes.append(note) for m in session.query(Mouse)] for note in notes]) #notes.append call should return m? fingers crossed FIXME

    session.add_all([Sire(Mouse=m) for m in session.query(Mouse).filter(200 <= Mouse.eartag, Mouse.eartag < 300)])
    session.add_all([Dam(Mouse=m) for m in session.query(Mouse).filter(300 <= Mouse.eartag, Mouse.eartag < 400)])
    session.commit()

    #make mating records and litters
    mrs=[]
    lits=[]
    n=10
    #make random pairings
    sires=[s for s in session.query(Sire)]
    dams=[d for d in session.query(Dam)]
    sire_arr=np.random.choice(len(sires),n)
    dam_arr=np.random.choice(len(sires),n)
    litter_sizes=np.random.randint(0,20,n) #randomize litter size
    for i in range (n):
        #pick sire and dam at random
        now=datetime.utcnow()
        mr=MatingRecord(Sire=sires[sire_arr[i]],Dam=dams[dam_arr[i]], startDateTime=now+timedelta(hours=i),stopTime=now+timedelta(hours=12))
        session.add(mr)
        session.commit()

        dob1=DOB(mr.est_e0+timedelta(days=19))
        session.add(dob1)
        session.commit() #FIXME this is where shit is seeming to break...
        printD(dob1.id)

        mr.dob_id=dob1.id
        session.add(mr)
        session.commit()
        printD(mr)

        lit=Litter(MatingRecord=mr,DOB=dob1) #FIXME there is a problem comparing datetimes because they are strings on they way back out >_<
        session.add(lit)
        session.commit()

        session.add_all(lit.make_members(litter_sizes[i]))
        session.commit()



def main():
    #SQLite does not check foreign key constraints by default so we have to turn it on every time we connect to the database
    #the way I have things written at the moment this is ok, but it is why inserting an id=0 has been working
    from time import sleep

    @event.listens_for(Engine, 'connect') #FIXME NOT WORKING!
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    #setup the engine
    echo=True
    #echo=False
    dbPath=':memory:'
    #dbPath='test2' #holy crap that is alow slower on the writes!
    engine = create_engine('sqlite:///%s'%(dbPath), echo=echo) #FIXME, check if the problems with datetime and DateTime on sqlite and sqlite3 modules are present!
    event.listen(engine,'connect',set_sqlite_pragma)

    #create metadata and session
    Base.metadata.create_all(engine)
    session = Session(engine)

    #populate constraint tables
    populateConstraints(session)

    #do some tests!

    makeObjects(session)


    """
    note1=Note(text='poop')
    note2=Note(text='poop2')
    note3=Note(text='poop3')
    note4=Note(text='poop4')
    note5=Note(text='poop5')
    note6=Note(text='dicks')
    #l1.notes=[Note('asdf note l1 test1')] #FIXME DANGEROUS WILL OVERWRITE
    #l2.notes(Note('testing note')) #FIXME this one doesnt work
    l1.notes.append(Note('wat'))
    l1.notes.append(note1)
    l1.notes.append(note6)
    mr1.notes.append(note1)
    m1.notes.append(note2)
    m1.notes.append(note3)
    m2.notes.append(note3)
    m2.notes.append(note5)
    session.add_all((mr1,m1,m2,l1,l2))
    session.commit()

    m3=Mouse(Litter=l1,num=0,sex='male',notes=[])
    m4=Mouse(Litter=l1,num=1,sex='female',notes=[])
    session.add_all((m3,m4))
    session.commit()
    """

    print('\n###***constraints***')
    [printD(c,'\n') for c in session.query(SI_PREFIX)]
    [printD(c,'\n') for c in session.query(SI_UNIT)]
    [printD(c,'\n') for c in session.query(SEX)]
    print('\n###***mice***')
    for mouse in session.query(Mouse):
        printD('\n',mouse)
    print('\n###***sires***')
    for s in session.query(Sire):
        printD('\n',s)
    print('\n###***dams***')
    for d in session.query(Dam):
        printD('\n',d)
    print('\n###***MatingRecords***')
    for mate in session.query(MatingRecord):
        printD('\n',mate)
    print('\n###***Litters***')
    for lit in session.query(Litter):
        printD('\n',lit)
    for note in session.query(Note):
        print('\n',note)

    #input('hit something to exit')
    
if __name__=='__main__':
    main()
