from database.models import Step, StepRecord
from database.imports import printD
from rig.ipython import embed

from database.dataio import Check
class tempDataIO(Check):
    """ Temporary dataio so that steps can be written and tested in advance """
    from database.models import Checker
    MappedClass=Checker
    def check(self,**kwargs):
        #raise NotImplementedError('Please implement me :) !')
        print( NotImplementedError('Please implement me :) !') )

class StepBase: 
    #TODO what is really cool about the way I have this set up right now is that you can use literally anything in a write step
        #I'm currently using my own backend, but anyone should be able to use the step frame work presented here WITHOUT the db
        #which means, that I need decouple the two so that one can run without the other
        #but but but there is so much cool stuff you get by having the steps in a database :/
        #well, maybe the step database could be its own thing? ick no, we'll worry about this later
    #dataIO=None #import this #FIXME I'm a bit worried about importing and initing the same dataio many times

    dataio=tempDataIO #FIXME
    keepRecord=False #TODO use this so that we can doccument steps and choose not to check them, bad scientist!
    checkpoint_step=False  #FIXME naming
    fail=False #TODO controls how the step fails
            
    dependencies=[] #this now used internally without the need for BaseExp/ExpBase
    expected_writeTarget_type=None #TODO one and only one per step

    @property
    def name(self):
        """ Modify as needed"""
        return self.__class__.__name__

    def __init__(self,session,ctrlDict,experiment=None): #FIXME for self running steps we need the ctrlDict
        if not self.__doc__:
            printD(self.dataio.__name__)
            if self.dataio.__name__=='tempDataIO':
                self.__doc__=self.dataio.__doc__
            else:
                raise NotImplementedError('PLEASE DOCUMENT YOUR SCIENCE! <3 U FOREVER %s'%self.__class__)
        if not experiment: #FIXME
            self.experiment_id=1
        else:
            self.experiment_id=experiment.id
        try: #FIXME
            self.io=self.dataio(session,ctrlDict[self.dataio.ctrl_name],ctrlDict) #quite elegant!? FIXME if we're going to use set to set the experiment state and stuff like that then we need to expand ctrlDict
        except:
            self.io=self.dataio(session,ctrlDict=ctrlDict)
        #TODO versioning instead of requiring unique names, the records are kept by id anyway and the name
        if not self.io.MappedInstance:
            printD('self.io.MappedInstance didnt init going to ipython')
            embed()
            printD(self.io)
            raise AttributeError('mapped instance didnt init')
            #SHOULD always get the most recent version, will have to verify this :/

        self.session=session
        try:
            #TODO version check! um... no?
                #well, except that the only things that might change are the dataIO or the deps
                #and the deps and the deps are already taken care of
                #we could track the changes to the dataio...
                #really we just want to have a record of the whole code base
                #or if the input on the dataio changes eg from axon to ni or something
            self.Step=session.query(Step).filter_by(name = self.name).order_by(Step.id.desc()).first()
            #printD(self.Step)
            if not self.Step:
                raise ValueError('No Step by that name')
        except ValueError:
            #raise
            self.persist()
        self.check_deps() #FIXME why didn't this call automatically?

    def check_deps(self):
        if not self.dependencies:
            return None
        deps=self.session.query(Step).filter(Step.name.in_(self.dependencies)).all()
        if len(deps) is not len(self.dependencies) and deps:
            printD('Length of deps and self.deps mismatch, check your spelling, did you create the dependency? May also be a first run Step.name = %s'%self.name)
            #embed()
            #raise ValueError('Length of deps and self.deps mismatch, check your spelling, did you create the dependency? Step.name = %s'%self.name)
        elif not deps: #FIXME
            printD('[!] no deps found, assuming first run through be sure to call again')
        else:
            pass
        if self.Step.dependencies:
            #if not set([d.name for d self.Step.dependencies]) == set(self.dependencies): 
            if not set(self.Step.dependencies) == set(deps): #TODO check if Step.deps needs {}
                printD('[!] dependences do not match, updating!')
        self.Step.dependencies.update(deps) #TODO make sure this updates proper
        self.session.commit()


    def persist(self,autocommit=True): #TODO
        self.Step=Step(name=self.name,docstring=self.__doc__,checkpoint=
                       self.checkpoint_step,dataio_id=self.io.MappedInstance.id,
                       keepRecord=self.keepRecord) #TODO subject, hardware, reagent type etc
                            #that might be one way to deal with writeTargets...
                            #except... no also there are the check steps that check for existence
                            #but that should be handled via the dataio...
        self.session.add(self.Step)


        if autocommit:
            self.session.commit()

    def format_dep_returns(self,**kwargs): #FIXME remind me why we aren't using bind?
        """ format the dependency returns to pass to io.do"""
        printD('FIXME')
        return [kwargs[name] for name in self.dependencies] #keeps them ordered at least but overloads the meaning of the order
    def add_kwargs(self,kwargs):
        """ in place modifier of kwargs used in do """
        pass
        
    def do(self,writeTarget=None,**kwargs):
        print('STEP %s >>'%self.__class__.__name__,self.__doc__)
        self.add_kwargs(kwargs) #add/rename kwargs to match what may be needed for the dataio
        dep_vals=self.format_dep_returns(**kwargs) #this looks weird becuase there are kwargs that match the name of dependencies
        if writeTarget:
            kwargs['writeTarget']=writeTarget
        kwargs['step_name']=self.__class__.__name__
        #printD(kwargs['step_name'])
        kwargs['dep_vals']=dep_vals #for analysis do steps and bind do steps? poorly doccumented
        try:
            valueDict=self.io.do(**kwargs) #FIXME maybe there is a place to chain recursive gets?
                #FIXME returning a dict is a artifact of haveing a bad setup for do_every_time, can fix soon
            if self.fail:
                if not valueDict[self.io.__class__.__name__]: #XXX NOTE XXX if fail dataio MUST return true or false
                    raise IOError('Step failed, resetting to last set of checkpoints')


            #self.experiment.steprecord.append(experiment.steprecord(self.Step,True)) #logging
            sr=StepRecord(experiment_id=self.experiment_id,step_id=self.Step.id,success=True,preceding_id=kwargs.get('preceding_id')) #TODO subjects; NOTE: preceding_id defaults to None...
            self.session.add(sr)
            if self.checkpoint_step: #FIXME combine this into self.Step (rename to self.something?)
                self.Step.isdone=True
            print('[OK] %s'%self.name)
            self.session.flush() #need this to get the id
            if self.keepRecord:
                kwargs['preceding_id']=sr.id
            kwargs.update(valueDict)
            return kwargs #ICK ICK ICK ICK man I really wish I could do this recursively
        except IOError:
            self.session.add(StepRecord(experiment_id=self.experiment_id,step_id=self.Step.id,success=False)) #TODO subjects etc, only keep track of time for steps that succeed
            if self.fail:
                printD('[!] Step failed. Resetting to last checkpoints.') #FIXME TODO need a way to break out to fix
                raise
            else:
                #self.experiment.steprecord.append(experiment.steprecord(self.Step,False))
                printD('[!] Step failed. Trying again.') #FIXME TODO need a way to break out to fix
                self.do(writeTarget,**kwargs)
                raise #FIXME breaks preceding
        finally:
            self.session.commit() #FIXME this make sense here?

