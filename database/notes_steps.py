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
