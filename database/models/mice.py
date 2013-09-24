#source file contining the definitions for all the tables related to mouse management
#in theory since this now has the 'mice' namespace I could rename it to mouse.py and then do DOB organism breeder male_breeder female_breeder MatingRecord Litter


from database.imports import *
from database.base import Base
from database.mixins import HasNotes, HasMetaData, HasDataFiles
from database.standards import frmtDT, timeDeltaIO
from sqlalchemy.orm import mapper

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

###----------------------
###  cages and cage racks
###----------------------

class CageRack(Base): #TODO this a 'collection'
    id=Column(Integer,primary_key=True)
    row=Column(Integer,primary_key=True,autoincrement=False)
    col=Column(String(1),primary_key=True,autoincrement=False)
    cage_id=Column(Integer,ForeignKey('cage.id'))


class Cage(Base): #TODO this is a 'unit'
    #the cool bit is that I can actually do all of these before hand if I print out my cage cards and get them prepped
    id=Column(Integer,primary_key=True, autoincrement=False) #cage card numbers
    location=relationship('CageRack',backref=backref('cage',uselist=False),uselist=False)
    mice=relationship('Mouse',primaryjoin='Mouse.cage_id==Cage.id',backref=backref('cage',uselist=False))
    litter=relationship('Litter',primaryjoin='Litter.cage_id==Cage.id',backref=backref('cage',uselist=False))


class CageTransfer(Base):
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


###-----------------------------------------------------
###  MOUSE Defintions for mouse tables and relationships TODO this datamodel could be replicated for pretty much any model organism?
###-----------------------------------------------------

class DOB(Base): #FIXME class DATETHING???  to keep all the dates with specific 
    """Clean way to propagate dobs to litters and mice"""
    dateTime=Column(DateTime,nullable=False) #on my core i7 4770k I get a mean of 1996 sdt of 329 calls of datetime.utcnow() with a unique timestamp, heavy rightward skew
    absolute_error=Column(Interval) #TODO read the doccumentation on this one to make sure it is ok
    #estimated=Column(DateTime) #transaction thingy for later

    matingRecord=relationship('MatingRecord',primaryjoin='MatingRecord.dob_id==DOB.id',backref=backref('dob',uselist='False')) #FIXME need to force match litter/mr dob...
    litter=relationship('Litter',primaryjoin='Litter.dob_id==DOB.id',backref=backref('dob',uselist=False)) #attempt to enforce one litter per DOB?
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

###-----------------------
###  Subjects
###-----------------------

class Subject(Base):
    __tablename__='subjects'
    id=Column(Integer,primary_key=True)
    type=Column(String,nullable=False)
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'subject',
    }

class Mouse(HasMetaData, HasNotes, Subject): #TODO species metadata???
    #in addition to the id, keep track of some of the real world ways people refer to mice!
    __tablename__='mouse'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)
    eartag=Column(Integer)
    tattoo=Column(Integer)
    num_in_lit=Column(Integer)  #for mice with no eartag or tattoo, numbered in litter, might replace this with mouse ID proper?
    name=Column(String(20))  #words for mice

    #cage and location information
    cage_id=Column(Integer,ForeignKey('cage.id')) #the cage card number

    sex_id=Column(String(1),ForeignKey('sex.abbrev'),nullable=False)
    #relationship('Breeder',primaryjoin='',backref=backref())
    genotype_id=Column(Integer) #TODO this should really be metadata, but how to constrain those metadata fields based on strain data?
    strain_id=Column(Integer,ForeignKey('strain.id')) #FIXME populating the strain ID probably won't be done in table? but can set rules that force it to match the parents, use a query, or a match or a condition on a join to prevent accidents? well, mouse strains could change via mute TODO

    #geology
    litter_id=Column(Integer, ForeignKey('litter.id')) #mice dont HAVE to have litters
    #FIXME there may be a way to get these from litter_id???
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire')) #FIXME test the sire_id=0 hack may not work on all schemas?
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam')) #FIXME delete these, they are not used anymore

    __mapper_args__ = {'polymorphic_identity':'mouse'}

    #dates and times
    dob_id=Column(Integer, ForeignKey('dob.id'),nullable=False) #backref FIXME data integrity problem, dob_id and litter.dob_id may not match if entered manually...
    @hybrid_property #TODO
    def age(self):
        if self.dod:
            return self.dod-self.dob.dateTime
        else:
            return datetime.now()-self.dob.dateTime #FIXME
        
    dod=Column(DateTime) #FIXME need to figure out how to directly link this to experiments eg, a setter for dod would just get current datetime and make the mouse dead instead of calling a completely separate killMouse method

    #breeding records
    breedingRec=relationship('Breeder',primaryjoin='Mouse.id==Breeder.id',backref=backref('mouse',uselist=False),uselist=False)

    #experiments
    #experiment_id=Column(Integer,ForeignKey('experiments.id'),unique=True) #FIXME m-m

    #things that not all mice will have but that are needed for data to work out
    slices=relationship('Slice',backref=backref('mouse',uselist=False))
    cells=relationship('Cell',primaryjoin='Cell.mouse_id==Mouse.id',backref=backref('mouse',uselist=False))


    def __init__(self,Litter=None, litter_id=None,sire_id=None,dam_id=None, dob_id=None,DOB=None, eartag=None,tattoo=None,num=None,name=None, sex_id=None,genotype=None,strain_id=None, cage_id=None, dod=None, notes=[]):
        self.notes=notes

        self.eartag=eartag
        self.tattoo=tattoo
        self.num=num
        self.name=name

        self.cage_id=cage_id

        self.sex_id=sex_id
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