class StepCompiler:
    """ Allows us to compile experimentes and steps offline
        need to make sure I can get the flow control to work
        properly with this though
    """
    #TODO ideally what we want is to compile a whole serries of sub graphs
        #that will have the same ordering every time and stretch from
        #one checkpoint step to the next, then those can be reused MUCH more easily
        #without having to guess at adding and removing nodes from a topo sort
        #during a live run (or something like that)
    #as long as we can get parallel orderings then all that needs to happen at
        #run time is to checkCheckpoints on the fly and choose the right stepList

    def __init__(self,baseStep,stepDict): #FIXME should be able to compile on steps not in the db
        #Base steps should be checkpoint steps when they produce new subjects/
        #reagents/hardware. If they dont produce anything but data, then they
        #should not persist since they will be reused over and over.
        self.baseStep=baseStep.Step
        self.stepDict=stepDict
        self.checkDeps()

    def compile_(self):
        self.checkDeps()
        self.branch_resets()
        return self.topoSort()
    @property
    def stepList(self): #FIXME
        #return self.unorderedTopoSort()
        return self.topoSort()
    def findConvergentNodes(self):
        #XXX good news, for convergent steps, as long as we pass the kwargs along to both children
            #all we have to do is make sure that we don't call the same node twice!
            #(temp persist until _all_ a grandchild node is called or the last/first node is called?
            #but we dont know the value is in kwargs until we error... so... we need the state?
            #TODO state and a step that pops kwarg values that are done (for all revdeps)
                #are highly related concepts... if you pop the key... don't even have to check the value
                #can just return a {None:None} dict if the step fails!
        #find nodes that converge in the atemporal graph
            #outcome 1: the dep is a simultaenous dep: do not run twice!
                #XXX this happends in the atemporal graph when the two revdeps are NOT
                    #in eachother's tc
            #outcome 2: the dep occurs @ multiple times
                #one way around this is to just always use check steps
                #but that means if you forget them everything will break
                #TODO track the state for these nodes and only compile them
                #at a later time
        def getStepsWithMultipleRevDeps(): #FIXME not quite sufficient! there could be two entire branches!
            pass
    def stepTreeThroughTime(self):
        #for steps that are used multiple times
            #add or subtract steps based on their predicted state
        pass
    def unifyCommonSteps(self):
        #detect convergent nodes that can happen at the same time
        pass

    def checkDeps(self): #FIXME somehow I seem to be loosing the power of check steps??!
        if not self.baseStep.gotAllCps:
            print('[!] utoh! some checkpoints werent finished!') #FIXME I'm starting to think there are multiple types of checkpoint steps that server different fucntions:/
                #one kind is the high level exeperiment outputs, one is for temporal order, and one is for tracking experiment state, another is for determining when downstream stuff is parallel... shit
                #XXX actually... maybe not, because as long as something in the dep tree is persisting as True
                #then we can just go ahead and assume that any of its deps were already met
        #TODO ordering!
        self.unfinished_nodes=set(self.baseStep.transitive_closure)
        for step in self.baseStep.checkpoints:
            if step.isdone:
                printD(step.id)
                self.unfinished_nodes.difference_update(step.transitive_closure)
                self.unfinished_nodes.difference_update([step]) #needed so that finished steps are dropped
    def branch_resets(self):
        #get all the edges for nodes in the transitive closure
        all_edges=set()
        dthing={}
        id_to_name={}
        for node in self.unfinished_nodes:
            base_deps=node._deps()
            base_revs=node._revdeps()
            dthing[node.id]=(node.name,set(),set())

            all_edges.update([(edge.step_id, edge.dependency_id) for edge in node.edges])


        #names={} #FIX
        for node in self.unfinished_nodes:
            if node.do_each_time: #TODO should probably be a Check...
                pass

    
            place_holder=node.id #FIXME shitty code to deal with collisions, makes bad assumptions
            #while depD.get(node.id): #XXX NOPE that won't work either because of how we get deps
                #if node.id+1 not in all_ids:
                    #place_holder=node.id+1

            #names[place_holder]=node.name
            #idNameDict={n.name:n.dependency_id for n in node.dependencies}
            #ordered_deps=[idNameDict[name] for name in self.stepDict[node.name].dependencies]
            #depD[place_holder]=ordered_deps #node._deps()
            #if node._revdeps: #FIXME naming
                #revD[place_holder]=node._revdeps()
            #else:
                #S.append(place_holder)


    def unorderedTopoSort(self): #TODO paralellizeable?
        """ Now ordered!"""
        #FIXME in theory we should just be able to call this again based on isdone...
        #TODO this is critical
        from collections import deque
        S=deque() #note: order matters here too left most happen first
        depD={}
        revD={}
        names={}
        #FIXME problem for unfinished_nodes ;_; >> we need a count to do branching
        #all_ids = [n.id for n in self.unfinished_nodes]
        #all_ids.append(self.baseStep.id)

        #TODO WITHOUT RECOMPILING AFTER EVERY STEP::
            #we want to take each instance of a auto_reset
            #node and have the only edge be to the rev_dep...
        renameD={}

        #FIXME the problem is that we need to replace the revdeps too...
            #so revdeps come last

        for node in self.unfinished_nodes:
            place_holder=node.id #FIXME shitty code to deal with collisions, makes bad assumptions
            #while depD.get(node.id): #XXX NOPE that won't work either because of how we get deps
                #if node.id+1 not in all_ids:
                    #place_holder=node.id+1

            names[place_holder]=node.name
            depIdNameDict={n.name:n.id for n in node.dependencies}
            ordered_deps=[depIdNameDict[name] for name in self.stepDict[node.name].dependencies]
            depD[place_holder]=ordered_deps #node._deps()
            if node._revdeps: #FIXME naming
                revD[place_holder]=node._revdeps()
            else:
                S.append(place_holder)

        #so it turns out that there is a super weird bug when adding the node itself
            #it happens because unfinished_nodes is ACTUALLY still attached to the session!
            #despite the rename, bam, nailed it :)
        S.append(self.baseStep.id) #gotta have the node itself in
        node=self.baseStep
        depIdNameDict={n.name:n.id for n in node.dependencies}
        ordered_deps=[depIdNameDict[name] for name in self.stepDict[node.name].dependencies]
        depD[self.baseStep.id]=ordered_deps
        names[self.baseStep.id]=self.baseStep.name

        L=deque()
        discards=set()
        while S:
            #printD(S)
            node=S.pop()
            #printD(node)
            L.appendleft(node)
            for dep in depD[node]:
                revD[dep].discard(node)
                discards.add(dep)
                if not revD[dep]: #ie if the set is empty
                    revD.pop(dep)
                    S.append(dep)
            depD.pop(node)
        if depD or revD:
            printD( depD,revD )
            printD( names )
            d={names[n]:[names[n] for n in dep] for n,dep in depD.items()}
            r={names[n]:[names[n] for n in rev] for n,rev in revD.items()}
            printD( d, r )
            raise TypeError('Graph starting at >>%s<< is not acyclic!!'%self.baseStep.name)
        else:
            return [names[id] for id in L]
    
    def topoSort(self):
        return self.unorderedTopoSort()

