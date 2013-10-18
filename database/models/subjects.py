from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasDataFiles, HasHardware, HasExperiments, HasProperties


###-----------------------
###  Subject Base
###-----------------------

class SubType(): #FIXME not sure if this is a good replacement for strain or not...
    #awe yeah type token
    id=Column(Integer,primary_key=True)
    parenttype_id=Column(Integer,ForeignKey('subtype.id'))
    subtypes=relationship('SubType',primaryjoin='SubType.id==SubType.parenttype_id',backref=backref('parenttype',uselist=False,remote_side=[id])) #AARRRGGGGGG not the most helpful way to do this >_<


class SubjectType(Base): #XXX not using, favoring use of STE so we can have nice python properties
    #id=Column(Integer,primary_key=True) #FIXME may not need this
    #name=Column(String,nullable=False,unique=True)
    id=Column(String,primary_key=True)
    subjects=relationship('Subject',primaryjoin='Subject.type_id==SubjectType.id',backref=backref('type',uselist=False))
    #reference_type=None #might be a way to add something like HardwareSubject??? may need the mixin for that and just have the mixin define the type by the table name
    #better to use HasMetaData, HasFiles, etc than to make stuff subjects... maybe change to 'HasExperiments'
    #true it is not as explicit...
    def __str__(self):
        return id


