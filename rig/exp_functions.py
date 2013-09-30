import re
import datetime
import inspect as ins
from sys import stdout
from time import sleep
from debug import TDB,ploc
try:
    import rpdb2
except:
    pass

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdbOff=tdb.tdbOff

#file to consolidate all the different functions I want to execute using the xxx.Control classes
#TODO this file needs a complete rework so that it can pass data to the database AND so that it can be used by keyboard AND so that it can be used by experiment scripts... means I may need to split stuff up? ;_;
#TODO rig control vs experiment control... these are technically two different 'modes' one is keyboard controlled the other is keyboard initiated...
#TODO ideally I want to do experiments the same way every time instead of allowing one part here and another there which is sloppy so those are highly ordered...
#TODO BUT I need a way to fix things, for example if the slice moves and I need to recalibrate the slice position (FUCK, how is THAT going to work out in metadata)

#TODO all of these are configured for terminal output only ATM, ideally they should be configged by whether they are called from keyboard or from experiment... that seems... reasonable??! not very orthogonal...
#mostly because when I'm running an experiment I don't want to accientally hit something or cause an error

#TODO split in to send and recieve?!?

#TODO datasource/expected datasource mismatch

class kCtrlObj:
    """key controller object"""
    def __init__(self, modestate, controller=lambda:None):
        self.charBuffer=modestate.charBuffer
        self.keyHandler=modestate.keyHandler
        #I probably do not need to pass key handler to thing outside of inputManager...
        #yep, not used anywhere, but I supose it could be used for submodes... we'll leave it in
        self.setMode=modestate.setMode
        self.updateModeDict=modestate.updateModeDict
        self.__mode__=self.__class__.__name__
        self.keyThread=modestate.keyThread
        self.ikCtrlDict=modestate.ikCtrlDict
        self.controller=controller
        self.initController(self.controller)

    def reloadControl(self): #this wont work because it wont write or something....
        printD('reiniting controller')
        rpdb2.setbreak()
        try:
            self.ctrl.cleanup()
            del(self.ctrl)
            from mcc import mccControl
            self.ctrl=Control()
            self.ikCtrlDict[self.__mode__]=self
            self.updateModeDict()
        except:
            printD('FAILURE')
            raise IOError
        return self

    def initController(self,controller):
        try:
            self.ctrl=controller()
            print('[OK]',controller.__name__,'started')
        except:
            print('[!] **LOAD ERROR**',controller.__name__,'not started, will listen for start')
            self.ctrl=lambda:None
            from threading import Thread
            #self.pollThrd=Thread(target=self.pollForCtrl,args=(controller,))
            #self.pollThrd.start()
        self.ikCtrlDict[self.__mode__]=self
        self.updateModeDict()
    
    def pollForCtrl(self,controller): #FIXME maybe we SHOULD do this here since these are more tightly integrated with modestate
        while self.keyThread.is_alive():
            try:
                self.ctrl=controller()
                printD(self)
                print('[OK]',controller.__name__,'started')
                #printD(self.__mode__)
                #self.ikCtrlDict[self.__mode__]=self
                self.updateModeDict()
                break
            except:
                sleep(2)


    def wrapDoneCB(self):
        class wrap:
            def __init__(self,call,pre=lambda:None,post=lambda:None):
                self.start=pre
                self.do=call
                self.stop=post
            def go(self,*args):
                #printD('wat')
                self.start()
                out=self.do(*args)
                self.stop()
                return out
        excluded=['cleanup','__init__','doneCB','readProgDict','updateModeDict','setMode']
        mems=ins.getmembers(self)
        funcs=[func for func in mems if ins.ismethod(func[1]) and func[0] not in excluded]
        #printFD(funcs)
        for tup in funcs:
            setattr(self,tup[0],wrap(tup[1],self.doneCB).go)

    def cleanup(self):
        pass


