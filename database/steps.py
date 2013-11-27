###---------
### THIS ONE
###---------

#TODO need a way to retrieve step classes directly from the database?
#FIXME this way of doing things is bad at recording get/set pairing for datasources :/
    #should the datasource/eventsource or whatever implement the get/check/set?
    #amusingly it looks like steps could inherit from datasources probably more flexible not to
    #FIXME some steps: eg setting modes, should only add themselves to the record on failure
        #otherwise the step list will become absurdly long
        #the unitary step tree can be kept somewhere else, or hopefully just reconstructed from the
        #base node if I can get it to work properly...
#TODO CHECK STEPS MAY NEED MORE DIVERSITY: EXPLORE
#these are the perisitent steps whose state is tracked directly, they are where everything should revert to, so slice on rig, got cell, analysis completed stuff like that; this is how we will do loops, if all the prior checkpoints are satisfied then we can build directly from the next known checkpoint step and trace the deps from there
    #another way to approach this is to assume a successful run and use invalidation steps
#persistent_node=False #True means that this node will not automatically reset itself to False on succesful exit, pretty sure this one of those 'hard' problems
#persistent_step=False #TODO a toggleable step that stores its state, may turn out that it should be thought of as a checkpoint step and so we will eventually get rid of it anyway
    #YEP XXX the whole point of checkpoint steps is that they can have MULTIPLE SIMULTANEOUS REVDEPS
    #thus, if it is not a checkpoint step, then the step will be called multiple times
    #checkpoint steps can still be called multiple times as needed by invalidating their state
    #TODO should all checkpoint steps be check steps that dependnt on a get or read step to validate?
        #the Set step would then also need to handle invalidation of other steps, which overlaods it
#TODO something to track experiment state

#from do()
    #FIXME writeTarget may not be for the final step until much later?
        #the the base write target should probably always be preceeded by a
        #Get boolean step that writes to experiment, ie: the "ExperimentDone" step
    #FIXME don't handle deps here, handle those upstairs in BaseExp???
    #FIXME loop steps, by taking a bool input at one step that then resets the state

    #FIXME multiple child steps??? using a database to pass values is super dumb
    #a good example is if we want to write to the db and do analysis at the same time
    #there is no reason why we shouldn't be able to do both at the same time... HRM
        #NOW FIXED by passing the kwargs dict around :/ village bycicle yada yada

from database.models import Step, StepRecord
from database.imports import printD
from IPython import embed
class StepBase: 
    #TODO what is really cool about the way I have this set up right now is that you can use literally anything in a write step
        #I'm currently using my own backend, but anyone should be able to use the step frame work presented here WITHOUT the db
        #which means, that I need decouple the two so that one can run without the other
        #but but but there is so much cool stuff you get by having the steps in a database :/
        #well, maybe the step database could be its own thing? ick no, we'll worry about this later
    #dataIO=None #import this #FIXME I'm a bit worried about importing and initing the same dataio many times
    dataio=None
    keepRecord=False #TODO use this so that we can doccument steps and choose not to check them, bad scientist!
    checkpoint_step=False  #FIXME naming
            
    dependencies=[] #this now used internally without the need for BaseExp/ExpBase
    expected_writeTarget_type=None #TODO one and only one per step

    @property
    def name(self):
        """ Modify as needed"""
        return self.__class__.__name__

    @property
    def __doc__(self):
        raise NotImplementedError('PLEASE DOCUMENT YOUR SCIENCE! <3 U FOREVER')

    def __init__(self,session,ctrlDict,experiment=None): #FIXME for self running steps we need the ctrlDict
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
    def do(self,writeTarget=None,**kwargs):
        dep_vals=self.format_dep_returns(**kwargs)
        if writeTarget:
            kwargs['writeTarget']=writeTarget
        kwargs['step_name']=self.__class__.__name__
        printD(kwargs['step_name'])
        kwargs['dep_vals']=dep_vals #for analysis do steps and bind do steps? poorly doccumented
        try:
            value=self.io.do(**kwargs) #FIXME maybe there is a place to chain recursive gets?
            #self.experiment.steprecord.append(experiment.steprecord(self.Step,True)) #logging
            self.session.add(StepRecord(experiment_id=self.experiment_id,step_id=self.Step.id,success=True)) #TODO subjects etc
            if self.checkpoint_step: #FIXME combine this into self.Step (rename to self.something?)
                self.Step.isdone=True
            print('[OK]')
            kwargs.update(value)
            return kwargs #ICK ICK ICK ICK man I really wish I could do this recursively
        except:
            #self.experiment.steprecord.append(experiment.steprecord(self.Step,False))
            raise

            self.session.add(StepRecord(experiment_id=self.experiment_id,step_id=self.Step.id,success=False)) #TODO subjects etc
            printD('[!] Step failed. Trying again.') #FIXME TODO need a way to break out to fix
            self.do(writeTarget,**kwargs)
        finally:
            self.session.commit() #FIXME this make sense here?


