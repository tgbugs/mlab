#Basic step logic, dissociated from datasource for the time being, may reintegrate into api.py

#substeps or dependency tree to say a step is compelted? I think they are the same...
#because let's say you want to do an analysis step, then the tree will say 'ok you need to do these things first'#and when it gets to a step that has other deps, it will go all the way to the first dependency and then work its way down
class Step:
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


#maybe start with an ordered list and then reorder based on deps?


#datasources are nodes with no dependencies! :) #FIXME except when they must be collected AFTER something in time :/
def topoSort(all_Steps_dict,current_step): #topological sort of the steps
    #FIXME maybe I DO want a bredth first search to deal with issues of temporal ordering???
    #yeah, especially since I have direct deps ordered already
    #get the last one first, (do all deps by same rule), get 2nd to last (do all deps by same rule), etc.
    for step in current_step.direct_dependencies: #TODO could be threaded... though direct deps may share...
        buildStepTree(all_Steps_dict,all_Steps_dict[step]

