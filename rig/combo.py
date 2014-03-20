from debug import TDB,ploc
from rig.ipython import embed
from sqlalchemy.orm import object_session #FIXME vs database.imports?
#from database.decorators import Get_newest_id, datafile_maker, new_abf_DataFile, hardware_interface, is_mds, new_DataFile
from database.standards import Get_newest_file
from threading import RLock
from rig.gui import takeScreenCap
from rig.functions import keyRequest,espFuncs,clxFuncs,mccFuncs,datFuncs,trmFuncs,guiFuncs
from rig.daq import trigger_LED_train


class allFuncs(espFuncs,clxFuncs,mccFuncs,datFuncs,trmFuncs,guiFuncs):
    def __init__(self,modestate,clx,esp,mcc,person_id=None,project_id=None):
        super().__init__(modestate,esp=esp,mcc=mcc,clx=clx,person_id=person_id,project_id=project_id) #FIXME one way around the problem is the have the funcs be separate so that they all have their own name spaces??

    def MCCstateToDataFile(self):
        self.c_datafile.mddictlist=self.getMCCState()
        self.session.commit()
        return self #IF THIS WORKS I WILL BUY A HAT AND EAT IT WAIT I ALREADY HAVE A HAT

    def record_abf_full(self):
        self.record()
        self.c_datafile=self.newDataFile('abf',
                                         self.c_experiment,
                                         self.write_target,
                                         self.c_cells)
        self.MCCstateToDataFile()
        self.wait_till_done()

    def test_pairs(self):
        self.loadfile('pair_test_0-1.pro')
        self.getKbdHit('Hit a key after adjusting the program so that the cell will spike')
        self.testZtO(-.075)
        self.record_abf_full()
        self.testZtO(-.05)
        self.record_abf_full()

        self.loadfile('pair_test_1-0.pro')
        self.getKbdHit('Hit a key after adjusting the program so that the cell will spike')
        self.testOtZ(-.075)
        self.record_abf_full()
        self.testOtZ(-.05)
        self.record_abf_full()

        self.allIeZ()
        

    #self.loadfile('current_step_-100-1000.pro')


    @keyRequest
    def paired_led_vc(self):
        #setup led
        DAQTask,DAQThrd=trigger_LED_train(0,4.2,500,100,1,'square')
        DAQThrd.start() #FIXME need a try/finally here?

        #move dict?
        try: #need this to make sure daq thread exists nomatter what
            if self.getBool('Hit space if you want to make a new movelist'):
                if len(self.markDict) < 5:
                    print(self.markDict)
                    print('You don\' have enough marks! Go make some!')
                    DAQTask.cleanup()
                    return None
                else:
                    self.makeNewMoveList('spline',number=10,step_um=100)
                    #except:
                        #DAQTask.cleanup() 
                        #print('Creation failed!')
                        #return None


            #setup holding values
            self.allVChold(-.075)
            self.allGain(2)
            self.loadfile('01_led_whole_cell_voltage.pro')

            def loop_func(pos):
                self.esp.BsetPos(pos)
                self.record_abf_full()

            self.move_loop(loop_func)
        except:
            raise
        finally: #return defaults no matter what
            self.allVChold(-.06)
            self.allGain(1)

            DAQTask.cleanup()
        #DAQThrd.join() #see if we need this?

    def move_loop(self,loop_func):
        """ loop function should take args """

        move_list=self.move_list[self._current_move_list_index:-1] #tracking for accidental failures
        for pos in move_list:
            loop_func(pos)
            self._current_move_list_index+=1
        print('Move list done')
        self._current_move_list_index=0





    
