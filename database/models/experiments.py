import numpy as np
from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes, HasMetaData, HasReagents, HasHardware, HasReagentTypes, HasDataFileSources, HasMetaDataSources, HasMdsHwRecords, HasDfsHwRecords

###-------------------
###  Experiment tables
###-------------------

class ExperimentType(HasReagentTypes, HasDataFileSources, HasMetaDataSources, Base): #FIXME no longer needs HDFS or HMDS
    """this stores all the constant data about an experiment that will be done many times"""
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(String(30),nullable=False)
    abbrev=Column(String)
    methods_id=Column(Integer,ForeignKey('citeable.id')) #XXX FIXME depricated in favor of steps
    #FIXME this will be reworked so that it has a single 'checkpoint' step

    experiments=relationship('Experiment',backref=backref('type',uselist=False))
    checkpoint_step_id=None #TODO this defines the methodes and the tools etc, Experiment can doccument the exact tree? or the toposort of the tree

    base_step_id=Column(ForeignKey('steps.id'),nullable=False)
    base_step=relationship('Step')
    #FIXME loop steps
    @property
    def steps(self): #TODO
        return base_step.transitive_closure() #or something like this
        #TODO make sure this thing is indexed by step name!

    @property
    def reagents(self): #FIXME
        return [rt.currentLot for rt in self.reagenttypes]


    def __init__(self,name=None,abbrev=None,base_step_id=None,methods_id=None,ReagentTypes=()):
        self.name=name
        self.abbrev=abbrev
        self.base_step_id=int(base_step_id)
        if methods_id is not None:
            self.methods_id=int(methods_id)

        self.reagenttypes.extend(ReagentTypes)

    def __repr__(self):
        return super().__repr__()


class Experiment(HasMetaData, HasReagents, HasMdsHwRecords, HasDfsHwRecords, Base): #TODO figure out how to unify with steps and 'sub checkpoint' deps
    #TODO somewhere in here this needs to reference the version of the code used to generate it
    #probably a commit hash will be sufficient but that assumes the people use git
    __tablename__='experiments'
    id=Column(Integer,primary_key=True)
    type_id=Column(Integer,ForeignKey('experimenttype.id'),nullable=False)

    #FIXME do these go here?
    project_id=Column(Integer,ForeignKey('project.id'),nullable=False)
    person_id=Column(Integer,ForeignKey('people.id'),nullable=False)

    startDateTime=Column(DateTime,default=datetime.now())
    endDateTime=Column(DateTime)

    #possible replacement for sdt and edt; TODO essentially Experiment because a flattened StepRecord for easier querying... FIXME these should probably go in exp type?
    startStepsTime=None #checkpoint steps the must evaluate to true prior to creation
    endStepTime=None

    #TODO list of steps completed with the time of completion: association object class? seems nice for querying
    #TODO FIXME don't let someone create an experiment if specific checkpoints/check steps aren't satisfied
    step_tree_version_id=None
    steprecord=relationship('StepRecord',order_by='StepRecord.id')
    steps=association_proxy('steprecord','step',creator=lambda step_id, success: StepRecord(step_id=step_id,success=success)) #FIXME make sure experiment_id gets set...

    stepStateDict={} #FIXME make me peristable please! hstore? or... something on top of step record?
    #we can do this by looking at the current step and comparing it to the state of the LIVE tree...
    def getBaseStepDict(self):
        for step in self.type.steps:
            self.stepStateDict[step.id]=False
        return stepStateDict


    @validates('type_id','person_id','endDateTime','startDateTime')
    def _wo(self, key, value): return self._write_once(key, value)

    def setEndDateTime(self,dateTime=None):
        if not self.endDateTime: #FIXME I should be able to do this with validates
            if not dateTime:
                self.endDateTime=datetime.now()
            else:
                self.endDateTime=dateTime
        else:
            print('endDateTime has already been set!') #FIXME why do warnings not just warn!?
            #raise RuntimeWarning('endDateTime has already been set!')

    def __init__(self,type_id=None,project_id=None,person_id=None,Reagents=(),Subjects=(),startDateTime=None,endDateTime=None):
        #FIXME block init until all checkpoint dependencies pass
        self.type_id=int(type_id)
        if project_id: #FIXME move to experiment type? if exptype is hierarchical can duplicate...
            self.project_id=int(project_id)
        if person_id:
            self.person_id=int(person_id)

        self.startDateTime=startDateTime
        self.endDateTime=endDateTime

        self.reagents.extend(Reagents)
        self.subjects.extend(Subjects)



