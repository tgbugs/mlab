from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasDataFiles, HasHardware
from database.models.experiments import Experiment
from database.standards import frmtDT


###-----------------------
###  Subject Base
###-----------------------

#TODO make sure that generating experiment and experiments are fine to be the same experiment
#FIXME if subjects have data about them and are generate by the same experiment there will be an infinite loop
class Subject(HasMetaData, HasDataFiles, HasHardware, HasNotes, Base):
    __tablename__='subjects'
    id=Column(Integer,primary_key=True)
    type=Column(String,nullable=False)

    #whole-part relationships for all subjects
    parent_id=Column(Integer,ForeignKey('subjects.id'))
    children=relationship('Subject',primaryjoin='Subject.id==Subject.parent_id',backref=backref('parent',uselist=False,remote_side=[id]))

    #experiment in which the subject was generated (eg a mating, or a slice prep)
    generating_experiment_id=Column(Integer,ForeignKey('experiments.id'))
    generating_experiment=relationship('Experiment',backref=backref('generated_subjects'),uselist=False)
    generated_from_subjects=relationship('Subject',secondary='experiments_subjects',
            primaryjoin='Subject.generating_experiment_id==experiments_subjects.c.experiments_id',
            secondaryjoin='Subject.id==experiments_subjects.c.subjects_id', #FIXME this is the problem
            backref='generated_subjects')
    #FIXME under this construction subjects that are generated by an experiment and have data about them cause errors
    #SOLUTION? maybe some subjects are more like reagents for certain experiments so input_subjects? could handle it that way in Experiment?
    #data containing subjects vs 'used' subjects
    #could also just leave off geid when they are enerated by the experiment where they are data subjects...

    #identified groups connector
    group_id=Column(Integer,ForeignKey('subjectcollection.id')) #FIXME fuck, m-m on this? :/ subjects *could* belong to mupltiple identified groups, for example the jim group and the jeremy group

    #datetime data birth/death, time on to right/ time out of rig etc
    #other time points are probably actually metadata bools
    startDateTime=Column(DateTime,default=datetime.now)
    sDT_abs_error=Column(Interval)
    endDateTime=Column(DateTime)

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
            if not new_allChilds[]:
                return allChilds
            return lastChildren(new_allChilds)

    @validates('parent_id','generating_experiment_id','startDateTime','sDT_abs_error','endDateTime')
    def _wo(self, key, value): return self._write_once(key, value)


    __mapper_args__ = {
        'polymorphic_on':type,
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

    def __init__(self,Parent=None,GeneratingExperiment=None,Group=None,
            startDateTime=None,sDT_abs_error=None,Experiments=[],Hardware=[],
            parent_id=None,generating_experiment_id=None,group_id=None):

        self.parent_id=parent_id
        self.generating_experiment_id=generating_experiment_id
        group_id=group_id
        self.startDateTime=startDateTime
        self.sDT_abs_error=sDT_abs_error

        self.experiments.extend(Experiments)
        self.hardware.extend(Hardware)

        if Parent:
            if Parent.id:
                self.parent_id=parent_id
            else:
                raise AttributeError
        if GeneratingExperiment:
            if GeneratingExperiment.id:
                self.generating_experiment=GeneratingExperiment.id
            else:
                raise AttributeError
        if Group:
            if Group.id:
                self.group_id=Group.id
            else:
                raise AttributeError


class SubjectCollection(Base):
    """Identified collections of subjects such as litters, will have a generating experiment, but maybe shouldnt, this would allow for arbitrary groupings of subjects with all sorts of relations beyond just having the same datafile or something, eg this could keep track of pairs or groups of cells that are recorded @ same time"""
    #this could be used for cages?? subject collection collection (lol?)
    id=Column(Integer,primary_key=True)
    name=Column(String(30),nullable=False)
    members=relationship('Subject',primaryjoin='Subject.group_id==SubjectCollection.id',backref=backref('group',uselist=False))

    #not redundant because often collections will exist before the exact number of individuals are added
    generating_experiment_id=Column(Integer,ForeignKey('experiments.id'))
    generating_experiment=relationship('Experiment',backref=backref('generated_collections'),uselist=False)
    generated_from_subjects=relationship('Subject',secondary='experiments_subjects',
            primaryjoin='SubjectCollection.generating_experiment_id==experiments_subjects.c.experiments_id',
            secondaryjoin='Subject.id==experiments_subjects.c.subjects_id',
            backref='generated_collections')

    startDateTime=Column(DateTime,default=datetime.now)
    sDT_abs_error=Column(Interval)

    @validates('generating_experiment_id','startDateTime','sDT_abs_error')
    def _wo(self, key, value): return self._write_once(key, value)

    @property
    def size(self):
        return len(self.members)

    @property
    def remaining(self): #TODO
        return None #sum([m.dod==None for m in self.members])

    def makeSubjects(self): #TODO
        return None

###-----------------------
###  Subjects
###-----------------------

class Mouse(Subject):
    __tablename__='mouse'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)

    eartag=Column(Integer)
    tattoo=Column(Integer)
    name=Column(String(20))  #words for mice

    #cage and location information
    cage_id=Column(Integer,ForeignKey('cage.id')) #the cage card number

    sex_id=Column(String(1),ForeignKey('sex.abbrev'),nullable=False)

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

    cells=relationship('Cell',primaryjoin='Cell.mouse_id==Mouse.id',backref=backref('mouse',uselist=False)) #FIXME
    def __init__(self,GeneratingExperiment=None,Group=None,startDateTime=None,
            sDT_abs_error=None,eartag,tattoo=None,name=None,sex_id=None,
            strain_id=None,cage_id=None,Experiments=[],Hardware=[],
            generating_experiment_id=None,group_id=None):

        super().__init__(GeneratingExperiment=GeneratingExpeirment,Group=Group,
                startDateTime=startDateTime,sDT_abs_error=sDT_abs_error,
                Experiments=Experiments,Hardware=Hardware,
                generating_experiment_id=generating_experiment_id,group_id=group_id)

        self.notes=notes

        self.eartag=eartag
        self.tattoo=tattoo
        self.num=num
        self.name=name

        self.cage_id=cage_id

        self.sex_id=sex_id
        self.strain_id=strain_id
    
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
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True) #FIXME

    @property
    def dateTimeOut(self):
        exp=self.experiments[0]
        return exp.endDateTime

    @property
    def thickness(self): #FIXME TODO
        exp=self.experiments[0]
        emd=Experiment.MetaData
        session=object_session(self)
        return session.query(emd).filter(emd.experiment_id==exp.id,emd.datasource_id=='slice thickness') #ick this is nasty to get out and this isn't even correct

    __mapper_args__ = {'polymorphic_identity':'slice'}


class Cell(Subject):
    __tablename__='cell'
    id=Column(Integer,ForeignKey('subjects.id'),primary_key=True,autoincrement=False)
    __mapper_args__={'polymorphic_identity':'cell'}

    def __repr__(self):
        base=super().__repr__()
        return '%s%s%s%s'%(base,''.join([h.strHelper(1) for h in self.hardware]),self.parent.strHelper(1),''.join([c.strHelper(1) for c in self.datafiles[0].subjects]))