class StepRunner:
    """ The class that actually runs the steps and interacts with subjects, hardware, etc
        Might also be where I put the step list builder, but I think that should go in step
        compiler or maybe even directly in the database since it should all be compiled beforehand
    """
    #how do we take the list L returned by the topo sort and use it with flow control?!
    def __init__(self,session,baseStep,stepDict,ctrlDict,Experiment,StepCompiler=StepCompiler):
        #FIXME all base steps should be done or fail where fail is how we continue
        self.compiler=StepCompiler(baseStep,stepDict)
        self.session=session
        stepList=self.compiler.compile_()
        self.getSteps(stepList,stepDict,ctrlDict,Experiment) #FIXME need a way to pick up where we left off??? interact w/ step record?
        #FIXME do something bout stepDict vs iStepDict
  
    def getSteps(self,stepList,stepDict,ctrlDict,Experiment):
        iStepDict={}
        for step in stepList:
            iStepDict[step]=stepDict[step](self.session,ctrlDict,Experiment)
        self.iStepDict=iStepDict

    #FIXME the step manager should probably handle all of this in conjunction with the database?
    #XXX depreicated
    def getDeps(self,stepDict): #this is gonna be a bit crazy, since all the steps are inited off the bat
        #FIXME I foresee the need for a way to reload the deps if something goes wrong...
            #maybe we can just call getDeps again? hell, we could even call it with a new step dict!
            #or even a new ctrlDict! actually... I bet changes to the ctrlDict get passed along...
            #HRM that might be a better way to handle controllers that haven't started... TODO
            #but that isn't good... because the tree is obfusticating the steps!
        self.iDepDict={}
        iodeps=set() #validate the iodeps to make sure they are all met in the previous steps
            #sadly don't currently have a good way to automatically correct for this :/
        for dep in self.dependencies: #TODO could probably be refactored for all the speedz
            iodeps.update(stepDict[dep].dataIO.dependencies)
        ioset=set(self.dataIO.dependencies)
        #TODO the step dependencies that corrispond to io deps (that need to go at the end)
        missing=ioset.difference(iodeps.intersection(ioset))
        if missing:
            raise ValueError('None %s\' dependencies satisfy the io dep for %s'%(self.name,missing))
        for dep in self.dependencies:
            self.iDepDict[dep]=stepDict[dep](stepDict,session,Experiment,ctrlDict)
        #FIXME make sure the dataio deps are executed LAST in the order
            #since kwarg passing is a substitute for func(func())

        #TODO easy way to persist progress is StepRecord/exp...

        #TODO optimize to limit when we need to recompute the topo sort, do as much before hand as possible
            #basically we want a 'persistent true' vs a 'transient true' distinction,
            #so a step can return that it exited successfully and still need to be completed
            #it should then be possible to predict the state of a node preceeding a given step apriori (I think)
    #XXX depreicated
    def runDeps(self,kwargDict): 
        #FIXME massive problem here! convergent upstream steps will be run multiple times!!!!!! NOT TO MENTION LOOPS!! #FIXME this needs to go to ExpBase, we need deps and revdeps, the nodes in the graph shouldn't be trying to traverse the graph! some steps that remain perisistently true will just be natural checkpoints
        #topo sort sub trees, find convergent nodes???
        #FIXME also have to deal with linearity in time for some stuff because SOME convergent nodes
            #are actaully called multiple times because they aren't actually the same step
            #will have to deal with that... instances of the step vs the step itself :/
            #when to converge and when not to converge
            #TODO the stepStateDict should help with this since node invalidation could make this work right
        for name,dep in self.iDepDict:
            FUCK=writeTargetTracker.getSubject() #TODO, maybe something like this!!!?
                #yes, because you can just add a 'go to next subject' step?
                #or is that too much... I have the subject tree traversal practially
                #automated at this point... I want that functionality too...
            kwargDict.update(dep.do(writeTarget=FUCK,**kwargs)) #FIXME damn it still need external management for the writeTarget :/
            #FIXME UNLESS we handle that here? but... we do need expman to bind subjects to data :/

    def do(self,**kwargs):
        self.kwargs_state=kwargs
        #if not kwargs.get('first_time_done'): #good news, we don't need this
            #kwargs['first_time_done']=True
            #stepList=self.compiler.compile_()
        #elif kwargs.get('recompile'):
        stepList=self.compiler.compile_()
        printD(stepList)
        current_step=self.iStepDict[stepList[0]]
        recompile=False
        for name in stepList: #FIXME loop isnt going to work for this!
            #unless that is, I massively improve the complier?
            #FIXME right now I would have to recompile every time I wanted to loop!
            #but at least that means I know where the problem is ^_^
            #and hell, I guess for the time being that will do :D
            current_step=self.iStepDict[name]

            try:
                self.kwargs_state.update(current_step.do(**self.kwargs_state))
            except:
                raise #TODO
                recompile=True
                break

            #printD(self.kwargs_state)
        if recompile:
            self.do(**kwargs) #FIXME somehow I think these will be the wrong kwargs?


