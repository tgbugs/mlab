#Basic step logic, dissociated from datasource for the time being, may reintegrate into api.py

#substeps or dependency tree to say a step is compelted? I think they are the same...
#because let's say you want to do an analysis step, then the tree will say 'ok you need to do these things first'#and when it gets to a step that has other deps, it will go all the way to the first dependency and then work its way down
class _Step:
    #XXX: NOTE these are only the DIRECT dependencies, and the order specifies only how they are to be run
    #not the actual order of steps which will be constructed from the dependencies
    #FIXME easy way to specify that a step should be depth or dredth first???? easy! just make a checkpoint step!
    direct_dependencies=('ordered','list/tuple','of','step','names that is ordered to make things deterministic') #XXX NOTE: every step should have at least one dependnecy unless they are leaves that other things depend on
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

    def __init__(self,session,Controller,ParentObject):
        pass
    def getter(self):
        pass
    def setter(self):
        pass
    def success(self):
        pass


class Step: #TODO make this peristable
    dependencies={'set','set'}
    preceeding_step='None' #TNIS could also be derived from a list? and is not necessarily a strict dependnecy, may ultimately go away?
    #TODO searching for a way to combine topo sort with procedures that must be done by one person and therefore need some regularity

    def noSideEffects(self):
        #database read
        #get value from datasource
        #do analysis or strict functions
        pass
    def sideEffects(self):
        #print to terminal! BUT this is ok, because THIS CODE doesn't do it, the datasource handles ALL of that
        #write to database; minimal a boolean 'step succeeded/failed'
        #change a variable; eg move a motor or set MCC state, clx file
        #write analysis results
        pass

    #TODO problem: looks like we need to intersperse se with nse?

class Step: #fucking mess... back to thinking
    deps={'',''}
    previous_step=None
    datasources=['',''] #FIXME when a writer writes is it just another datasource???
    reader_types=['',''] #should be ordered for consistency could be a set
    writer_types=['','']
    def __init__(self,ExpStepRecord,datasourcedict={}):
        self.ExpStepRecord=ExpStepRecord
        self.nodepreaders=nodpereaders #FIXME shouldn't this be defined before __init__ since we've split off datasources? actually I think it needs to be live! :/
        self.Writers=Writers #big problem here... the 'writer' is an object that may not exist... since it would be an initilized mapped class :/
    def readSomeThings(self,Readers=()):
        #FIXME preferably read from memory, which I THINK is how Readers is flexible
        #in that Writers can return the written thing directly to the reader... and
        #the code that goes through the steps should automatically pass Writers to Readers
        #directly from the dep tree, so we call self.go(nondepreaders,(dep1.go(),dep2.go(),dep3.go())) or something like that
        pass
    def doSomeThings(self):
        pass
    def writeSomeThings(self):
        #FIXME shouldn't we be able to smartly pass values already in memory/session from step to step without having to read from the database?
        pass
    def go(self,Readers=(),Writers=()):
        def readThings(Readers=()):
            return [r.read for reader in  Readrs]
        def doThings(readThings=()):
        def writeThings(doneThings=()):


class Step:
    deps=[]
    setters=[]
    datasources=[]
    analysisDatasources=[]
    
    def setValues(self):
        pass
    def getValues(self):
        pass
    def checkGottenAgainstSet(self):
        pass


class addNewSubjectStep: #??? instead of the pre/inter/post I use currently?
    pass

class trmGotCell:
    datasources=['trmGetBool']
    def do(self):
        for ds in self.datasources:


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
        buildStepTree(all_Steps_dict,all_Steps_dict[step]

