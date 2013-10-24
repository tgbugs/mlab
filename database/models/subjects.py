from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasDataFiles, HasHardware, HasExperiments, HasProperties, HasSwcHwRecords, HasTreeStructure

#has events to provide a consistent way to keep track of predicted future things, maybe even conflicts if I will be absent
#did I set up the SetupStep yet? that is really important for interactive checklisting


###-----------------------
###  Subject Base
###-----------------------

class SubType(): #FIXME not sure if this is a good replacement for strain or not...
    #awe yeah type token
    id=Column(Integer,primary_key=True)
    parenttype_id=Column(Integer,ForeignKey('subtype.id'))
    subtypes=relationship('SubType',primaryjoin='SubType.id==SubType.parenttype_id',backref=backref('parenttype',uselist=False,remote_side=[id])) #AARRRGGGGGG not the most helpful way to do this >_<


class SubjectType(Base): #FIXME right now this isn't doing anything useful, could it?
    id=Column(String,primary_key=True)
    subjects=relationship('Subject',primaryjoin='Subject.type_id==SubjectType.id',backref=backref('type',uselist=False))
    def __str__(self):
        return self.id
    def __init__(self,id,has_sex=None):
        self.id=id
        self.has_sexual_ontogeny=has_sex


#TODO make sure that generating experiment and experiments are fine to be the same experiment
#FIXME if subjects have data about them and are generate by the same experiment there will be an infinite loop
#TODO TODO the best way to associate hardware to a subject is NOT by direcly linking the subject to the hardware, becuase that can change, but using the hardware present at that time with it's associated datafilesource (or the like) and associating the subject to THAT sub structure
class Subject(HasMetaData, HasDataFiles, HasSwcHwRecords, HasExperiments, HasProperties, HasHardware, HasNotes, HasTreeStructure, Base):
    """ Please see Subject for basic __init__ kwargs"""
    __tablename__='subjects'
    id=Column(Integer,primary_key=True)
    type_id=Column(String,ForeignKey('subjecttype.id'),nullable=False)

    #part-whole relationships for all subjects use primarily for tracking variables in experiments
    #can be used for both mutually exclusive (death) relationships and coterminus (in vivo, groups)
    parent_id=Column(Integer,ForeignKey('subjects.id')) #FIXME move to 'HasTreeStructure'???
    children=relationship('Subject',primaryjoin='Subject.id==Subject.parent_id',backref=backref('parent',uselist=False,remote_side=[id])) #FIXME remote()? FIXME parent id set on child, then set again on children?

    #FIXME since we removed generating experiment id do we need to have a way to link say a slice to an experiment? and direcly link? yeah, we need a destructive version of has ontogeny; NO WE DO NOT, we can just query against ALL the subjects in the experiment and sort by type... but... maybe we do... to make it explicit... since we might not add them to the experiment while it is running... and ideally we want to limit any modification of the raw experiment (eg no adding subjects once endDateTime has been set) and we do still want to have a record of inputs and outputs made explicit

    #identified groups connector
    #XXX NOTE XXX we do NOT need this for subjectcollection because generating_parent_id props via exp
    group_id=Column(Integer,ForeignKey('subjectgroup.id',use_alter=True,name='sg_fk')) #FIXME fuck, m-m on this? :/ subjects *could* belong to mupltiple identified groups, for example the jim group and the jeremy group
    #blinded group id?
    #location_id=Column(Integer,ForeignKey('locations.id'))

    #datetime data birth/death, time on to right/ time out of rig etc
    #other time points are probably actually metadata bools
    startDateTime=Column(DateTime,default=datetime.now)
    sDT_abs_error=Column(Interval)
    endDateTime=Column(DateTime)
    @validates('startDateTime','sDT_abs_error','endDateTime') #FIXME FIXME want to vaildate parent_id but sqlalchemy's default behavior writes it twice
    def _wo(self, key, value): return self._write_once(key, value)

    __mapper_args__ = {
        'polymorphic_on':type_id,
        'polymorphic_identity':'subject',
    }

    def __init__(self,parent_id=None,reproduction_experiment_id=None,
            group_id=None,startDateTime=None,sDT_abs_error=None,
            Experiments=(),Hardware=(),Properties={}):
        if self.type_id is 'subject':
            raise NotImplementedError('You shouldn\'t add undefined subjects to the database!')

        #FIXME there might be a way to do this with try:except
        if parent_id:
            self.parent_id=int(parent_id) #FIXME could lead to some hard to follow errors... raise earlier?
        if reproduction_experiment_id:
            self.reproduction_experiment_id=int(reproduction_experiment_id)
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


