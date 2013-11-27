#put all the steps here
from real_dios import * #the steps will use globals to look up the names of the dios
from database.steps import StepBase
from database.real_dios import * #FIXME

#this can proceed without actually having to decide whether to use decorators or not
    #all we need is the names of the functions or the classes


###------
### steps
###------

class Get_checkpoint_test(StepBase):
    """ Testing checkpoints to see if they work """
    dataio=Get_trmDoneNB
    keepRecord=True
    dependencies=[]
    checkpoint_step=True

class Get_at_desired_xy(StepBase):
    """ poop """
    dataio=Get_trmDoneNB
    keepRecord=True
    dependencies=[]

for i in range(1,5):
    cls=type('Get_at_pia_xy_%s'%i,(Get_at_desired_xy,),{'__doc__':' Get_at_desired_xy for pia_xy_%s'%i}) #FIXME yes, I can see how to automate this now though we probably don't want to save it as a separate step...
        #which sucks because of how intertwined the Step.step_id is with all this >_<
    locals()['Get_at_pia_xy_%s'%i]=cls


class Get_pia_xy_1(StepBase):
    """ poop """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=['Get_at_pia_xy_1'] #FIXME if collision detect and it is a multi time even
         #the we could automate by adding a step using the rev_dep name ie get_pia_xy_1...
         #seems reaonsable

class Get_pia_xy_2(StepBase):
    """ poop """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=['Get_at_pia_xy_2']

class Get_pia_xy_3(StepBase):
    """ poop """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=['Get_at_desired_xy']
    dependencies=['Get_at_pia_xy_3']

class Get_pia_xy_4(StepBase):
    """ poop """
    dataio=Bind_espXY #FIXME name collisions be here!
    keepRecord=True
    dependencies=['Get_at_pia_xy_4']

class Bind_pia_xys(StepBase):
    """ poop """
    dataio=Bind_dep_vals
    keepRecord=True
    dependencies=['Get_pia_xy_1','Get_pia_xy_2','Get_pia_xy_3','Get_pia_xy_4']#,'Get_checkpoint_test']

class Get_DM_LRUD(StepBase):
    """ get the orientation of the slice dorsal facing and medial facing left or right or up or down """
    dataio=Get_trmString
    keepRecord=True
    dependencies=['Get_slice_on_rig']#,'Get_DV_LR','']

class Set_WriteTarget(StepBase): #TODO this will be the base for algorithmic write target setting but for now could just query for them and confirm and/or creat new
    pass


def load_steps(locs): #FIXME clearly we need a way to flush these babies without updating
    from inspect import isclass
    stepDict={}
    excluded={
        'StepBase',
        'Get',
    }
    for name,locvar in locs.items():
        if isclass(locvar):
            if StepBase in locvar.__mro__ and name not in excluded:
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