class StepRecord(HasNotes, Base): #in theory this could completely replace experiment...
    id=Column(Integer,primary_key=True)
    experiment_id=Column(Integer,ForeignKey('experiments.id'),nullable=False)
    step_id=Column(Integer,ForeignKey('steps.id'),nullable=False)
    #startDateTime=None #pretty sure we don't need this...
    endDateTime=Column(DateTime,default=datetime.now) #FIXME just have dateTime???
    success=Column(Boolean,nullable=False)
    step=relationship('Step',uselist=False)
    data=None #TODO do I need this here??

    #FIXME is this redundant? is it enough to know that a specific reagent type is to be used at step x
        #and then to look up the actual reagent used in that experiment? what if the reagent that has data?
        #and why not keep track of the data here too? (rhetorical question, but answer might be we should)
    hardware_id=Column(Integer,ForeignKey('hardware.id'))
    reagent_id=Column(Integer,ForeignKey('reagents.id'))
    subject_id=Column(Integer,ForeignKey('subjects.id'))
    subjectgroup_id=Column(Integer,ForeignKey('subjectgroup.id')) #suddenly uuids look really freeking handy :/
    #TODO could this replace records tables for hardware/subject binds or hardware mds binds?
    #TODO how can we use this to record the ACTUAL 'writeTarget' that was used in the step?
        #do we want that? or will it be too redundant?
        #either way, I think we might want to associate reg/sub/har to single steps
        #the question is whether we want to propagate them to the experiment that way
        #ANSWER no they can be direcly associated with the experiment since the id is all
        #that would be passed along anyway; could check for consistency...


###
#FIXME TODO steps, just like experiments, produce things, IN FACT this makes the start and end times supurfluous, because the step becomes 'pair mice' and it happends at a specific time
    #whether this complicates querying and slows it way the fuck down is another question altogether :/ it does fix the ambigious meaning of start and end time thought...
    #furthermore they are still compatible because instead of start time and end time we end up with 'start step' and 'end step' or 'start steps' and 'end steps' which for
    #most experiments will be a 'check/validate all checkpoints step...'
