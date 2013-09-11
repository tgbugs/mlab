#source file contining the definitions for all the tables related to mouse management
#in theory since this now has the 'mice' namespace I could rename it to mouse.py and then do DOB organism breeder male_breeder female_breeder MatingRecord Litter

from database.imports import *
from sqlalchemy                         import Float
from sqlalchemy                         import ForeignKeyConstraint

from sqlalchemy.ext.declarative         import declared_attr #main mice notes

from database.dateTimeFuncs import *

from database.base import Base, HasNotes
#from notes import HasNotes

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

###----------------------
###  cages and cage racks
###----------------------

class CageRack(Base): #TODO this a 'collection'
    id=Column(Integer,primary_key=True)
    row=Column(Integer,primary_key=True,autoincrement=False)
    col=Column(String,primary_key=True,autoincrement=False)
    cage_id=Column(Integer,ForeignKey('cage.id'))


class Cage(Base): #TODO this is a 'unit'
    #the cool bit is that I can actually do all of these before hand if I print out my cage cards and get them prepped
    id=Column(Integer,primary_key=True, autoincrement=False) #cage card numbers
    location=relationship('CageRack',backref=backref('cage',uselist=False),uselist=False)
    mice=relationship('Mouse',primaryjoin='Mouse.cage_id==Cage.id',backref=backref('cage',uselist=False))
    litter=relationship('Litter',primaryjoin='Litter.cage_id==Cage.id',backref=backref('cage',uselist=False))


###-----------------------------------------------------
###  MOUSE Defintions for mouse tables and relationships TODO this datamodel could be replicated for pretty much any model organism?
###-----------------------------------------------------

class DOB(Base): #FIXME class DATETHING???  to keep all the dates with specific 
    """Clean way to propagate dobs to litters and mice"""
    dateTime=Column(DateTime,nullable=False) #on my core i7 4770k I get a mean of 1996 sdt of 329 calls of datetime.utcnow() with a unique timestamp, heavy rightward skew
    absolute_error=Column(Float(precision=53)) #note: it is safe to store any timedelta less than a couple of years and still retain microseconds at full precision
    #estimated=Column(DateTime) #transaction thingy for later

    printD('I get here')
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
        return '\n%sDOB %s %s %s'%(tabs,frmtDT(self.dateTime),_plusMinus,self.absolute_error)
    def __repr__(self):
        return '\nDOB %s %s %s'%(frmtDT(self.dateTime),_plusMinus,self.absolute_error)


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


class Breeder(Base):
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
        return base#+'%s'%(self.mouse.strHelper(depth+1))

    def __repr__(self):
        base=super().__repr__('id')
        #return base+'%s %s %s\n'%(self.mouse.strHelper(1),''.join([mr.strHelper(1) for mr in self.matingRecords]),''.join([lit.strHelper(1) for lit in self.litters]))
        return base+'%s %s\n'%(''.join([mr.strHelper(1) for mr in self.matingRecords]),''.join([lit.strHelper(1) for lit in self.litters]))


class Sire(HasNotes, Breeder):
    #__tablename__=None #used to force single table inheritance, note: exclude_properties is not needed here
    id=Column(Integer,ForeignKey('breeder.id'),primary_key=True,autoincrement=False)
    #sex=Column(String,nullable=False) #FIXME ah balls, didn't workout...
    #CheckConstraint() #FIXME god damn it this won't work the way I have my sex table set up... I need two constraints there... and so will have to split out male and female >_<

    matingRecords=relationship('MatingRecord',backref='sire')
    litters=relationship('Litter',backref='sire')
    offspring=relationship('Mouse',primaryjoin='Sire.id < foreign(Mouse.id)',backref=backref('sire',uselist=False),viewonly=True)

    __mapper_args__ = {'polymorphic_identity':'m'}


class Dam(HasNotes, Breeder):
    #__tablename__=None #used to force single table inheritance, note: exclude_properties is not needed here #turns out STI is good in one dir, but for other constraints it sucks :/
    id=Column(Integer,ForeignKey('breeder.id'),primary_key=True,autoincrement=False)

    matingRecords=relationship('MatingRecord',backref='dam')
    litters=relationship('Litter',backref='dam')
    offspring=relationship('Mouse',primaryjoin='Dam.id < foreign(Mouse.id)',backref=backref('dam',uselist=False),viewonly=True)

    __mapper_args__ = {'polymorphic_identity':'f'}


class MatingRecord(HasNotes, Base):
    id=Column(Integer,primary_key=True)#,unique=True) #THIS MUST BE UNIQUIE DUHHHH #FIXME wierd stuff be here!??!
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire'))#,primary_key=True) #backref
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam'))#,primary_key=True) #backref
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
    
    dob_id=Column(Integer,ForeignKey('dob.id')) #FIXME the foreing key missmatch I get on update is cause by... what? check for referencing a table that does not exist
    
    litter=relationship('Litter',primaryjoin='and_(MatingRecord.id==foreign(Litter.mr_id),MatingRecord.sire_id==foreign(Litter.sire_id),MatingRecord.dam_id==foreign(Litter.dam_id),MatingRecord.dob_id==foreign(Litter.dob_id))',uselist=False,backref=backref('matingRecord',uselist=False))
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
    mr_id=Column(Integer, ForeignKey('matingrecord.id'),unique=True) #could be the source? YEP IT WAS
    #mr_sdt=Column(DateTime, ForeignKey('matingrecord.startDateTime'),unique=True) #FIXME could be the source?
    dob_id=Column(Integer,ForeignKey('dob.id'),nullable=False)

    cage_id=Column(Integer, ForeignKey('cage.id'))


    name=Column(String) #the name by which I shall write upon their cage cards!

    #FIXME use @declared_attr to define size, do not need a column for that...
    @property
    def size(self):
        return len(self.members.count)
    @property #you get the idea
    def males(self):
        return len(self.members.male.count)
    

            
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
                self.dob_id=MatingRecord.dob_id #FIXME
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
            raise
            sire='\n\tSire Unknown'
        return base+'%s %s'%(sire,self.dam.strHelper(depth+1))

    def __repr__(self):
        base=super().__repr__()
        try:
            sire=self.sire.strHelper(1)
        except:
            sire='\n\tSire Unknown'
        try:
            matingRecord='\n\tMatingRecord %s\n\t\tstartDateTime %s'%(self.matingRecord.id,frmtDT(self.matingRecord.startDateTime))
        except:
            matingRecord='\n\tMatingRecord None'
        return base+'%s %s %s'%(sire,self.dam.strHelper(1),matingRecord)