class StepRunner:
    """ The class that actually runs the steps and interacts with subjects, hardware, etc
        Might also be where I put the step list builder, but I think that should go in step
        compiler or maybe even directly in the database since it should all be compiled beforehand
    """
    #how do we take the list L returned by the topo sort and use it with flow control?!
    def __init__(self,session,stepList,stepDict,ctrlDict,Experiment):
        self.session=session
        self.stepList=stepList
        self.getSteps(stepDict,ctrlDict,Experiment) #FIXME need a way to pick up where we left off??? interact w/ step record?
        #FIXME do something bout stepDict vs iStepDict
  
    def getSteps(self,stepDict,ctrlDict,Experiment):
        iStepDict={}
        for step in self.stepList:
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
    def runDeps(self,kwargDict): #FIXME massive problem here! convergent upstream steps will be run multiple times!!!!!! NOT TO MENTION LOOPS!! #FIXME this needs to go to ExpBase, we need deps and revdeps, the nodes in the graph shouldn't be trying to traverse the graph! some steps that remain perisistently true will just be natural checkpoints
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
        current_step=self.iStepDict[self.stepList[0]]
        for name in self.stepList: #FIXME loop isnt going to work for this!
            #unless that is, I massively improve the complier?
            #FIXME right now I would have to recompile every time I wanted to loop!
            #but at least that means I know where the problem is ^_^
            #and hell, I guess for the time being that will do :D
            current_step=self.iStepDict[name]
            self.kwargs_state.update(current_step.do(**self.kwargs_state))
            print(self.kwargs_state)


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

    def __init__(self,baseStep): #FIXME should be able to compile on steps not in the db
        #Base steps should be checkpoint steps when they produce new subjects/
        #reagents/hardware. If they dont produce anything but data, then they
        #should not persist since they will be reused over and over.
        self.baseStep=baseStep.Step
        self.checkDeps()
    @property
    def stepList(self): #FIXME
        return self.unorderedTopoSort()
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

    def unorderedTopoSort(self): #TODO paralellizeable?
        from collections import deque
        S=deque() #note: order matters here too left most happen first
        depD={}
        revD={}
        names={}
        #FIXME problem for unfinished_nodes ;_; >> we need a count to do branching
        #all_ids = [n.id for n in self.unfinished_nodes]
        #all_ids.append(self.baseStep.id)
        for node in self.unfinished_nodes:
            place_holder=node.id #FIXME shitty code to deal with collisions, makes bad assumptions
            #while depD.get(node.id): #XXX NOPE that won't work either because of how we get deps
                #if node.id+1 not in all_ids:
                    #place_holder=node.id+1

            depD[place_holder]=node._deps()
            names[place_holder]=node.name
            if node._revdeps: #FIXME naming
                revD[place_holder]=node._revdeps()
            else:
                S.append(place_holder)

        #so it turns out that there is a super weird bug when adding the node itself
            #it happens because unfinished_nodes is ACTUALLY still attached to the session!
            #despite the rename, bam, nailed it :)
        S.append(self.baseStep.id) #gotta have the node itself in
        depD[self.baseStep.id]=self.baseStep._deps() #FIXME BEWARE revdeps not in...
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
            #return depD,revD
            raise TypeError('Graph is not acyclic!!')
        else:
            return [names[id] for id in L]

###
#FIXME do persisitent steps actually fix problems of simultaneous revdeps
    #AND temporal ordering at the same time?!
#S.appendleft(dep) #if there is a way to split deps into 'do last and together?'
#FIXME clearly I need to just do the bloodly temporal ordering and stop trying to be
    #all sneeky and smart about it and make it explicit instead of
    #trying to read minds huristically
    #XXX ACTUALLY, no, using bind steps and checkpoints is the right way for this
        #I may need to break out checkpoint steps and persist steps
        #but checkpoint steps are how we are going to get temporal order
        #for the 'do all this' then do that

    #FIXME how to gurantee the ordering matches that given above?
    #we don't want to do that here anyway, but if we want to reflect
    #the order without having the original list of names we are probably going to have a bad time :/