#TODO make sure that generating experiment and experiments are fine to be the same experiment
#FIXME if subjects have data about them and are generate by the same experiment there will be an infinite loop
#TODO TODO the best way to associate hardware to a subject is NOT by direcly linking the subject to the hardware, becuase that can change, but using the hardware present at that time with it's associated datafilesource (or the like) and associating the subject to THAT sub structure
HasDataFileSourcePlaceHolder=type('thingamabob',(object,),{}) #a way to associated a df channel/source to a subject until I can get the data out of the datafile and into the raw data... I think this is a good way...
class Subject(HasMetaData, HasDataFiles, HasSwcHwRecord, HasExperiments, HasProperties, HasHardware, HasNotes, Base):
    __tablename__='subjects'
    id=Column(Integer,primary_key=True)
    #type=Column(String,nullable=False)
    type_id=Column(String,ForeignKey('subjecttype.id'),nullable=False)

    #whole-part relationships for all subjects
    parent_id=Column(Integer,ForeignKey('subjects.id'))
    children=relationship('Subject',primaryjoin='Subject.id==Subject.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))

    #imagine you could patch the same cell multiple times with different headstages, what would be needed
    #or hell, the same cell with multiple headstages (some serious assertions here wrt dendrite patching)
    #FIXME HasHardware needs to be mutable and work on a single experiment basis

    #experiment in which the subject was generated (eg a mating, or a slice prep)
    generating_experiment_id=Column(Integer,ForeignKey('experiments.id'))
    generating_experiment=relationship('Experiment',backref=backref('generated_subjects'),uselist=False)

    #generative relationships, some are being preserving others are terminal (binary fision anyone?)
    #FIXME if parent_id is None then we can use this???? maybe a bit too much overlap?
    #ontogeny vs part-whole
    generated_from_subjects=relationship('Subject',secondary='subjects_experiments',
            primaryjoin='Subject.generating_experiment_id==subjects_experiments.c.experiments_id',
            secondaryjoin='Subject.id==subjects_experiments.c.subjects_id', #FIXME this is the problem
            backref='generated_subjects')
    #FIXME under this construction subjects that are generated by an experiment and have data about them cause errors
    #SOLUTION? maybe some subjects are more like reagents for certain experiments so input_subjects? could handle it that way in Experiment?
    #data containing subjects vs 'used' subjects
    #could also just leave off geid when they are enerated by the experiment where they are data subjects...

    #identified groups connector
    #XXX NOTE XXX we do NOT need this for subjectcollection because generating_parent_id props via exp
    group_id=Column(Integer,ForeignKey('subjectgroup.id',use_alter=True,name='sg_fk')) #FIXME fuck, m-m on this? :/ subjects *could* belong to mupltiple identified groups, for example the jim group and the jeremy group
    location_id=Column(Integer,ForeignKey('locations.id'))

    #datetime data birth/death, time on to right/ time out of rig etc
    #other time points are probably actually metadata bools
    startDateTime=Column(DateTime,default=datetime.now)
    sDT_abs_error=Column(Interval)
    endDateTime=Column(DateTime)

    #variables for running experiments #FIXME move to protocol
    paramNames=tuple #persistable values that are not filled in at init
    preStepNames=tuple
    interStepNames=tuple
    postStepNames=tuple
    child_type=Base #FIXME?

    @property
    def rootParent(self): #FIXME probably faster to do this with a func to reduce queries
        if self.parent:
            return parent.getRootParent()
        else:
            return self

    @property
    def lastChildren(self,allChilds=[]):
        if not allChilds and self.children:
            return lastChildren(self.children)
        else:
            new_allChilds=[]
            for child in allChilds:
                try:
                    new_allChilds.extend(child.children)
                except:
                    pass
            if not new_allChilds:
                return allChilds
            return lastChildren(new_allChilds)

    @validates('parent_id','generating_experiment_id','startDateTime','sDT_abs_error','endDateTime')
    def _wo(self, key, value): return self._write_once(key, value)

    __mapper_args__ = {
        #'polymorphic_on':type,
        'polymorphic_on':type_id,
        'polymorphic_identity':'subject',
    }

    def nthChildren(self,n,allChilds=[]):
        if n:
            if not allChilds and self.children:
                return nthChildren(n-1,self.children)
            else:
                new_allChilds=[]
                for child in allChilds:
                    try:
                        new_allChilds.extend(child.children)
                    except:
                        pass
                return nthChildren(n-1,new_allChilds)
        else:
            return allChilds


    def __init__(self,parent_id=None,generating_experiment_id=None,
            group_id=None,startDateTime=None,sDT_abs_error=None,
            Experiments=[],Hardware=[],Properties={}):

        #FIXME there might be a way to do this with try:except
        if parent_id:
            self.parent_id=int(parent_id) #FIXME could lead to some hard to follow errors... raise earlier?
        if generating_experiment_id:
            self.generating_experiment_id=int(generating_experiment_id)
        if group_id:
            self.group_id=int(group_id)
        self.startDateTime=startDateTime
        self.sDT_abs_error=sDT_abs_error

        self.experiments.extend(Experiments)
        self.hardware.extend(Hardware)
        self.properties.update(Properties)
        #[self.Properties(self,key,value) for key,value in Properties.items()]

class SubjectGroup(Base): #TODO m-m probably should just make a 'HasArbitraryCollections' mixin
    id=Column(Integer,primary_key=True)
    name=Column(String(30),nullable=False)
    parent_id=Column(Integer,ForeignKey('subjects.id',use_alter=True,name='sub_fk')) #FIXME this won't join to children...
    parent=relationship('Subject',primaryjoin='Subject.id==SubjectGroup.parent_id',backref=backref('subgroups'),uselist=False) #URG this feels REALLY ugly
    members=relationship('Subject',primaryjoin='and_(Subject.group_id==SubjectGroup.id,Subject.parent_id==SubjectGroup.parent_id)') #m-m?

    def __len__(self):
        return len(self.members)

class SubjectCollection(Subject): #FIXME NOT to be used for purely logical groups eg cell tuple
    """Identified collections of subjects that have no physical form in themselves yet are still subjects and can generate subjects"""
    __tablename__='subjectcollection'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)
    #name=Column(String(30),nullable=False) #should now be in properties
    __mapper_args__ = {'polymorphic_identity':'subjectcollection'}

    @property
    def remaining(self):
        return [m for m in self.members if not m.endDateTime]

    @property
    def size(self): #FIXME just use len??
        return len(self.members)

    def __len__(self):
        return len(self.members)

###-----------------------
###  Subjects
###-----------------------

