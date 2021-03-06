#source file contining the definitions for all the tables related to mouse management
#in theory since this now has the 'mice' namespace I could rename it to mouse.py and then do DOB organism breeder male_breeder female_breeder MatingRecord Litter

from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes
from database.standards import frmtDT

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

#repositories for data, locations for real things
#labbooks and citations for everything else

###----------------------
###  cages and cage racks #FIXME convert all of this to a hierarchical 'location' thingamabob
###----------------------

class CageRack(): #TODO this a 'collection'
    id=Column(Integer,primary_key=True)
    row=Column(Integer,primary_key=True,autoincrement=False)
    col=Column(String(1),primary_key=True,autoincrement=False)
    cage_id=Column(Integer,ForeignKey('cage.id'))


class Cage(): #TODO this is a 'unit'
    #the cool bit is that I can actually do all of these before hand if I print out my cage cards and get them prepped
    id=Column(Integer,primary_key=True, autoincrement=False) #cage card numbers
    location=relationship('CageRack',backref=backref('cage',uselist=False),uselist=False)
    mice=relationship('Mouse',primaryjoin='Mouse.cage_id==Cage.id',backref=backref('cage',uselist=False))
    #litter=relationship('Litter',primaryjoin='Litter.cage_id==Cage.id',backref=backref('cage',uselist=False))


class CageTransfer():
    #TODO this is a transaction record for when someone changes the cage_id on a mouse
    #or does a cage.mice.append(mouse) (im not even sure that actually works???)
    #FIXME this HAS to be implemented as an event trigger!!!!
    #triggers require actual sql see: http://docs.sqlalchemy.org/en/rel_0_8/core/ddl.html
    #TODO the versioned mixin may be more along the lines of what I want for this?
    id=Column(Integer,primary_key=True)
    dateTime=Column(DateTime, default=datetime.now)
    user_id=None
    action=None
    mouse_id=Column(Integer, ForeignKey('mouse.id'))
    old_cage_id=Column(Integer, ForeignKey('cage.id'))
    new_cage_id=Column(Integer, ForeignKey('cage.id'))


