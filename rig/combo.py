from debug import TDB,ploc
from rig.ipython import embed
from sqlalchemy.orm import object_session #FIXME vs database.imports?
#from database.decorators import Get_newest_id, datafile_maker, new_abf_DataFile, hardware_interface, is_mds, new_DataFile
from database.standards import Get_newest_file
from threading import RLock, Thread
from rig.gui import takeScreenCap
from rig.functions import keyRequest,espFuncs,clxFuncs,mccFuncs,datFuncs,trmFuncs,guiFuncs,keyFuncs
from rig.daq import trigger_LED_train
from analysis.online_analysis import abf_basic_vc_analysis
from time import sleep
import numpy as np #FIXME move this to an analysis file or a calcs file

#FIXME what we REALLY REALLY want, is some way to take allFuncs and let it provide a base for scripts that can then be modified ON THE FLY and run again... basically want to hook in to the existing session and still be able to modify the code... not sure if that is possible?


class allFuncs(espFuncs,clxFuncs,mccFuncs,datFuncs,trmFuncs,guiFuncs,keyFuncs):
    def __init__(self,modestate,clx,esp,mcc,person_id=None,project_id=None):
        self.session=modestate.Session()
        super().__init__(modestate,esp=esp,mcc=mcc,clx=clx,person_id=person_id,project_id=project_id) #FIXME one way around the problem is the have the funcs be separate so that they all have their own name spaces??
        self.update_headstages()

    ##
    # combo init stuff that needs to go last to prevent EXPLOOOSIONS
    ##
    def update_headstages(self):
        for cell in self.c_cells:
            self.headstage_state[cell.headstage]=cell.id

    ##
    # functions
    ##
    def MCCstateToDataFile(self):
        self.c_datafile.mddictlist=self.getMCCState()
        self.session.commit()
        return self #IF THIS WORKS I WILL BUY A HAT AND EAT IT WAIT I ALREADY HAVE A HAT

    def spawn_online_analysis(self,datafile,analysis_function): #TODO
        """ Starts a new thread that runs online analysis"""
        analysis_thread=Thread(target=analysis_function,args=(datafile,))
        analysis_thread.start()

    def newMetaData(self,value,targets,metadatasource,abs_error=None):
        if hasattr(targets,'__iter__'):
            for target in targets:
                new_md=target.MetaData(value,target.id,metadatasource.id,abs_error)
                self.add_com_sess(new_md)
        else:
            new_md=targets.MetaData(value,targets.id,metadatasource.id,abs_error)
            self.add_com_sess(new_md)

    @keyRequest
    def get_cell(self):
        hs=self.getBool('Hit space for HS 1 or anything else for HS 0') 

        if self.headstage_state[hs]:
            raise IOError('That headstage is already in use!') #FIXME

        self.mcc.selectMC(hs)
        self.current_headstage=hs

        self.newCell()
        self.headstage_state[hs]=self.c_target.id #FIXME make this explicit instead of hiding it all over the place
        self.c_target.headstage=int(hs) #FIXME extremely undesireable way to do this
        self.session.commit()

        #FIXME convert c_cells to a dict where the keys are headstages, that should make getting the data in much easier!

        print('current target:',self.c_target)
        position=self.getPos() #TODO
        self.newMetaData(position,self.c_target,self.getPos.mds)
        depth=self.getDistance_um()
        self.newMetaData(depth,self.c_target,self.getDistance_um.mds)

        self.setVCholdOFF()
        self.setVChold(-.06)
        self.autoOffset()
        self.autoCap()
        self.getKbdHit('hit a key when you bump a cell')
        self.setVCholdON()
        self.getBrokenIn() #FIXME make sure to set everything back to 0!

    def getPosWrite(self):
        self.newMetaData(self.getPos(),self.c_target,self.getPos.mds)

    def record_abf_full(self,analysis_function=lambda df:None):
        self.record()
        self.c_datafile=self.newDataFile('abf',
                                         self.c_experiment,
                                         self.c_cells)
        self.c_target=self.c_datafile
        self.MCCstateToDataFile()
        self.wait_till_done()
        self.spawn_online_analysis(self.c_datafile,analysis_function)

    def record_abf_pos(self):
        self.record_abf_full()
        self.getPosWrite()

    def current_steps_01(self): #TODO make this autodetect the number of active chans
        self.allICnoHold()
        self.loadfile('01_current_step_-100-1000.pro') #spelling as usual
        self.record_abf_full()

    def check_for_cells(self,n=1):
        #check that we have two cells!
        if len(self.c_cells) != n:
            raise IOError('I\'m sorry Dave. I can\'t do that.')
        else:
            return n

    @keyRequest
    def pair_test(self):
        self.check_for_cells(2)

        self.testZtO(-.075)
        self.loadfile('pair_test_0-1.pro')
        self.getKbdHit('Hit a key after adjusting the program so that the cell will spike')
        self.record_abf_full()
        self.testZtO(-.05)
        self.record_abf_full()

        self.testOtZ(-.075)
        self.loadfile('pair_test_1-0.pro')
        self.getKbdHit('Hit a key after adjusting the program so that the cell will spike')
        self.record_abf_full()
        self.testOtZ(-.05)
        self.record_abf_full()

        self.allIeZ()

    @keyRequest
    def ask_moveList(self,move_pattern=None,number=None,step_um=None,points=[]):
        if self.getBool('Hit space if you want to make a new movelist'):
            if len(self.markDict) < 5:
                print(self.markDict)
                raise AttributeError('You don\' have enough marks! Go make some!')
            else:
                try:
                    self.makeNewMoveList(move_pattern,number,step_um,points)
                except:
                    raise

    @staticmethod
    def make_DAQ_wrapper(minV,maxV,on_ms,off_ms,reps,stepType):
        DAQTask,DAQThrd=trigger_LED_train(minV,maxV,on_ms,off_ms,reps,stepType)
        def wrapped(function):
            """ makes sure the DAQTask gets turned off no matter what"""
            DAQThrd.start() #FIXME need a try/finally here?
            try:
                return function()
            except:
                print('Running protocol FAILED!')
                raise
            finally:
                DAQTask.cleanup()
        #wrapped.__name__=function.__name__ #:(
        return wrapped
            
    def make_MCC_wrapper(self,function): #TODO could replace this with a hasattr check?
        """ save the original state of the mcc to return to after everything is done """
        def wrapped():
            saved_state=self.getMCCState()
            try:
                return function()
            except:
                print('FAILED')
                raise
            finally:
                self.setMCCState(saved_state)
        return wrapped


    def move_loop(self,loop_func):
        """ Run loop_function at each position in the move list
            loop function should take args """
        move_list=self.move_list[self._current_move_list_index:-1] #tracking for accidental failures
        for pos in move_list:
            loop_func(pos)
            self._current_move_list_index+=1
        print('Move list done')
        self._current_move_list_index=0

    def VC_all_ML(self):
        #set MCC values
        self.allVChold(-.075)
        self.allGain(2)

        #set CLX values
        self.loadfile('01_led_whole_cell_voltage.pro')

        #repeated steps
        def loop_func(pos):
            self.esp.BsetPos(pos)
            self.record_abf_full(abf_basic_vc_analysis)
            self.newMetaData(self.getPos(),self.c_datafile,self.getPos.mds)


        #run the loop
        self.move_loop(loop_func)

    def getMeanCellsPos(self): #TODO anaFuncs??? move this...
        plist=[c.position for c in self.c_cells]
        return tuple(np.mean( np.vstack(plist) , axis=0 ))

    @keyRequest
    def som_pyr_led_exp(self): #FIXME shouldn't it be possible to keep these in their own class?
        self.check_for_cells(2)

        #set the start as the average of the two cell positions
        start=self.getMeanCellsPos()
        points=[start] #pretty sure this works out because 'start' is just moved up to the spline
        #points for movelists
        guides=self.getMarks(['one','two','three','four','five']) #TODO get this from spline layout early on?
        points.extend(guides)

        #do max-min along cortex to see what we see
        self.ask_moveList('spline',number=2,step_um=1000,points=points) #TODO find a way to save the points AND the movelist, maybe put the movelist in with the cells?

        #setup the basic ephys #TODO can just make this its own function
        run_current=self.make_MCC_wrapper(self.current_steps_01)
        run_pairs=self.make_MCC_wrapper(self.pair_test)

        #setup the DAQ
        wrapper_DAQ=self.make_DAQ_wrapper(0,4.2,500,100,1,'square')
        print('Is the LED controller on? Are all the filters in the right place? Shutter open? Light block pointing the right direction?')
        #setup the MCC
        wrapper_MCC=self.make_MCC_wrapper(self.VC_all_ML)


        #run the basic ephys
        run_current()
        run_pairs()

        #run the maxmin
        wrapper_DAQ(wrapper_MCC)

        #make the movelist for the incremental
        self.makeNewMoveList('spline',number=10,step_um=100,points=points)

        #run the distribution
        wrapper_DAQ=self.make_DAQ_wrapper(0,4.2,500,100,1,'square') #have to remake the wrapper because the thread ends
        wrapper_DAQ(wrapper_MCC)

        #TODO need a way to recover from crashes without havning to do everything again

    def cleanup(self):
        super().cleanup()

