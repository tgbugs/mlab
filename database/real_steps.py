#put all the steps here
from real_dios import * #the steps will use globals to look up the names of the dios
from database.steps import StepBase
from database.real_dios import * #FIXME

#this can proceed without actually having to decide whether to use decorators or not
    #all we need is the names of the functions or the classes

#XXX without the database the code only tells you what to do
    #with the database we can know what /was done/
###------
### basic steps
###------

class Get_checkpoint_test(StepBase):
    """ Testing checkpoints to see if they work """
    dataio=Get_trmDoneNB
    keepRecord=True
    dependencies=[]
    checkpoint_step=True

class Get_done_or_fail(StepBase):
    """ Base step for alternate get done or fail key input """
    dataio=Get_trmDoneORFail
    keepRecord=True
    fail=True


class Get_at_desired_xy(StepBase):
    """ poop """
    dataio=Get_trmDoneNB
    keepRecord=True
    dependencies=[]

class Get_esp_xy(StepBase): #XXX branch steps can help fix this
            #but then what if there are 3 direct descendants we
            #shouldnt call it every time >_< DAMN IT
    """ Get esp x and esp X and (in the darkness) bind them """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=[] #technically Check_esp_on...


###----------
### setup rig
###----------

class Get_pipette_count(StepBase): #use this to see if the pipettes are shitty
    """ How many pipettes did you pull? """
    #dataio=Get_trmCounterNB #TODO
    dataio=Get_trmInt

class Write_pipette_count(StepBase): #TODO
    """ Writes the count to database """
    dependencies=['Get_pipette_count'] #NOTE: this will automatically write the result

class Get_got_patch_tools(StepBase): #XXX placeholder
    """ If you have foreceps, syringes, 2x pasteur pipetts hit space """
    dataio=Get_trmDoneNB

class Check_got_patch_tools(StepBase):
    """ Get 'em all? """
    dataio=Check_deps_done
    dependencies=['Get_got_patch_tools'] #TODO hardwaresteps
    checkpoint_step=True

class Get_got_internal(StepBase):
    """ Check if you have your internal(s). And that they are on ice. Type specced later """
    dataio=Get_trmDoneNB

class Check_chamber_setup(StepBase):
    """ Make sure the chamber is good to go """
    dataio=Check_deps_done
    dependencies=[
        'Got_acsf', #TODO
        'Get_flow_rate', #TODO
    ]

class Get_esp300_calib(StepBase):
    """ Get the calibration for the esp300, move around the grid and measure the displacement """
    dataio=Comp_esp300_calib #TODO should we just use eval() for this? or what...

class Write_esp300_calib(StepBase): #TODO
    """ write dep value to db """
    dependencies=['Get_esp300_calib']

class Check_700B(StepBase): #not needed atm
    """ If you are seeing this then it probably means the 700B is on and mcc is too """
    dataio=Check_700B

class Check_headstage_sanity(StepBase):
    """ Make sure the channels match"""
    dataio=Check_headstages
    #dependencies=['Got_700B_on']

class Check_invitro_rig_setup(StepBase):
    """ everything ready for slice to go on? """
    dataio=Check_deps_done
    checkpoint_step=True #FIXME reset_when_ends_class=experiment
    dependencies=[
        'Check_got_patch_tools',
        'Write_pipette_count',
        'Write_esp300_calib',
        'Get_got_internal',
        'Check_chamber_ready',
        'Check_headstage_sanity',
    ]


###----------------
### slice on to rig
###----------------


class Get_DM_LRUD(StepBase): #FIXME this doesnt even stop to ask for the string!
    """ VITAL for identifying which side was up in the interface chamber 
        get the orientation of the slice dorsal facing and medial facing left or right or up or down
        format should be D,M and then [L,R,U,D],[L,R,U,D]
    """
    dataio=Get_trmString
    keepRecord=True
    dependencies=[]

class Get_slice_thickness_check(StepBase):
    """ Do a second check no slice thickness using the microscope. Make sure to put the harp on first. """
    dataio=Get_trm_dist_um
    keepRecord=True
    dependencies=[] #['Get_DM_LRUD'] #FIXME temporal only...

class Check_slice_on_rig(StepBase):
    """ Slice is on the rig with all deps met. """
    dataio=Check_deps_done
    checkpoint_step=True
    dependencies=[
                  'Check_invitro_rig_setup',
                  'Check_slice_rt_for_30',
                  'Get_DM_LRUD',
                  'Get_slice_thickness_check',
                 ]
    


###-----------------
### get pia position
###-----------------

for i in range(1,6):
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

class Get_pia_xy_5(StepBase):
    """ poop """
    dataio=Bind_espXY
    keepRecord=True
    dependencies=['Get_at_pia_xy_5']

class Bind_pia_xys(StepBase):
    """ poop """
    dataio=Bind_dep_vals
    keepRecord=True
    #checkpoint_step=True #FIXME this needs to have its state tracked but should always be false
    dependencies=['Get_pia_xy_1','Get_pia_xy_2','Get_pia_xy_3','Get_pia_xy_4','Get_pia_xy_5']#,'Get_checkpoint_test']


for i in range(1,6): #TODO make this a function
    at_s='Get_at_target_depth_xy_%s'%i
    xy_s='Get_target_depth_xy_%s'%i
    at_cls=type(at_s,(Get_at_desired_xy,),
                   {'__doc__':' get at %s ith for target depth position'%i})
    xy_cls=type(xy_s,(Get_esp_xy,),
                   {'__doc__':' get %s ith xy for target depth position'%i,
                    'dependencies':['Get_at_target_depth_xy_%s'%i],
                   })
    locals()[at_s]=at_cls
    locals()[xy_s]=xy_cls