'''
###---------------------------------------------------------
###  Date of birth table for use with anything that needs it
###---------------------------------------------------------

class DOB(Base): #FIXME class DATETHING???  to keep all the dates with specific 
    """Clean way to propagate dobs to litters and mice"""
    id=Column(Integer,primary_key=True)
    dateTime=Column(DateTime,nullable=False) #on my core i7 4770k I get a mean of 1996 sdt of 329 calls of datetime.utcnow() with a unique timestamp, heavy rightward skew
    absolute_error=Column(Interval) #TODO read the doccumentation on this one to make sure it is ok
    #estimated=Column(DateTime) #transaction thingy for later

    #matingRecord=relationship('MatingRecord',primaryjoin='MatingRecord.dob_id==DOB.id',backref=backref('dob',uselist='False')) #FIXME need to force match litter/mr dob...
    #litter=relationship('Litter',primaryjoin='Litter.dob_id==DOB.id',backref=backref('dob',uselist=False)) #attempt to enforce one litter per DOB?
    mice=relationship('Mouse',primaryjoin='Mouse.dob_id==DOB.id',backref=backref('dob',uselist=False))

    def __init__(self,dateTime,absolute_error=None):
        self.dateTime=dateTime
        try:
            self.absolute_error=absolute_error #FIXME with interval, should be timedelta type
        except:
            self.absolute_error=None

    def strHelper(self,depth=0):
        tabs='\t'*depth
        return '\n%sDOB %s %s %s'%(tabs,frmtDT(self.dateTime),_plusMinus,self.absolute_error)
    def __repr__(self):
        return '\nDOB %s %s %s'%(frmtDT(self.dateTime),_plusMinus,self.absolute_error)


###----------------
###  Mouse breeding
###----------------

class Breeder(Base):
    id=Column(Integer,ForeignKey('mouse.id'),primary_key=True,autoincrement=False)
    sex_id=Column(String(1),ForeignKey('sex.abbrev'),nullable=False) #FIXME ah balls, didn't workout...

    __mapper_args__ = {
        'polymorphic_on':sex_id,
        'polymorphic_identity':'breeder',
        'with_polymorphic':'*'
    }

    def __init__(self,Mouse=None,sex_id=None,notes=[]):
        self.notes=notes
        self.id=id
        self.sex_id=sex_id
        if Mouse:
            if Mouse.id:
                self.id=Mouse.id
                self.sex_id=Mouse.sex_id
            else:
                raise AttributeError('Mouse has no id! Did you commit before referencing the instance directly?')

    def strHelper(self,depth=0):
        base=super().strHelper(depth,'id')
        return base#+'%s'%(self.mouse.strHelper(depth+1))

    def __repr__(self):
        base=super().__repr__('id')
        #return base+'%s %s %s\n'%(self.mouse.strHelper(1),''.join([mr.strHelper(1) for mr in self.matingRecords]),''.join([lit.strHelper(1) for lit in self.litters]))
        return base+'%s %s\n'%(''.join([mr.strHelper(1) for mr in self.matingRecords]),''.join([lit.strHelper(1) for lit in self.litters]))


class Sire(Breeder):
    #__tablename__=None #used to force single table inheritance, note: exclude_properties is not needed here
    id=Column(Integer,ForeignKey('breeder.id'),primary_key=True,autoincrement=False)
    #sex=Column(String,nullable=False) #FIXME ah balls, didn't workout...
    #CheckConstraint() #FIXME god damn it this won't work the way I have my sex table set up... I need two constraints there... and so will have to split out male and female >_<

    matingRecords=relationship('Experiment',backref='sire')
    litters=relationship('Litter',backref='sire')
    offspring=relationship('Mouse',primaryjoin='Sire.id < foreign(Mouse.id)',backref=backref('sire',uselist=False),viewonly=True)

    __mapper_args__ = {'polymorphic_identity':'m'}


class Dam(Breeder):
    #__tablename__=None #used to force single table inheritance, note: exclude_properties is not needed here #turns out STI is good in one dir, but for other constraints it sucks :/
    id=Column(Integer,ForeignKey('breeder.id'),primary_key=True,autoincrement=False)

    matingRecords=relationship('Experiment',backref='dam')
    litters=relationship('Litter',backref='dam')
    offspring=relationship('Mouse',primaryjoin='Dam.id < foreign(Mouse.id)',backref=backref('dam',uselist=False),viewonly=True)

    __mapper_args__ = {'polymorphic_identity':'f'}


class MatingRecord(Base): #XXX DEPRICATED
    id=Column(Integer,primary_key=True)
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire'))
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam'))
    startDateTime=Column(DateTime,nullable=False)
    stopDateTime=Column(DateTime)
    e0_err=Column(Interval) #FIXME test this!
    est_e0=Column(DateTime) #FIXME this shit will error

    @hybrid_property #FIXME http://docs.sqlalchemy.org/en/rel_0_8/orm/extensions/hybrid.html
    def e0_err(self):
        return (self.stopDateTime-self.startDateTime)/2
        
    @hybrid_property
    def est_e0(self):
        return self.startDateTime+self.e0_err #standard: sticks this right in the middle of the interval

    dob_id=Column(Integer,ForeignKey('dob.id')) #FIXME the foreing key missmatch I get on update is cause by... what? check for referencing a table that does not exist
    
    litter=relationship('Litter',primaryjoin='and_(MatingRecord.id==foreign(Litter.mr_id),MatingRecord.sire_id==foreign(Litter.sire_id),MatingRecord.dam_id==foreign(Litter.dam_id),MatingRecord.dob_id==foreign(Litter.dob_id))',uselist=False,backref=backref('matingRecord',uselist=False))
    
    def __init__(self,sire_id=None,Sire=None,dam_id=None,Dam=None,startDateTime=None,stopDateTime=None,notes=[]):
        self.notes=notes
        self.startDateTime=startDateTime
        self.stopDateTime=stopDateTime

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
        return base+'%s %s\n\tstartDateTime %s %s'%(self.sire.strHelper(1),self.dam.strHelper(1),self.startDateTime,litter)


class Litter(Base): #FIXME replace with NameSubjectGroup or something #XXX DEPRICATED
    id=Column(Integer,primary_key=True)
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire'),nullable=False) #can have mice w/o litters, but no litters w/o mice
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam'),nullable=False)
    mr_id=Column(Integer, ForeignKey('matingrecord.id'),unique=True)
    dob_id=Column(Integer,ForeignKey('dob.id'),nullable=False)

    cage_id=Column(Integer, ForeignKey('cage.id'))

    name=Column(String(20)) #the name by which I shall write upon their cage cards!

    @property
    def size(self):
        return len(self.members)
    @property #you get the idea
    def males(self):
        return sum([m.sex_id=='m' for m in self.members])
    @property #you get the idea
    def females(self):
        return sum([m.sex_id=='f' for m in self.members])
    @property #you get the idea
    def unknowns(self):
        return sum([m.sex_id=='u' for m in self.members])

    @property
    def m_left(self):
        return sum([m.sex_id=='m' and m.dod==None for m in self.members])
    @property
    def f_left(self):
        return sum([m.sex_id=='f' and m.dod==None for m in self.members])
    @property
    def u_left(self):
        return sum([m.sex_id=='u' and m.dod==None for m in self.members])

    members=relationship('Mouse',primaryjoin='Mouse.litter_id==Litter.id',backref=backref('litter',uselist=False)) #litter stores the members and starts out with ALL unknown each mouse has its own entry

    def make_members(self,number):
        """Method to generate new members of a given litter that can then be added to the database

        DEPRICATED
        USE: Litter.members.extend([Mouse(Litter=self,sex_id='u') for i in range(number)])

        """
        pass

    def __init__(self, MatingRecord=None, mr_id=None, Sire=None, Dam=None, DOB=None, sire_id=None, dam_id=None, dob_id=None, name=None, cage_id=None, notes=[]):
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
        return base+'%s %s %s %s\n\tSize %s'%(sire,self.dam.strHelper(1),self.dob.strHelper(1),matingRecord,self.size)
'''
