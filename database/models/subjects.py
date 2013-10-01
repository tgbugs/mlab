from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasDataFiles, HasHardware
from database.standards import frmtDT

#an attempt to simplify the the relationship of objects to data

###-----------------------
###  Subjects
###-----------------------

class Subject(HasMetaData, HasDataFiles, HasHardware, HasNotes, Base): #FIXME should metadata all go here?
    __tablename__='subjects'
    id=Column(Integer,primary_key=True)
    type=Column(String,nullable=False)
    __mapper_args__ = {
        'polymorphic_on':type,
        'polymorphic_identity':'subject',
    }
    def __init__(self,Experiments=[],Hardware=[]):
        self.experiments.extend(Experiments)
        self.hardware.extend(Hardware)


class Mouse(Subject): #TODO species metadata???
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
    slices=relationship('Slice',primaryjoin='Slice.mouse_id==Mouse.id',backref=backref('mouse',uselist=False))
    cells=relationship('Cell',primaryjoin='Cell.mouse_id==Mouse.id',backref=backref('mouse',uselist=False))


    def __init__(self,Litter=None, litter_id=None,sire_id=None,dam_id=None, dob_id=None,DOB=None, eartag=None,tattoo=None,num=None,name=None, sex_id=None,genotype=None,strain_id=None, cage_id=None, dod=None, notes=[], Experiments=[]):
        super().__init__(Experiments)
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


class Slice(Subject): #FIXME slice should probably be a subject
    __tablename__='slice'
    #TODO experiments for slice prep might should also add these slices as their subjects? or should the slices get their data about the conditions they were generated under from the mouse?!?
    #well, mice don't refer directly to mating record... but litter's do...
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True) #FIXME
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False)#,primary_key=True) #works with backref from mouse
    #TODO check that there are not more slices than the thickness (from the metadta) divided by the total length of the largest know mouse brain
    startDateTime=Column(DateTime,default=datetime.now) #time onto rig rather than t cut
    #just like I don't store slice -> rig time in cell we dont store cut time in slice
    #HOWEVER we will need to store that in ExperimentMetaData
    #hemisphere
    #FIXME why the fuck is thickness metadata... it is linked to protocol and slice prep... ah, I guess it is sliceprep metadata that sort of needs to propagate
    @property
    def thickness(self):
        exp=self.experiments[0]
        emd=Experiment.MetaData
        return query(emd).filter(emd.experiment_id==exp.id,emd.datasource_id=='slice thickness') #ick this is nasty to get out and this isn't even correct

    cells=relationship('Cell',primaryjoin='Cell.slice_id==Slice.id',backref=backref('slice',uselist=False))

    __mapper_args__ = {'polymorphic_identity':'slice'}

    def __init__(self,Prep=None,Mouse=None,mouse_id=None,prep_id=None,startDateTime=None,Hardware=[], Experiments=[]):
        super().__init__(Experiments,Hardware)
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


class Cell(Subject):
    __tablename__='cell'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)
    mouse_id=Column(Integer,ForeignKey('mouse.id'),nullable=False) #FIXME grandparent_id
    slice_id=Column(Integer,ForeignKey('slice.id'),nullable=False) #FIXME parent_id
    startDateTime=Column(DateTime,default=datetime.now)
    __mapper_args__={'polymorphic_identity':'cell'}
    def __init__(self,Slice=None,Mouse=None,Experiments=[],Hardware=[],slice_id=None,mouse_id=None,experiment_id=None,hs_id=None,startDateTime=None):
        super().__init__(Experiments,Hardware)
        #printD(Slice.mouse)
        self.startDateTime=startDateTime
        self.slice_id=slice_id
        self.mouse_id=mouse_id
        self.experiment_id=experiment_id
        self.hs_id=hs_id
        #self.slice=Slice #FIXME extremely inconsistent behavior around this DO NOT USE
        #self.mouse=Slice.mouse #FIXME wierd
        if Slice:
            if Slice.id:
                self.slice_id=Slice.id
                self.mouse_id=Slice.mouse_id
            #else:
                #raise AttributeError
    #def strHelper(self,depth=0):
        #base=super().strHelper(depth)
    def __repr__(self):
        base=super().__repr__()
        return '%s%s%s%s'%(base,''.join([h.strHelper(1) for h in self.hardware]),self.slice.strHelper(1),''.join([c.strHelper(1) for c in self.datafiles[0].subjects]))