class Bind_target_depth_xys(StepBase):
    """ bind all the xys the define the target depth """
    dataio=Bind_dep_vals
    dependencies=['Get_target_depth_xy_%s'%i for i in range(1,6)]

###---------------------------
### compute stimulus positions (from target depth xys)
###---------------------------

class Comp_pia_spline(StepBase):
    dataio=Comp_spline_from_points
    __doc__=dataio.__doc__
    dependencies=['Bind_pia_xys']

class Comp_target_spline(StepBase):
    dataio=Comp_spline_from_points
    __doc__=dataio.__doc__
    dependencies=['Bind_target_depth_xys']

class Comp_stimulus_positions(StepBase):
    dataio=Comp_stimulus_positions
    __doc__=dataio.__doc__
    #dependencies=[]#,'Bind_cells_xys'] HRM! don't even seed it? or do?
    dependencies=['Comp_target_spline','Comp_two_cells_mean_position']#,'Bind_cells_xys'] HRM! don't even seed it? or do?
    #could do wavelet binning based on control data but that would be overkill
    #TODO we want random order not random position

class Comp_two_cells_mean_position(StepBase):
    dataio=Comp_mean_position
    __doc__=dataio.__doc__
    #dependencies=['Got_n_cells'] #FIXME TODO or/any steps???
    dependencies=['Got_two_cells']


###-----------------
### mcc, clx control
###-----------------

class Set_MCC_headstage(StepBase): #TODO
    pass

class Set_MCC_V_hold_off(StepBase): #TODO
    pass

class Set_MCC_auto_pipette_offset(StepBase): #TODO
    pass

class Set_MCC_V_neg60(StepBase): #TODO
    pass

###----------------
### patching logic!
###----------------

class Check_slice_layout_mapped(StepBase): #TODO should be acompanied by a check step that DoneWithPair
    """ Basic prep for any invitro slice experiment is now done. """
    dataio=Check_deps_done
    checkpoint_step=True
    dependencies=['Comp_stimulus_positions',]

class Got_cell_contact(StepBase):
    """ Bumped up against single cell, aka positive pressure released """
    dataio=Get_trmDoneORFail
    fail=True

class Got_giga_seal(StepBase):
    """ Giga seal on a single cell """
    dataio=Get_trmDoneORFail #TODO read from mcc resistance
    fail=True

class Got_broken_in(StepBase):
    """ Broken in to a single cell """
    dataio=Get_trmDoneORFail #TODO read from mcc or clx?
    fail=True

class Got_two_cells(StepBase):
    """ Both cells have been patched, time for DATA """
    dataio=Get_trmDoneORFail
    fail=True

class Check_access(StepBase): #TODO
    """ Check to make sure we still have access, not a show stopper since sometimes we get stuff back """
    dependencies=[] #FIXME damn it datafiles
    dependencies=['Read_datafiles']


class DONE_with_cell(StepBase): #FIXME damn it this does not scale with N ;_; well, you could just add 4 end steps?
    """ done with one of multiple cells :/ how to do w/o having n classes :/ """
    #dependencies=['Got_data','RESET_patch_nodes']

class DONE_with_all_cells(StepBase): #FIXME reset one? or reset both?
    """ all the data from this pair of neurons is done """
    dependencies=['Got_data','RESET_patch_nodes']

class ALL_DONE_invitro_LED_control(StepBase):
    """ Totally done with the control experiment, this is actually the base step for LED controls """
    dataio=Get_trmDoneORFail

###-----------------
### Data acquisition
###-----------------

class Write_cell_record(StepBase):
    """ add a cell record to the database """

class Set_all_MCC_V_neg75(StepBase):
    """ hold at -75mV to isolate excitatory current """

class Set_CLX_protocol_dual_led_pulse(StepBase):
    """ load the clampex protocol """

class Set_esp_xy_position(StepBase):
    """ move the scope to a specific xy """

class Set_CLX_run_protocol(StepBase):
    """ run the protocol and collect the data """
    dependencies=[]

class Get_datafile_name(StepBase):
    """ get the name of the datafile """
    dataio=Get_newest_abf
    dependencies=['Get_clx_savedir_url','Set_CLX_run_protocol']

class Get_clx_savedir_url(StepBase):
    dataio=Get_clx_savedir_url
    __doc__=dataio.__doc__
    dependencies=[]


class Write_datafile_record(StepBase):
    """ write the datafile entry to the database """
    dataio=Write_clx_datafile
    dependencies=['Get_clx_savedir_url','Get_datafile_name']
    def format_dep_returns(self,**kwargs):
        return kwargs['Get_datafile_name']

class Write_datafile_metadata(StepBase):
    """ write the position to  datafile metadata """
    dataio=Write_datafile_metadata
    dependencies=['Get_esp_xy','Write_datafile_record']
    #TODO use last_getter_id to pass metadatasource?
    def format_dep_returns(self,**kwargs):
        return kwargs['Get_esp_xy']



###------------------------
### Subject managment steps
###------------------------

class Set_WriteTarget(StepBase): #TODO this will be the base for algorithmic write target setting but for now could just query for them and confirm and/or creat new
    """ set the write target for everything """


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