###----------------------------------------------------------
### Subject Mixins  These are ONLY for ForeignKey columns !!!
###----------------------------------------------------------

class UsesJTI:
    """ Mixin for making new Subject classes that have their own columns
        TODO/FIXME should all other mixins inherit from JTISubject automatically?

        By default __tablename__=cls.__name__.lower()+'s' so if the plural of mouse is not mouses
        and that bothers you set __tablename__ manually

        By default __mapper_args__={'polymorphic_identity':cls.__name__.lower()} to override
        set __mapper_args__ manually and to extend mapper args use __mapper_args__.update({})
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()+'s'
    @declared_attr
    def id(cls):
        super_id=super().__tablename__ #FIXME this is is unstable and only works if UsesJTI is right before Subject...
        #printD(super_id)
        return Column(Integer,ForeignKey('%s.id'%super_id),primary_key=True)
    @declared_attr
    def __mapper_args__(cls):
        return {'polymorphic_identity':cls.__name__.lower()} #FIXME
    #__mapper_args__ = {'polymorphic_identity':type_string}
    def __init__(self,**kwargs):
        super().__init__(**kwargs)


#XXX NOTE: subjects must have either HGE or HO, but how to check for this... TODO
class HasGeneratingExperiment(UsesJTI): #single parent object TODO may want a non JTI for reagents/hardware?
    """ For things that are generated by an experimental protocol, this might
        overlap with hardware and reagents... mixing acsf is an experiment
        not writing down the exact values the scale gives is actually bad
        because you want some record verifying that you follow the protocol
    """
    @declared_attr
    def generating_experiment_id(cls):
        return Column(Integer,ForeignKey('experiments.id'),nullable=False)

    @declared_attr
    def generating_experiment(cls):
        #generating experiments should be what 'defines' certain properties
        #there won't be a generated from subjects here because there should only be a single parent
        #thus we will use the part-whole
        ctab=cls.__tablename__
        return relationship('Experiment',backref=backref('generated_%s'%ctab)
                            ,uselist=False)

    #@declared_attr
    #def parent_id(cls): #FIXME conflicts with parent_id set in Subject :/
        #all subjects have parent ids, HGE subjects must specify one
        #return Column(Integer,ForeignKey('subjects.id'),nullable=False)

    #FIXME without sub experiments we cannot automatically assign parent
    #based on the single subject of an experiment because experiments
    #can have multiple subjects, therefore we need a mechanism in the
    #protocol that will correctly associate parent-child, I think I already
    #have this actually
    def __init__(self,**kwargs):
        #removed the check against repo_experiment_id becasue sqlalchemy catches the overlapping fks
        #and thus prevents the conflict
        try:
            if kwargs['generating_experiment_id']:
                self.generating_experiment_id=int(kwargs.pop('generating_experiment_id'))
        except KeyError:
            pass #this will catch on insert due to not null constraint
            #raise AttributeError('%s must have a generating_experiment_id!'%self.__class__.__name__)
        super().__init__(**kwargs)

#
#FIXME figure out some way to have HGE be default for all objects except those w/ HO??? seesm wrong
#ah yes, imagine all the psychological studies which need neither of those, same with certain field work
class HasOntogeny(UsesJTI): #FIXME naming to make it clear how this works w/ generating experiment...
    """mixin for subjects where n>=1 parents can combine to make m>=1 offspring
    """
    #this setup nicely enforces the fact that if there are parents
    #there had bettered be some record of the mating
    #of couse you could use this to track the reproductive habits
    #of a single bacterium, which totally misses the point, but yeah
    @declared_attr
    def repro_experiment_id(cls): #FIXME naming
        #TODO check that the exptype is right?
        return Column(Integer,ForeignKey('experiments.id'))
    @declared_attr
    def repro_experiment(cls):
        ctab=cls.__tablename__
        return relationship('Experiment',backref=backref('repro_%s'%ctab),
                            uselist=False)
    @declared_attr
    def ontpars(cls): #ontogenetic parents
        sctab='subjects'#super().__tablename__ #FIXME
        ctab=cls.__tablename__
        cname=cls.__name__
        return relationship(cname,secondary='%s_experiments'%sctab,primaryjoin=
                '%s.repro_experiment_id==%s_experiments.c.experiments_id'%(cname,sctab),
                secondaryjoin='%s.id==%s_experiments.c.%s_id'%(cname,sctab,sctab), #FIXME will break for mouse
                backref='offspring') #due to lack of mice_experiments table >_<
    @validates('repro_experiment_id')
    def _wo(self, key, value): return self._write_once(key, value)
    def __init__(self,**kwargs):
        #removed the check against repo_experiment_id becasue sqlalchemy catches the overlapping fks
        #and thus prevents the conflict
        try:
            if kwargs['repro_experiment_id'] is not None:
                self.repro_experiment_id=int(kwargs.pop('repro_experiment_id'))
        except KeyError:
            pass #will catch like usual when the column is null, making the errors consistent
        super().__init__(**kwargs)
            #raise Warning('%s has no parents, do you want this?'%self.__class__.__name__)

class HasSexOntogeny(HasOntogeny): #TODO composite subjects can have sex ontogoeny w/o having a sex
    @property
    def sire(self):
        if self.ontpars:
            return [m for m in self.ontpars if m.sex_id == 'm'][0]
        else:
            print('This %s has no recorded father!'%self.__class__.__name__)
    @property
    def dam(self):
        if self.ontpars: #FIXME need to require @ least a mother?
            return [m for m in self.ontpars if m.sex_id == 'f'][0]
        else:
            print('This %s has no recorded mother!'%self.__class__.__name__)
    #@declared_attr
    #def sire(cls): #TODO
        #pass
        #cn=cls.__name__
        #return relationship('%s'%cn,primaryjoin='',secondaryjoin='',uselist=False)
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class HasSex(HasSexOntogeny):
    @declared_attr
    def sex_id(cls):
        return Column(String(1),ForeignKey('sex.abbrev'),nullable=False)
    @property
    def breedingRecs(self):
        return [e for e in self.experiments if e.type.name=='Mating Record'] #FIXME does this go here?
    def __init__(self,**kwargs): #FIXME how to do this cooperatively
        self.sex_id=str(kwargs.pop('sex_id')) #FIXME also varargs is a danger?
        super().__init__(**kwargs)

class HasGenetics(UsesJTI):
    @declared_attr
    def strain_id(cls):
        return Column(Integer,ForeignKey('strain.id'),nullable=False)
    #something to track the measured genotype and make sure it matches
    @property
    def somethingYouDoWithStrain(self):
        return None
    def __init__(self,**kwargs):
        self.strain_id=int(kwargs.pop('strain_id'))
        super().__init__(**kwargs)

class HasLocation(UsesJTI): #FIXME may not need JTI on this one in particular...
    @declared_attr
    def location_id(cls):
        return Column(Integer,ForeignKey('locations.id'))
    @declared_attr
    def location(cls):
        return relationship('Location',primaryjoin='%s.location_id==Location.id'%cls.__name__,
                            backref=backref('%s'%cls.__tablename__),uselist=False)
    def __init__(self,**kwargs):
        try:
            location_id=kwargs.pop('location_id')
            self.location_id=int(location_id) #FIXME location_id=None will error
        except KeyError:
            pass
        super().__init__(**kwargs)

#FIXME Mixins MUST Implement ForeignKey constraints otherwise they should not be a mixin

###---------------------------------------------------------------------------------
###  Subjects THOU SHALT NOT USE THESE FOR QUERYING only for creation and post query
###---------------------------------------------------------------------------------

class NewSubjectType(UsesJTI, Subject):
    pass

class Litter(HasSexOntogeny, Subject):
    @property
    def member_sex_count(self): #FIXME optimize some day
        return {key:len([m for m in self.children if m.sex_id is key]) for key in ['m','f','u']} #FIXME get all sex_ids, also, best format or no?
    def member_sex_left(self): #FIXME optimize some day
        return {key:len([m for m in self.children if m.sex_id is key and not m.endDateTime]) for key in ['m','f','u']} #FIXME get all sex_ids, also, best format or no?
    @property
    def remaining(self):
        return [m for m in self.children if not m.endDateTime]
    @property
    def size(self): #FIXME just use len??
        return len(self.children)
    def __len__(self):
        return len(self.children)


class Mouse(HasSex, HasGenetics, HasLocation, Subject):
    #FIXME  some way to add rows to SubjectType automatically?
    #TODO consider using 'include_properties':[] and/or 'exclude_properties':[]
    __tablename__='mice'
    @property
    def age(self):
        if self.endDateTime:
            return self.endDateTime-self.startDateTime #FIXME uncertainty
        else:
            return datetime.now()-self.startDateTime #uncertainty plox
    #def __init__(self,**kwargs):
        #super().__init__(**kwargs)


class Slice(HasGeneratingExperiment, Subject): #FIXME slice should probably be a subject
    @property
    def dateTimeToRig(self): #FIXME is the how I want to do this... I could do this via type...?
        return self.startDateTime
    @property
    def dateTimeOut(self): #FIXME well, since I can't do that, how do I persist THIS (in type??)
        exp=self.generating_experiment
        return exp.endDateTime
    @property
    def thickness(self): #FIXME
        return None
        #FIXME TODO using a dict doesn't work for sanity checks, need a per experiment sanity check table that matches the protocol values, either by association or something else, whatever the mechanism it needs to generalize to making sure hardware matches
        return self.experiments[0].values_from_protocols['thickness'] #FIXME currently a sanity check against the protocol but no way to measure...


class Cell(HasGeneratingExperiment, Subject):
    pass
    #def __repr__(self):
        #base=super().__repr__()
        #return base
        #return '%s%s%s%s'%(base,''.join([h.strHelper(1) for h in self.hardware]),self.parent.strHelper(1),''.join([c.strHelper(1) for c in self.datafiles[0].subjects]))


class HardwareSubject(): #XXX depricated, hardware simply uses HasExperiments now... and steps can be on hardware or reagents in addition to subjects
    #TODO we can make this ObjectSubject and bind anything we want to a subject without having to do crazy shit with Hardware-Hardware interactions and stuff like that since most hardware doesn't have generation experiments
    """Class used to represent hardware as a subject for calibration"""
    #hell, chemistry is just a bunch of reagent subjects...
    #this DOES mean that I will need to come up with a way of associating subjects/people/hardware to MDSes in a transient way but still keep records, this is one of those things that fluctuates more slowly
    hardware_id=Column(Integer,ForeignKey('hardware.id'),nullable=False,unique=True) #FIXME
    hardware=relationship('Hardware',backref=backref('data_records',uselist=False),uselist=False) #FIXME hw-sub relationships are now fucking insane
    __mapper_args__={'polymorphic_identity':'hardware'}
    def __init__(self,**kwargs):
        self.hardware_id=int(kwargs.popitem('hardware_id'))

class Sample(HasGeneratingExperiment, Subject):
    #does this pattern work for samples taken from cytoplasm?
    #it is generated by an experiment
    #it will probably have data associated with it at some point...
    #looking good...
    #it will have a literal part-whole parent and a generating subject that are the same...
    pass

#is broken as expected, fortunately sqlalchemy catches it for us w/ the multiple fks
#class StrangComingIntoBeing(HasOntogeny, HasGeneratingExperiment, Subject):
    #pass