#edges=set() #might want to query for this? any edge that ends with an end in start.tc
#def makeDepDicts(edges):
    #edges=array(edges)
    #depDict=dict.fromkeys(edges[:,0],set())
    #revDepDict=dict.fromkeys(edges[:,1],set())
    #for step,dep in edges:
        #depDict[step].add(dep)
        #revDepDict[dep].add(step) #this is fucking stupid
    #return depDict,revDepDict
#depD,revD=makeDepDicts(edges)







###
#Basic step logic, dissociated from datasource for the time being, may reintegrate into api.py

#substeps or dependency tree to say a step is compelted? I think they are the same...
#because let's say you want to do an analysis step, then the tree will say 'ok you need to do these things first'#and when it gets to a step that has other deps, it will go all the way to the first dependency and then work its way down
    #XXX: NOTE these are only the DIRECT dependencies, and the order specifies only how they are to be run
    #not the actual order of steps which will be constructed from the dependencies
    #FIXME easy way to specify that a step should be depth or dredth first???? easy! just make a checkpoint step!
    #direct_dependencies=('ordered','list/tuple','of','step','names that is ordered to make things deterministic') #XXX NOTE: every step should have at least one dependnecy unless they are leaves that other things depend on
    #XXX this way the order things are done in is always preserved WITHIN dependencies, leading to more regularity in how an experiment is done... though there is some risk that things would fail if done in another order?

    #ordered lists of deps make experimental procedures deterministic
    #FIXME always test as UNORDERED to make sure that you aren't cheating by getting data from deps[0] that is infact needed in deps[1] but deps[0] is NOT explicitly listed in deps[1] as a dependency....
    #fucking side effects

    #this is better than just a list of things to check every time
    #the question is whether the dependencies will vary from experiment to experiment
    #and thus reduce reuseability? I don't think it will

    #FIXME big question, with the dep tree it is the REVERSE of how most people think of science,
    #namely as a list of things to do in a certain order
    #there may be a way to also have that functionality (ie just have no deps) but honestly I think this will end up being safer...
    #TODO in fact, when there are no steps, the dependencies for the experiment itself will just be the ordered list of steps, damn that is so cool :D
        #except that it would be better for things with 'no' deps to simply specify the previous thing so that the order would be preserved... that might be best... but it creates more work when the order doesn't really matter
    #FIXME one datasource per step?!??!?! FIXME ANSWER YES: because using the dependency tree model


    #preceeding_step='None' #TNIS could also be derived from a list? and is not necessarily a strict dependnecy, may ultimately go away?
    #TODO searching for a way to combine topo sort with procedures that must be done by one person and therefore need some regularity

    #def noSideEffects(self):
        #database read
        #get value from datasource
        #do analysis or strict functions
    #def sideEffects(self):
        #print to terminal! BUT this is ok, because THIS CODE doesn't do it, the datasource handles ALL of that
        #write to database; minimal a boolean 'step succeeded/failed'
        #change a variable; eg move a motor or set MCC state, clx file
        #write analysis results

    #TODO problem: looks like we need to intersperse se with nse?

        #FIXME preferably read from memory, which I THINK is how Readers is flexible
        #in that Writers can return the written thing directly to the reader... and
        #the code that goes through the steps should automatically pass Writers to Readers
        #directly from the dep tree, so we call self.go(nondepreaders,(dep1.go(),dep2.go(),dep3.go())) or something like that
        #FIXME shouldn't we be able to smartly pass values already in memory/session from step to step without having to read from the database?