class clxFuncs(kCtrlObj):
    def __init__(self, modestate):
        from clx import clxControl
        super().__init__(modestate,clxControl)
        #self.initController(clxmsg)
        #printD('clx ctrl',self.ctrl)
        #self.clxCleanup=self.cleanup
        self.programDict={}
        #self.wrapDoneCB()

    #class only
    def readProgDict(self,progDict):
        self.programDict=progDict
        return self

    def cleanup(self):
        super().cleanup()
        try:
            self.ctrl.DestroyObject()
            print(self.ctrl.__class__,'handler destroyed')
        except:
            pass
            #print('this this works the way it is supposed to the we should never have to destory the object')


    #input with output
    def getStatus(self,outputs): #TODO outputs... should be able to output to as many things as I want... probably should be a callback to simplify things elsewhere? no?!?!
        status=self.ctrl.GetStatus()
        print(status)
        return self

    def load(self,key=None):
        if not key:
            print('Please enter the program to load')
            self.keyHandler(1)
            key=self.charBuffer.get()
        try:
            path=self.programDict[key]
            #printD(path)
            self.ctrl.LoadProtocol(path.encode('ascii'))
        except:
            print('Program not found')
            raise

        return self

    #input only
    def startMembTest(self):
        self.ctrl.StartMembTest(120)
        self.ctrl.StartMembTest(121)
        return self

class datFuncs(kCtrlObj): 
    #interface with the database TODO this should be able to run independently?
    """Put ANYTHING permanent that might be data in here"""
    def __init__(self, modestate):
        #from database.models import * #DAMNIT FIXME
        super().__init__(modestate)
        self.markDict={}
        self.posDict={}
        self.MCCstateDict={}
        #self.wrapDoneCB()
        self.updateModeDict()
        #FIXME
        #this class should be the one to get data out of dataman
        #dataman should have a method 'saveData' that takes the source class (self) and the data and stores it

    def newExperiment(self):
        return self

    def newCell(self):
        return self

    def newSlice(self):
        return self

    def addMetaData(self):
        return self

    def addDataFile(self): #FIXME not sure this should go here...
        return self

    def getUserInputData(self):
        """Sadly there is still some data that I can't automatically collect"""
        #get cell depths FROM SAME STARTING POINT??? measure this before expanding tissue with internal???
        return self