class Slice(HasMetaData, HasNotes, Base):
    id=None
    id=Column(Integer,primary_key=True) #FIXME
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False)#,primary_key=True) #works with backref from mouse
    prep_id=Column(Integer,ForeignKey('experiments.id'),nullable=False) #TODO this should really refer to slice prep, but suggests that this class should be 'acute slice'
    prep=relationship('Experiment',primaryjoin='Experiment.id==Slice.prep_id',backref=backref('slices',uselist=True))
    #TODO check that there are not more slices than the thickness (from the metadta) divided by the total length of the largest know mouse brain
    startDateTime=Column(DateTime,default=datetime.now)#,primary_key=True) #these two keys should be sufficient to ID a slice and I can use ORDER BY startDateTime and query(Slice).match(id=Mouse.id).count() :)
    #hemisphere
    #slice prep data can be querried from the mouse_id alone, since there usually arent two slice preps per mouse
    #FIXME why the fuck is thickness metadata... it is linked to protocol and slice prep... ah, I guess it is sliceprep metadata that sort of needs to propagate

    cells=relationship('PatchCell',primaryjoin='PatchCell.slice_id==Slice.id',backref=backref('slice',uselist=False))

    def __init__(self,Prep=None,Mouse=None,mouse_id=None,prep_id=None,startDateTime=None):
        self.startDateTime=startDateTime
        self.mouse_id=mouse_id
        self.prep_id=prep_id

        #self.AssignID(Mouse)
        #self.AssignID(Prep)

        if Prep:
            if Prep.id:
                self.prep_id=Prep.id
            else:
                raise AttributeError
            if Prep.subjects:
                self.mouse_id=Prep.subjects[0].id
            else:
                raise AttributeError('your sliceprep has no mouse!')
        elif Mouse:
            if Mouse.id:
                self.mouse_id=Mouse.id
            else:
                raise AttributeError
    def strHelper(self,depth=0):
        return super().strHelper(depth)


''' replaced by cells to datafile table it's simpler and has same data
class CellPairs(Base): #FIXME cell tupels?!??!
    #FIXME should THIS have datafiles instead??@??@
    #YES yes eys eys eys ey sy
    __tablename__='cell_to_cell'
    id=None
    cell_1_id=Column(Integer,ForeignKey('cell.id'),primary_key=True)
    cell_2_id=Column(Integer,ForeignKey('cell.id'),primary_key=True)
    def __init__(self,Cell_1=None,Cell_2=None,cell_1_id=None,cell_2_id=None):
        self.cell_1_id=cell_1_id
        self.cell_2_id=cell_2_id
        if Cell_1:
            if Cell_1.id:
                self.cell_1_id=Cell_1.id
            else:
                raise AttributeError
        if Cell_2:
            if Cell_2.id:
                self.cell_2_id=Cell_2.id
            else:
                raise AttributeError
    def __repr__(self):
        return '%s %s'%(self.cell_1_id,self.cell_2_id)

    #TODO FIXME so maybe this shouldn't be explicit here, it should be in the metadata linking cells to datafile channels????
'''

class Cell(Subject):
    __tablename__='cell'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False) #FIXME
    #FIXME overlap between experiment type and cell type, confusing
    #exp_type=Column(String,nullable=False)
    __mapper_args__={
        #'polymorphic_on':exp_type,
        'polymorphic_identity':'cell'}