class Step(Base):
    """ Why do we have steps when we could just write code you ask. Well
        The reason is because we want to automate things AND doccument how
        we do it. This makes doccumentation and coding the same process
        which is right in line with core python philosophy and is an
        extremely useful mindset to have for science. Write once: read forever.
    """
    #TODO version steps and automatically update edges!???! FIXME or everything write once except docstring? or even  version the docstring???
    #TODO figure out if there is a way to store python fucntions in the db
    #TODO when report=False we can compile entire serries of steps down to just the get/set/write for speed
    #TODO make sure to allow 'set only' steps that just print a 'make sure you do this' for things that don't actually need validation
    #XXX NOTE yes, this is a better way to conceptualize sub-experiments using the tree
    #TODO individual steps should be versioned, not sure what the basis should be though... changed deps?
        #the reason we want versioning is so that we can always use the base step to recreate the tree
        #or really so that the step-experiment association is actually the steps that were used
    __tablename__='steps'
    id=Column(Integer,primary_key=True) #FIXME this could nicely alleviate the concern about naming, but we do still need a reasonable way id them
    type_id=None #FIXME do we want this??? get, set, check, analysis? don't really... need a table for 4 things?
        #get set bind read write analysis check
    name=Column(String,nullable=False,unique=True) #FIXME versioning??!??
    docstring=Column(String,nullable=False) #pulled from __doc__ and repropagated probably should be a citeable?
    checkpoint=Column(Boolean,default=False) #FIXME TODO is this the right way to do this??? nice way to delimit the scope of an 'experiment' if we still have experiments when this is all done
    isdone=Column(Boolean,default=False) #FIXME FIXME should we keep the step tree state here!???! seems ok? unless we try to run two experiments off the same step at the same time, then we will really mess stuff up... ideally we need a per experiment tree or something??? though from a science checklist point of view you don't want to reset stuff every time... hrm; using only direct dependencies is nice in that as soon as the steps registers as successful and the next step proceeds, the previous (in many cases) should be reset to false!
    @validates('isdone')
    def is_checkpoint(self, key, value):
        if not value:
            return value
        elif not self.checkpoint:
            raise TypeError('Step is not a checkpoint, state must always be False!')
        else:
            return value

    dataio_id=Column(Integer,ForeignKey('dataio.id'),nullable=False) #FIXME will need to unify metadatasource, datasource, datafilesource, etc under one index? default should be 'StepEvent' or something... maybe 'StepRecord'
    keepRecord=Column(Boolean,default=True) #set to false for steps that don't need to be put in the record; TODO can this double as a 'set_only'???
    #FIXME damn, this does seem to complicate the 'HasExperiments' setup...
        #the step itself *should* specify an expected subject type
    #TODO where do we put things like 'get this subject,' 'retrieve this hardware' 'make sure you have this reagent'
        #do those need to be tied to datasources? or maybe a special kind of step?
        #however they are stored/added the MUST be leaves on the tree AND they must be super easy to query for
        #this WILL be slower and more complicated than just giving a list of reagents needed etc
        #BUT it will kill two birds with one stone: doccumentation and procedure
        #There is a wierd divide between 'go get X' and 'got X' that has to do with the state of the tree
        #that I have talked about elsewhere, but it should be trivial to create new leaf steps from a list of
        #hardware or reagents and link them directly to a setup step
        #and that can be linked to a 'check to make sure we have this' step, which can be linked to a 'make this' step...
    hardwaretype_id=None #these leaves are really easy to change/update? the dependency changes but the record of the step and the object is w/ experiment
    subjecttype_id=None
    reagenttype_id=None
    #dep_assoc=Table('step_dep_assoc',Base.metadata, #this represents the edges of the graph
                                 #Column('dependency_id',ForeignKey('steps.id'),primary_key=True),
                                 #Column('step_id',ForeignKey('steps.id'),primary_key=True))

    #TODO/FIXME ordering for generating actual procedures???

    #TODO objective: an Experiment has steps_version_number_id=n and using that
        #it should be possible to get the list of dependencies for each Step
        #steps either exist or do not exist, all that matters is that traversing
        #the graph from the root should give the original version
    #def creator(step): #just in case the setattr fails
        #raise IOError('use add_dep to add things because this doesnt check edges properly')

    dependencies=association_proxy('edges','dependency') #creator set at __init__
    _deps=association_proxy('edges','dependency_id')
    _revdeps=association_proxy('_rev_edges','step_id')
    all_edges=relationship('StepEdgeVersion',primaryjoin='StepEdgeVersion.step_id==Step.id'
        ,order_by='-StepEdgeVersion.id') #newest first to make finding deletes simple
    transitive_closure=association_proxy('tc_edges','tc')
    #lambda:[] #all upstream dependencies expressed as edges starting at self and ending at all upstream steps #step graphs might be small enough we don't need this
    #@property
    #def allcps(self): #FIXME this is super slow? better to try to query for it?
        #return set((step for step in self.transitive_closure if step.checkpoint))
    allcps=association_proxy('tc_edges','cp')

    @property
    def checkpoints(self): #FIXME STI to break out checkpoint step methods??? NO
        #the step itself cannot be in its own tc, thus see if a step is in the union of all TCs and done
        #there may be a faster way but right now I don't really care
        cpunion=set()
        [cpunion.update(cp.allcps) for cp in self.allcps]
        return self.allcps.difference(cpunion) #cps that arent in the union of the tc cps

    @property
    def gotAllCps(self):
        for cp in self.checkpoints:
            if not cp.isdone:
                return False
        return True
        #return all([cp.isdone for cp in self.checkpoints])

    def edges_at_version(self,version=None): #FIXME profile these two to see which is faster
        if not self.all_edges:
            return []
        if not version:
            version=self.all_edges[0].id #works because of inverted sort
        ver_edges=[edge for edge in self.all_edges if edge.id <= version]
        first_instance=[]
        for edge in ver_edges:
            found = False
            for fedge in first_instance: #surely this would make it slower?
                found = edge.dependency_id == fedge.dependency_id
                if found:
                    break #this way we stop inner loop asap
                else:
                    continue
            if not found:
                first_instance.append(edge)
        return [edge.dependency for edge in first_instance if edge.added]

    def deps_at_version(self,version=None): #FIXME not quite working as expected...
        if not self.all_edges:
            return []
        elif not version:
            version=self.all_edges[0].id #works because of inverted sort
        ver_edges=[edge for edge in self.all_edges if edge.id <= version]
        culled=set()
        for deled in [edge for edge in ver_edges if not edge.added]:
            [culled.add(edge) for edge in ver_edges if edge.dependency_id ==
             deled.dependency_id and edge.id <= deled.id] #<= gets rid of the deleted too
        return [edge.dependency for edge in ver_edges if edge not in culled]

    @reconstructor
    def __dbinit__(self):
        def creator(step):
            return StepEdge(self,step)
        setattr(self.dependencies,'creator',creator)

    def __init__(self,**kwargs): 
        super().__init__(**kwargs)
        def creator(step):
            return StepEdge(self,step)
        setattr(self.dependencies,'creator',creator)


