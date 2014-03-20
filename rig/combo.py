from debug import TDB,ploc
from rig.ipython import embed
from sqlalchemy.orm import object_session #FIXME vs database.imports?
#from database.decorators import Get_newest_id, datafile_maker, new_abf_DataFile, hardware_interface, is_mds, new_DataFile
from database.standards import Get_newest_file
from threading import RLock
from rig.gui import takeScreenCap
from rig.functions import keyRequest,espFuncs,clxFuncs,mccFuncs,datFuncs,trmFuncs,guiFuncs,keyFuncs
from rig.daq import trigger_LED_train
from analysis.online_analysis import abf_basic_vc_analysis


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
        self.mcc.selectMC(hs)
        self.current_headstage=hs

        self.newCell()

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
        self.getBrokenIn()

    def record_abf_full(self,analysis_function=lambda df:None):
        self.record()
        self.c_datafile=self.newDataFile('abf',
                                         self.c_experiment,
                                         self.c_cells)
        self.MCCstateToDataFile()
        self.wait_till_done()
        self.spawn_online_analysis(self.c_datafile,analysis_function)

    def current_steps_01(self): #TODO make this autodetect the number of active chans
        self.allICnoHold()
        self.loadfile('01_current_steps_-100-1000.pro')
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
        wrapped.__name__=function.__name__
        return wrapped
            
    def wrapper_MCC(self,function): #TODO could replace this with a hasattr check?
        """ save the original state of the mcc to return to after everything is done """
        saved_state=self.getMCCState()
        try:
            return function()
        except:
            print('FAILED')
            raise
        finally:
            self.setMCCState(saved_state)


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


        #run the loop
        self.move_loop(loop_func)


    @keyRequest
    def som_pyr_led_exp(self): #FIXME shouldn't it be possible to keep these in their own class?
        self.check_for_cells(2)

        #points for movelists
        points=self.getMarks(['start','one','two','three','four','five']) #TODO get this from spline layout early on?

        #do max-min along cortex to see what we see
        self.ask_moveList('spline',number=2,step_um=1000,points=points) #TODO find a way to save the points AND the movelist, maybe put the movelist in with the cells?

        #run the basic ephys
        self.wrapper_MCC(self.current_steps_01)
        self.wrapper_MCC(self.pair_test)

        #setup the DAQ
        wrapper_DAQ=self.make_DAQ_wrapper(0,4.2,500,100,1,'square')
        print('Is the LED controller on? Are all the filters in the right place? Shutter open? Light block pointing the right direction?')

        #run the maxmin
        wrapper_DAQ(self.wrapper_MCC(self.VC_all_ML))


        #make the movelist for the incremental
        self.makeNewMoveList('spline',number=10,step_um=100,points=points)

        #run the distribution
        wrapper_DAQ(self.wrapper_MCC(self.VC_all_ML))

    def cleanup(self):
        super().cleanup()