class PatchCell(HasDataFiles, HasMetaData, HasNotes, Cell):
    __tablename__='patchcell'
    #link to subject
    id=Column(Integer,ForeignKey('cell.id'),primary_key=True,autoincrement=False)
    patch_id=Column(Integer,ForeignKey('experiments.id'),nullable=False) #FIXME this should be Patch ?? but.. but.. but.. also that unique constraint... #check experiment.prep_id == slice.prep_id
    slice_id=Column(Integer,ForeignKey('slice.id'),nullable=False)
    #FIXME check that experiment_id.sliceprep.slices contains slice_id

    #link to data
    #FIXME link to data seems like it is going to be via metadata :/
    hs_id=Column(Integer,ForeignKey('hardware.id'),nullable=False) #TODO use this when creating datafile metadata?!
    startDateTime=Column(DateTime,default=datetime.now)
    __mapper_args__={'polymorphic_identity':'patch cell'}

    #these should probably go in metadata which can be configged per experiment
    #wholeCell=None
    #loosePatch=None


    #TODO abfFiles are going to be a many-many relationship here....
    #abfFile_channel=None #FIXME this nd the headstage serials seems redundant but... wtf? I have to link them somehow

    breakInTime=None

    rheobase=None

    #headstage=relationship('Hardware',primaryjoin='Cell.hs_id==Hardware.id')

    #NOTE: this table is now CRITICAL for maintaining a record of who was patched with whom
    #_cell_2=relationship('Cell', #FIXME I should only need ONE ROW for this
                        #secondary='cell_to_cell',
                        #primaryjoin='Cell.id==CellPairs.cell_1_id',
                        #secondaryjoin='Cell.id==CellPairs.cell_2_id',
                        #backref=backref('_cell_1'),
                      #)
    @hybrid_property #FIXME shouldn't his just be a property?
    def cells(self):
        #return self._cell_1+self._cell_2
        return self.datafiles.cell
    def __init__(self,Slice=None,Experiment=None,Headstage=None,slice_id=None,mouse_id=None,experiment_id=None,hs_id=None,startDateTime=None):
        self.startDateTime=startDateTime
        self.slice_id=slice_id
        self.mouse_id=mouse_id
        self.experiment_id=experiment_id
        self.hs_id=hs_id
        if Slice:
            if Slice.id:
                self.slice_id=Slice.id
                self.mouse_id=Slice.mouse_id
            else:
                raise AttributeError
        if Patch:
            if Patch.id:
                self.patch_id=Patch.id
        if Headstage:
            if Headstage.id:
                self.hs_id=Headstage.id
            else:
                raise AttributeError
    #def strHelper(self,depth=0):
        #base=super().strHelper(depth)
    def __repr__(self):
        base=super().__repr__()
        return '%s%s%s%s'%(base,self.headstage.strHelper(1),self.slice.strHelper(1),''.join([c.strHelper(1) for c in self.cells]))
    
    #TODO analysis should probably reference the objects not the other way around



###----------------
###  Mouse breeding
###----------------

class Breeder(Base):
    id=Column(Integer,ForeignKey('mouse.id'),primary_key=True,autoincrement=False)
    #sex=Column(String,ForeignKey('sex.id'),nullable=False) #FIXME ah balls, didn't workout...
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
    @e0_err.setter
    def e0_err(self):
        raise AttributeError('readonly attribute, set a stopTime if you want this')
        
    @hybrid_property
    def est_e0(self):
        return self.startDateTime+self.e0_err #standard: sticks this right in the middle of the interval
    @est_e0.setter
    def est_e0(self):
        raise AttributeError('readonly attribute, set a stopTime if you want this')

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
        return base+'%s %s %s'%(self.sire.strHelper(1),self.dam.strHelper(1),litter)


class Litter(HasNotes, Base):
    sire_id=Column(Integer, ForeignKey('sire.id',use_alter=True,name='fk_sire'),nullable=False) #can have mice w/o litters, but no litters w/o mice
    dam_id=Column(Integer, ForeignKey('dam.id',use_alter=True,name='fk_dam'),nullable=False)
    mr_id=Column(Integer, ForeignKey('matingrecord.id'),unique=True)
    dob_id=Column(Integer,ForeignKey('dob.id'),nullable=False)

    cage_id=Column(Integer, ForeignKey('cage.id'))

    name=Column(String(20)) #the name by which I shall write upon their cage cards!

    #FIXME use @declared_attr to define size, do not need a column for that...
    #FIXME may need queries for this? ;_;
    @property
    def size(self):
        return self.members.count()
    @property #you get the idea
    def males(self):
        return self.members.filter(Mouse.sex_id=='m').count()
    @property #you get the idea
    def females(self):
        return self.members.filter(Mouse.sex_id=='f').count()
    @property #you get the idea
    def unknowns(self):
        return self.members.filter(Mouse.sex_id=='u').count()

    #TODO verify that 'remaining males' and 'remaning females' won't accidentally be negative, I think the way I have it now works best, actual records for mice instead of just numbers could use an assert in python or maybe a check? nah
    
    @property
    def m_left(self):
        return self.members.filter(Mouse.sex_id=='m',Mouse.dod==None).count()

    @property
    def u_left(self):
        return self.members.filter(Mouse.sex_id=='f',Mouse.dod==None).count()

    @property
    def u_left(self):
        return self.members.filter(Mouse.sex_id=='u',Mouse.dod==None).count()

            

    members=relationship('Mouse',primaryjoin='Mouse.litter_id==Litter.id',backref=backref('litter',uselist=False)) #litter stores the members and starts out with ALL unknown each mouse has its own entry

    def make_members(self,number):
        """Method to generate new members of a given litter that can then be added to the database"""
        return [Mouse(Litter=self,sex_id='u') for i in range(number)]

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
        return base+'%s %s %s'%(sire,self.dam.strHelper(1),matingRecord)