class StepEdge(Base): #FIXME note that this table could hold multiple independent trees
    __tablename__='stepedges' #FIXME WARNING risk of redundant insert and delete!
    step_id=Column(Integer,ForeignKey('steps.id'),primary_key=True)
    dependency_id=Column(Integer,ForeignKey('steps.id'),primary_key=True)
    step=relationship('Step',primaryjoin='Step.id==StepEdge.step_id',backref=backref('edges',lazy=False,collection_class=set),uselist=False,lazy=True) #TODO might be possible to do cycle detection here? FIXME might want to spec a join_depth if these graphs get really big...
    dependency=relationship('Step',primaryjoin='Step.id==StepEdge.dependency_id',backref=backref('_rev_edges',lazy=False,collection_class=set),uselist=False,lazy=True) #lazy should be ok, this IS used in the association_proxy...
    def __init__(self,step_id=None,dependency_id=None):
        self.step_id=int(step_id)
        self.dependency_id=int(dependency_id)
    def __repr__(self):
        return '\n%s -> %s'%(self.step_id,self.dependency_id)
    def __eq__(self,other):
        return self.step_id == other.step_id and self.dependency_id == other.dependency_id
    def __ne__(self,other):
        return self.step_id != other.step_id or self.dependency_id != other.dependency_id
    def __hash__(self):
        return hash('%s%s'%(self.step_id,self.dependency_id)) #needed to make add and update work properly




    #versioning does not quite seem to be what I want??!? since this is only add/delete
    #recovering the version of the whole table is possible using that type of versioning
    #but maybe it is a bit more than I need?


