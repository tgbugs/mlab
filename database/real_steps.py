#put all the steps here
from real_dios import * #the steps will use globals to look up the names of the dios
from database.steps import StepBase

#this can proceed without actually having to decide whether to use decorators or not
    #all we need is the names of the functions or the classes


###------
### steps
###------



### do this later, for now just write out the damned classes
namespace_dict={'dataIO':None,
                'keepRecord':True,
                'checkpoint_step':False,
                'dependencies':[],
               }
steps={
    '':None,
}

def makeStepFromDict(key,value):
    return type(key,(StepBase,),value)
