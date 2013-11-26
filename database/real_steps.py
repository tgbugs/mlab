#put all the steps here
from real_dios import * #the steps will use globals to look up the names of the dios
from database.steps import StepBase
from database.real_dios import * #FIXME

#this can proceed without actually having to decide whether to use decorators or not
    #all we need is the names of the functions or the classes


###------
### steps
###------

class Get_at_desired_xy(StepBase):
    """ poop """
    dataio=Get_trmDoneNB
    keepRecord=True
    dependencies=[]

class Get_pia_xy_1(StepBase):
    """ poop """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=['Get_at_desired_xy']

class Get_pia_xy_2(StepBase):
    """ poop """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=['Get_at_desired_xy']

class Get_pia_xy_3(StepBase):
    """ poop """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=['Get_at_desired_xy']

class Get_pia_xy_4(StepBase):
    """ poop """
    dataio=Bind_espXY #FIXME name collisions be here!
    keepRecord=True
    dependencies=['Get_at_desired_xy']

class Bind_pia_xys(StepBase):
    """ poop """
    dataio=Bind_dep_vals
    keepRecord=True
    dependencies=['Get_pia_xy_1','Get_pia_xy_2','Get_pia_xy_3','Get_pia_xy_4']


def load_steps(locs): #FIXME clearly we need a way to flush these babies without updating
    from inspect import isclass
    stepDict={}
    excluded={
        'StepBase',
        'Get',
    }
    for name,locvar in locs.items():
        if isclass(locvar):
            if locvar.__base__ == StepBase and name not in excluded:
                stepDict[name]=locvar
    return stepDict

stepDict=load_steps(locals())

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

def main(locs):
    from IPython import embed
    locals().update(locs)
    embed()

if __name__ == '__main__':
    main(locals())