class StepTC(Base):
    """ Transitive closure of the graph """
    __tablename__='steptc'
    step_id=Column(Integer,ForeignKey('steps.id'),primary_key=True)
    tc_id=Column(Integer,ForeignKey('steps.id'),primary_key=True)
    step=relationship('Step',primaryjoin='Step.id==StepTC.step_id',backref=backref('tc_edges',lazy=False,collection_class=set),uselist=False,lazy=True) #TODO might be possible to do cycle detection here? FIXME might want to spec a join_depth if these graphs get really big...
    tc=relationship('Step',primaryjoin='Step.id==StepTC.tc_id',uselist=False,lazy=True) #lazy should be ok, this IS used in the association_proxy...
    cp=relationship('Step',primaryjoin='and_(Step.id==StepTC.tc_id, Step.checkpoint == True)',uselist=False,lazy=True) #FIXME this doesn't quite seem right...
    def __eq__(self,other):
        return self.step_id == other.step_id and self.tc_id == other.tc_id
    def __ne__(self,other):
        return self.step_id != other.step_id or self.tc_id != other.tc_id
    def __hash__(self):
        return hash('%s%s'%(self.step_id,self.tc_id)) #needed to make add and update work properly



#TODO TypeEngine.with_variant!!! for switching between Hstore and pickle or the like, WHOO

class StepEdgeVersion(Base):
    #TODO diff two versions of the tree
    __tablename__='stepedgevers'
    id=Column(Integer,primary_key=True) #we can just call this version number... FIXME sqlite autoincrement?
    step_id=Column(Integer,ForeignKey('steps.id'),primary_key=True)
    dependency_id=Column(Integer,ForeignKey('steps.id'),primary_key=True)
    dependency=relationship('Step',primaryjoin='Step.id==StepEdgeVersion.dependency_id',uselist=False) #may want to joined load here, don't need it for the normal table
    added=Column(Boolean,nullable=False) #if added==False then it was deleted
    @validates('id','step_id','dependency_id','added')
    def _wo(self, key, value): return self._write_once(key, value)

    @property
    def deleted(self): #just for completeness
        return not self.added

    def __repr__(self):
        return 'ver:%s step:%s dep:%s add:%s'%(self.id,self.step_id,self.dependency_id,self.added)


class stepGraphManager: #XXX Depricated in favor of the events interface
    def __init__(self,session):
        self.session=session
        self.steps=session.query(Step.id).all()
        self.edges=np.array(session.query(StepEdge.step_id,StepEdge.dependency_id).all()) #XXX NOTE these edges can be used over and over again!
    def getDeps(self,edge):
        return self.edges[:,1][self.edges[:,0]==edge]
    def addEdge(step,dep):
        s=int(step)
        d=int(dep)
        def cycle(edge,step):
            if edge==step:
                return True
            deps=getDeps(edge)
            if step in deps:
                return True
            else:
                for e in deps:
                    if cycle(e,step):
                        return True
                return False
        if cycle(d,s):
            raise BaseException('This edge would add a cycle to the graph! It will not be created!')
        else:
            self.session.add(StepEdge(s,d))


class StepManager:
    def __init__(self,session,root_step=None):
        self.root=root_step
        #self.session=session
        self.edges=np.array(session.query(StepEdge.step_id,StepEdge.dependency_id).all())
    def mirrorGraph(self,root=None):
        #make a graph from adjascency matrix and the root node
        if not root:
            root=self.root.id
        #nodes=set()
        def traverse(node,edges,nodes=set()):
            nodes.add(node) #FIXME could pop the node...
            for edge in edges[:,1][edges[:,0]==node]:
                if edge==node:
                    edges=edges[edges[:,0]!=edges[:,1]]
                elif edge in nodes:
                    continue
                traverse(edge,edges)
            return nodes
        return traverse(root,self.edges)


        def _traverse(edge,edge_set):
            edge_set.add(edge)
            [traverse(e,edge_set) for e in edge.dependency.edges]
        #edge_set=set()
        #[traverse(edge,edge_set) for edge in self.root.edges]
            