class Mouse(Subject):
    __tablename__='mouse'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)

    #FIXME SEND THESE TO PROPERTIES???
    #eartag=Column(Integer)
    #tattoo=Column(Integer)
    #name=Column(String(20))  #words for mice

    #cage and location information
    #cage_id=Column(Integer,ForeignKey('cage.id')) #the cage card number moved to location

    sex_id=Column(String(1),ForeignKey('sex.abbrev'),nullable=False) #FIXME properties?

    strain_id=Column(Integer,ForeignKey('strain.id')) #phylogeny of strains shall be handled in its own table

    __mapper_args__ = {'polymorphic_identity':'mouse'}

    @property
    def age(self):
        if self.endDateTime:
            return self.endDateTime-self.startDateTime #FIXME uncertainty
        else:
            return datetime.now()-self.startDateTime #uncertainty plox
        
    @property
    def breedingRecs(self):
        return [e for e in self.experiments if e.type.name=='mating record']

    def __init__(self,parent_id=None,generating_experiment_id=None,group_id=None,
            startDateTime=None,sDT_abs_error=None,eartag=None,tattoo=None,name=None,
            sex_id=None,Experiments=[],Hardware=[]):

        super().__init__(parent_id=parent_id,generating_experiment_id=generating_experiment_id,
            group_id=group_id,startDateTime=startDateTime,sDT_abs_error=sDT_abs_error,
            Experiments=[],Hardware=[])

        self.sex_id=sex_id
        self.strain_id=strain_id

        #self.eartag=eartag #identifiers store... keywords store? these arent reused across individuals...
        #self.tattoo=tattoo #so they don't need their own table...
        ##self.num=num
        #self.name=name

        #self.cage_id=cage_id

    
    def ___repr__(self): #XXX depricated
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
    __mapper_args__ = {'polymorphic_identity':'slice'}
    @property
    def dateTimeToRig(self): #FIXME this seems like a REALLY bad way to make up for the undefined nature of startDateTime............ docstring maybe????
        return self.startDateTime
    @property #FIXME again, these are things that are outside the BASIC datastore that I am building here, so they should go somehwere else
    def dateTimeOut(self):
        exp=self.generating_experiment
        return exp.endDateTime
    @property
    def thickness(self):
        return [m for m in self.experiments[0].metadata_ if m.metadatasource.name=='trmSliceThickness'][0] #FIXME this ok?


class Cell(Subject):
    __mapper_args__={'polymorphic_identity':'cell'}
    def __repr__(self):
        base=super().__repr__()
        return '%s%s%s%s'%(base,''.join([h.strHelper(1) for h in self.hardware]),self.parent.strHelper(1),''.join([c.strHelper(1) for c in self.datafiles[0].subjects]))


#FIXME the binding between data and subjects is really fucking tenuous sometimes... :/
#FIXME think about whether we really want to bind subjects to hardware, that seems... strange???
#FIXME HasDataRecords places a corrisponding entry for subjects as opposed to defining a 'HasDataRecords/HasExperiments' that works for subjects and anything like subjects?
class HardwareSubject(Subject): #TODO we can make this ObjectSubject and bind anything we want to a subject without having to do crazy shit with Hardware-Hardware interactions and stuff like that since most hardware doesn't have generation experiments
    """Class used to represent hardware as a subject for calibration"""
    #hell, chemistry is just a bunch of reagent subjects...
    #this DOES mean that I will need to come up with a way of associating subjects/people/hardware to MDSes in a transient way but still keep records, this is one of those things that fluctuates more slowly
    __tablename__='hardwaresubject'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False,unique=True)
    hardware=relationship('Hardware',backref=backref('data_records',uselist=False),uselist=False) #FIXME hw-sub relationships are now fucking insane
    __mapper_args__={'polymorphic_identity':'hardware'}
    def __init__(self,hardware_id,parent_id=None,generating_experiment_id=None,
            group_id=None,startDateTime=None,sDT_abs_error=None,
            Experiments=[],Hardware=[]):

        super().__init__(parent_id=parent_id,generating_experiment_id=generating_experiment_id,
            group_id=group_id,startDateTime=startDateTime,sDT_abs_error=sDT_abs_error,
            Experiments=[],Hardware=[]) #Hardware=[] : somewhere down there there is a sliderule

        self.hardware_id=int(hardware_id)

class Sample(Subject):
    __mapper_args__={'polymorphic_identity':'sample'}
    #does this pattern work for samples taken from cytoplasm?
    #it is generated by an experiment
    #it will probably have data associated with it at some point...
    #looking good...
    #it will have a literal part-whole parent and a generating subject that are the same...