class _BaseDataIO: #XXX DEPRICATED see dataio.py for new version
    @property
    def name(self):
        return self.__class__.__name__[4:]
    reader_name=None #aka ctrl_name #FIXME now though it seems more like a single function?!? :/ more code :/
    setter_name=None #useful for 'set variable' style steps eg mcc set mode
    Writer=None #useful for write database using orm steps eg MetaData
    def __init__(self,Reader,Setter=None):
        def checkName(iCls,name):
            if iCls.__class.__name__ == name:
                return iCls 
            else: raise AttributeError('Names dont match!')
        self.Reader=checkName(Reader,self.reader_name)
        self.Setter=checkName(Setter,self.setter_name)
        #FIXME analysis can be shoved into this framework by having setter and reader be the same class :/
        #but that stupidly inefficienty

        self.expected_value=None
        self.ev_error=None

    def setValue(value,error=None): #this would be 'expected value' eg the weight on a scale or the x,y coords
        raise NotImplementedError('You MUST implement this at the subclass level')
        self.ev_error=error
        self.expected_value=value #FIXME find a way to not duplicate this
        self.Setter(value)

    def getValue(self,analysis_value=None): #FIXME lots of bugs can come from the lack of mux here
        """ Read a value from some input source, sets self.value """
        #FIXME is it akward to pass in values as a function via reader!??! eg Reader=lambda: dumpdata()?
        #instead of actually passing values??!?! eeeeeehhhhh as long as I hide the implementation
        #FIXME but then the reader can't change at runtime...
        self.value=analysis_value
        if not self.value:
            self.value=self.Reader() #the value could technically be anything... bool, real, tuple...
        #self.Reader() could be what triggers the casscade of steps, but then we'd have to deal w/ fails
        raise NotImplementedError('You MUST implement this at the subclass level')

    def checkValue(self,checkingFunction=lambda v: v):
        """ Validate the measured value against the set/expected value
            or validate using a checkingFunction
        """
        if self.ev_error:
            minimum=self.expected_value - self.ev_error
            maximum=self.expected_value + self.ev_error
            if minimum >= self.value or self.value >= maximum:
                raise ValueError('Expected %s +- %s got %s'%(self.expected_value,self.ev_error,self.value))
        elif self.expected_value:
            if self.value != self.expected_value:
                raise ValueError('Expected %s got %s'%(self.expected_value,self.value))
        else:
            if not checkingFunction(self.value):
                raise ValueError('Check failed!')

    def transformValue(self,function=lambda value:value): #FIXME useful for live correction of outputs?
        self.value=function(self.value)
        raise NotImplementedError('You MUST implement this at the subclass level')

    def writeValue(self,writeTarget): #this should ALWAY be called FIXME Target or Targets?!???!
        """ write the value to the database associated with the writeTarget
            eg Experiment, Subject, Hardware, Reagent """
        self.Writer(writeTarget,self.value)
        raise NotImplementedError('You MUST implement this at the subclass level')
    
    def do(self,writeTarget,set_value=None,set_error=None):
        self.setValue(set_value)
        self.writeValue(writeTarget)


def things():
    #get scalar data
    #get tensor data
    #get timeserries of the above
    #get datafile
    #get true/false
    #get event
    
    #set value/variable

    #write to database
    
    #check one value against another
    pass



class DataFileSource: #the database entry PLUS how to record the datafile
    pass   
    



class CheckpointStep:
    #end of a protocol
    #block of things that make it faster to do them all before eg setup
    #auto generate from subjects, reagents and hardware/tools or other checkpoint steps
    pass


class addNewSubjectStep: #??? instead of the pre/inter/post I use currently?
    pass

class trmGotCell:
    datasources=['trmGetBool']
    def do(self):
        for ds in self.datasources:
            pass


def doExperiment():
    def getDataOnSubjectSet(): #this is what will trigger the dep tree to check and compile
        return None
    while 1:
        getDataOnSubjectSet() #FIXME seems like we may still need a way to deal with the subject tree too...
        if input()=='y': #a check to get a new slice? seems ugly compared to pre/inter/post...
            changeHigherLevelSubject() #yeah... still have to be able to changes slices...
        #how to doccument the pre/inter/post as part of the dep tree??? ACTUALLY, don't have too, it already IS doccumented, can just record that we did the steps again for a different set of subjects...
        #hybrid of the subject tree and the dep tree...
        #TODO a experiment-step-subject history table thing???!?!
        #this is why dep trees only need to be for a single subject, experiment logic will handle the rest


class stepStateTree: #replace with a list or a dict under exp logic?
    """class to keep track of the true false state of upstream nodes"""
    #FIXME this might already be present in the database, just check the step record
    #and make sure there is an record already matching Experiment-StepName with a value of True
    #surely there is a faster way... well yeah, just store the Step records (association table between experiment and step and time and maybe one other thing since steps can repeate) to a list in memory once they are persisted and then just check that so we don't have to query





#maybe start with an ordered list and then reorder based on deps?


#datasources are nodes with no dependencies! :) #FIXME except when they must be collected AFTER something in time :/
def topoSort(all_Steps_dict,current_step): #topological sort of the steps
    #FIXME maybe I DO want a bredth first search to deal with issues of temporal ordering???
    #yeah, especially since I have direct deps ordered already
    #get the last one first, (do all deps by same rule), get 2nd to last (do all deps by same rule), etc.
    for step in current_step.direct_dependencies: #TODO could be threaded... though direct deps may share...
        buildStepTree(all_Steps_dict,all_Steps_dict[step])

if __name__ == '__main__':
    main()
