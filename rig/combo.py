from debug import TDB,ploc
from rig.ipython import embed
from sqlalchemy.orm import object_session #FIXME vs database.imports?
#from database.decorators import Get_newest_id, datafile_maker, new_abf_DataFile, hardware_interface, is_mds, new_DataFile
from database.standards import Get_newest_file
from threading import RLock
from rig.gui import takeScreenCap
from rig.functions import keyRequest,espFuncs,clxFuncs,mccFuncs,datFuncs,trmFuncs,guiFuncs,keyFuncs
from rig.daq import trigger_LED_train


class allFuncs(espFuncs,clxFuncs,mccFuncs,datFuncs,trmFuncs,guiFuncs,keyFuncs):
    def __init__(self,modestate,clx,esp,mcc,person_id=None,project_id=None):
        super().__init__(modestate,esp=esp,mcc=mcc,clx=clx,person_id=person_id,project_id=project_id) #FIXME one way around the problem is the have the funcs be separate so that they all have their own name spaces??

    def MCCstateToDataFile(self):
        self.c_datafile.mddictlist=self.getMCCState()
        self.session.commit()
        return self #IF THIS WORKS I WILL BUY A HAT AND EAT IT WAIT I ALREADY HAVE A HAT

    def spawn_online_analysis(self,datafile,analysis_function): #TODO
        """ Starts a new thread that runs online analysis"""
        analysis_thread=threading.Thread(target=analysis_function,args=datafile)
        analysis_thread.start()

    def record_abf_full(self,analysis_function=lambda df:None):
        self.record()
        self.c_datafile=self.newDataFile('abf',
                                         self.c_experiment,
                                         self.write_target,
                                         self.c_cells)
        self.MCCstateToDataFile()
        self.wait_till_done()
        self.spawn_online_analysis(self.c_datafile,analysis_function)

    def current_steps_01(self): #TODO make this autodetect the number of active chans
        self.allICnoHold()
        self.loadfile('01_current_steps_-100-1000.pro')
        self.record_abf_full()

    def test_pairs(self):
        self.getKbdHit('Hit a key after adjusting the program so that the cell will spike')
        self.testZtO(-.075)
        self.loadfile('pair_test_0-1.pro')
        self.record_abf_full()
        self.testZtO(-.05)
        self.record_abf_full()

        self.getKbdHit('Hit a key after adjusting the program so that the cell will spike')
        self.testOtZ(-.075)
        self.loadfile('pair_test_1-0.pro')
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

    def make_DAQ_wrapper(minV,maxV,on_ms,off_ms,reps,stepType)
        DAQTask,DAQThrd=trigger_LED_train(minV,maxV,on_ms,off_ms,reps,stepType)
        def wrapped(function):
            """ makes sure the DAQTask gets turned off no matter what"""
            DAQThrd.start() #FIXME need a try/finally here?
            try:
                return function()
            except:
                print('FAILED')
                raise
            finally:
                DAQTask.cleanup()
        wrapped.__name__=function.__name__
        return wrapped
            
    def wrapper_MCC(self,function):
        """ save the original state of the mcc to return to after everything is done """
        saved_state=self.getMCCState()
        try:
            return function()
        except:
            print('FAILED')
            raise
        finally:
            self.setMCCState(saved_state)

    def VC_all_ML(self):
        #set MCC values
        self.allVChold(-.075)
        self.allGain(2)

        #set CLX values
        self.loadfile('01_led_whole_cell_voltage.pro')

        #repeated steps
        def loop_func(pos):
            self.esp.BsetPos(pos)
            self.record_abf_full(vc_basic_analysis)


        #run the loop
        self.move_loop(loop_func)

    @keyRequest
    def som_pyr_led_exp(self):
        #movelist for 

        points=getMarks(['start','one','two','three','four','five']) #TODO get this from spline layout early on?

        #do max-min along cortex to see what we see
        self.ask_moveList('spline',number=2,step_um=1000,points=points) #FIXME

        #run the basic ephys
        self.wrapper_MCC(self.current_steps_01)
        self.wrapper_MCC(self.test_pairs)

        #setup the DAQ
        wrapper_DAQ=self.make_DAQ_wrapper(0,4.2,500,100,1,'square')
        print('Is the LED controller on? Are all the filters in the right place? Shutter open? Light block pointing the right direction?')

        #run the maxmin
        wrapper_DAQ(self.wrapper_MCC(self.VC_all_ML))

        self.ask_moveList('spline',number=10,step_um=100,points=points):

        #run the distribution
        wrapper_DAQ(self.wrapper_MCC(self.VC_all_ML))

    def move_loop(self,loop_func):
        """ Run loop_function at each position in the move list
            loop function should take args """
        move_list=self.move_list[self._current_move_list_index:-1] #tracking for accidental failures
        for pos in move_list:
            loop_func(pos)
            self._current_move_list_index+=1
        print('Move list done')
        self._current_move_list_index=0


    def cleanup(self):
        super().cleanup()



    