class mccFuncs(kCtrlObj): #FIXME add a way to get the current V and I via... telegraph?
    def __init__(self, modestate):
        from mcc import mccControl
        super().__init__(modestate,mccControl) #FIXME this needs better error messages
        #self.initController(mccmsg)
        self.MCCstateDict={}
        #self.wrapDoneCB()
        self.updateModeDict()
        
        #associated metadata sources
        self.state1DataSource=None


    def inpWait(self):
        #wait for keypress to move to the next program, this may need to spawn its own thread?
        print('HIT ANYTHING TO ADVANCE! (not the dog, that could end poorly)')
        self.keyHandler(1)
        self.charBuffer.get()
        return self

    def getState(self): #FIXME this function and others like it should probably be called directly by dataman?
        printD('hMCCmsg outer',self.ctrl.hMCCmsg)
        def base():
            state.append(self.ctrl.GetHoldingEnable())
            state.append(self.ctrl.GetHolding())
            state.append(self.ctrl.GetPrimarySignal())
            state.append(self.ctrl.GetPrimarySignalGain())
            state.append(self.ctrl.GetPrimarySignalLPF())
            state.append(self.ctrl.GetPipetteOffset())

        def vc():
            base()
            state.append(self.ctrl.GetFastCompCap())
            state.append(self.ctrl.GetSlowCompCap())
            state.append(self.ctrl.GetFastCompTau())
            state.append(self.ctrl.GetSlowCompTau())
            state.append(self.ctrl.GetSlowCompTauX20Enable())

        def ic():
            base()
            state.append(self.ctrl.GetBridgeBalEnable())
            state.append(self.ctrl.GetBridgeBalResist())

        def iez():
            base()

        modeDict={0:vc,1:ic,2:iez}
        stateList=[]
        for i in range(self.ctrl.mcNum):
            self.ctrl.selectMC(i)
            state=[] #FIXME: make this a dict with keys as the name of the value? eh would probs complicate
            state.append(i) #might be suprflulous but it could simplify the code to read out stateList
            mode=self.ctrl.GetMode()
            state.append(mode)
            modeDict[mode]()
            stateList.append(state)
            print(state)

        self.MCCstateDict[datetime.datetime.utcnow()]=stateList
        return self

    def printMCCstate(self):
        print(re.sub('\), ',')\r\n',str(self.MCCstateDict)))
        return self

    def setMCState(self,MC=None,Mode=None,Holding=None,HoldingEnable=None): #TODO
        #FIXME all of the experiment logic needs to be stored in one place instead of hidden in 10 files
        #selectMC,SetMode,SetHolding,SetHoldingEnable,
        #self.ctrl.selectMC()
        return self

    def allIeZ(self):
        self.ctrl.selectMC(0)
        self.ctrl.SetMode(2)
        self.ctrl.selectMC(1)
        self.ctrl.SetMode(2)
        return self
    def allVCnoHold(self):
        #try:
        self.ctrl.selectMC(0)
        self.ctrl.SetMode(0)
        self.ctrl.SetHoldingEnable(0)
        self.ctrl.selectMC(1)
        self.ctrl.SetMode(0)
        self.ctrl.SetHoldingEnable(0)
        #except:
            #raise BaseException
        return self
    def allVChold_60(self):
        self.ctrl.selectMC(0)
        self.ctrl.SetMode(0)
        self.ctrl.SetHolding(-.06)
        self.ctrl.SetHoldingEnable(1)
        self.ctrl.selectMC(1)
        self.ctrl.SetMode(0)
        self.ctrl.SetHolding(-.06)
        self.ctrl.SetHoldingEnable(1)
        return self
    def allICnoHold(self):
        self.ctrl.selectMC(0)
        self.ctrl.SetMode(1)
        self.ctrl.SetHoldingEnable(0)
        self.ctrl.selectMC(1)
        self.ctrl.SetMode(1)
        self.ctrl.SetHoldingEnable(0)
        return self
    def testZtO_75(self):
        self.ctrl.selectMC(0)
        self.ctrl.SetMode(1)
        self.ctrl.SetHoldingEnable(0)
        self.ctrl.selectMC(1)
        self.ctrl.SetMode(0)
        self.ctrl.SetHolding(-.075)
        self.ctrl.SetHoldingEnable(1)
        return self
    def testOtZ_75(self):
        self.ctrl.selectMC(0)
        self.ctrl.SetMode(0)
        self.ctrl.SetHolding(-.075)
        self.ctrl.SetHoldingEnable(1)
        self.ctrl.selectMC(1)
        self.ctrl.SetMode(1)
        self.ctrl.SetHoldingEnable(0)
        return self
    def zeroVChold_60(self):
        self.ctrl.selectMC(0)
        self.ctrl.SetMode(0)
        self.ctrl.SetHolding(-.06)
        self.ctrl.SetHoldingEnable(1)
        return self
    def oneVChold_60(self):
        self.ctrl.selectMC(1)
        self.ctrl.SetMode(0)
        #self.ctrl.poops(1) #awe, this is broken now due to something
        self.ctrl.SetHolding(-.06)
        self.ctrl.SetHoldingEnable(1)
        return self
    def cleanup(self):
        super().cleanup()
        try:
            self.ctrl.DestroyObject()
            print(self.ctrl.__class__,'handler destroyed')
        except:
            pass


class espFuncs(kCtrlObj):
    def __init__(self, modestate):
        from esp import espControl
        super().__init__(modestate,espControl)
        self.markDict={} #FIXME
        self.posDict={} #FIXME
        #self.initController(npControl)
        self.updateModeDict()
        self.modestate=modestate
        self.setMoveDict()
        #self.event=modestate.event
        
        #associated metadatasources:
        self.EspXDataSource=None
        self.EspYDataSource=None

    def getPos(self):
        #may want to demand a depth input (which can be bank)
        #try:
        pos=self.ctrl.getPos()
        #self.doneCB()
        self.posDict[datetime.datetime.utcnow()]=pos #FIXME dat should handle ALL of this internally
        print(pos)
        #except:
            #printD('oops')
            #raise
        return self

    def setPos(self,x,y):
        self.ctrl.setPos((x,y)) #FIXME may need BsetPos

    def cleanup(self):
        super().cleanup()
        self.ctrl.cleanup()
        return self


def main():
    esp=espFuncs(None,None,None,None)
    #mcc=mccFuncs(None,None,None,None)

if __name__=='__main__':
    main()
