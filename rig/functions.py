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
    def __init__(self, modestate, controller=None):
        self.charBuffer=modestate.charBuffer
        self.keyHandler=modestate.keyHandler
        #I probably do not need to pass key handler to thing outside of inputManager...
        #yep, not used anywhere, but I supose it could be used for submodes... we'll leave it in
        self.setMode=modestate.setMode
        self.updateModeDict=modestate.updateModeDict
        self.__mode__=self.__class__.__name__
        self.keyThread=modestate.keyThread
        self.ctrl=controller
        #self.initController(self.controller)

    def initController(self,controller): #XXX DEPRICATED
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
    def __init__(self, modestate, controller):
        try:
            if controller.__class__.__name__ is not 'clxControl':
                raise TypeError('wrong controller type')
        except:
            raise
        #from clx import clxControl
        super().__init__(modestate,controller)
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
    def __init__(self, modestate, controller):
        try:
            if controller.__class__.__name__ is not 'mccControl':
                raise TypeError('wrong controller type')
        except:
            raise
        #from mcc import mccControl
        super().__init__(modestate,controller) #FIXME this needs better error messages
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
    def __init__(self, modestate, controller):
        try:
            if controller.__class__.__name__ is not 'espControl':
                raise TypeError('wrong controller type')
        except:
            raise
        #from esp import espControl


        super().__init__(modestate,controller)
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

    def printPosDict(self):
        #self.doneCB()
        print(re.sub('\), ',')\r\n',str(self.posDict)))
        return self

    def mark(self): #FIXME
        """mark/store the position of a cell using a character sorta like vim"""
        stdout.write('\rmark:')
        stdout.flush()
        self.keyHandler(1)
        key=self.charBuffer.get()
        #printD('we got the key from charBuffer')
        if key in self.markDict:
            print('Mark %s is already being used, do you want to replace it? y/N'%(key))
            self.keyHandler(1)
            yeskey=self.charBuffer.get()
            if yeskey=='y' or yeskey=='Y':
                self.markDict[key]=self.ctrl.getPos()
                print(key,'=',self.markDict[key])
            else:
                print('No mark set')
        elif key=='\x1b':
            self.unmark()
        else:
            self.markDict[key]=self.ctrl.getPos()
            print(key,'=',self.markDict[key])
        #self.keyHandler(getMark) #fuck, this could be alot slower...
        return self

    def unmark(self):
        #self.doneCB()
        try:
            self.keyHandler(1)
            mark=self.charBuffer.get()
            pos=self.markDict.pop(mark)
            print("umarked '%s' at pos %s"%(mark,pos))
        except:
            pass
        return self

    def gotoMark(self): #FIXME
        #self.doneCB()
        stdout.write('\rgoto:')
        stdout.flush()
        self.keyHandler(1)
        key=self.charBuffer.get()
        if key in self.markDict:
            print('Moved to: ',self.ctrl.BsetPos(self.markDict[key])) #AH HA! THIS is what is printing stuff out as I mvoe FIXME I removed BsetPos at some point and now I need to add it... back? or what
        else:
            print('No position has been set for mark %s'%(key))
        return self

    def printMarks(self):
        """print out all marks and their associated coordinates"""
        print(re.sub('\), ','),\r\n ',str(self.markDict)))
        #self.doneCB()
        return self

    def fakeMove(self):
        #self.doneCB()
        if self.ctrl.sim:
            from numpy import random #only for testing remove later
            a,b=random.uniform(-10,10,2) #DO NOT SET cX or cY manually
            self.ctrl.setPos((a,b))
            print(self.ctrl._cX,self.ctrl._cY)
        else:
            print('Not in fake mode! Not moving!')
        return self

    def getDisp(self):
        """BLOCKING stream the displacement from a set point"""
        #self.doneCB()
        from numpy import sum as npsum #FIXME should these go here!?
        from numpy import array as arr

        if not len(self.markDict):
            self.keyHandler(1)
            key=self.charBuffer.get()
            self.markDict[key]=self.ctrl.getPos()

        dist1=1
        print(list(self.markDict.keys()))
        while self.keyThread.is_alive(): #FIXME may need a reentrant lock here to deal w/ keyboard control
            self.keyHandler(1) #call this up here so the pass through is waiting
            pos=self.markDict.values()
            dist=(npsum((arr(self.ctrl._BgetPos()-arr(list(pos))))**2,axis=1))**.5 #FIXME the problem here is w/ _BgetPos()
            if dist1!=dist[0]:
                #names='%s \r'%(list(self.markDict.keys())) #FIXME sadly, it seems there is no way ;_;
                stdout.write('\r'+''.join(map('{:1.5f} '.format,dist)))
                stdout.flush()
                dist1=dist[0]
            try:
                key=self.charBuffer.get_nowait()
                #FIXME this should go AFTER the other bit to allow proper mode changing
                if key=='q' or key=='\x1b': #this should be dealt with through the key handler...
                    print('\nleaving displacement mode')
                    break
                elif key: #FIXME HOW DOES THIS EVEN WORK!?!??!
                    #printD('breaking shit')
                    try:
                        func=self.modestate.keyActDict[key]
                        if func.__name__ !='getDisp':
                            from threading import Thread
                            a=Thread(target=func)
                            a.start()
                    except:
                        printD('should have keyHandled it')
            except:
                pass
        return self

    def setSpeedDef(self):
        #self.doneCB()
        self.ctrl.setSpeedDefaults()
        return self

    def cleanup(self):
        super().cleanup()
        self.ctrl.cleanup()
        return self

    def setMoveDict(self,moveDict={'w':'up','s':'down','a':'left','d':'right'}):
        self.moveDict=moveDict
        return self

    def move(self): #FIXME this does not work in displacement mode because modestate.key is always i
        key=self.modestate.key
        if key.isupper(): #shit, this never triggers :(
            #printD('upper')
            self.ctrl.move(self.moveDict[key.lower()],.2) #FIXME
        else:
            #printD('lower')
            self.ctrl.move(self.moveDict[key.lower()],.1)
        return self
    def printError(self):
        print('Error:',self.ctrl.getErr().decode('utf-8'))
        return self
    def readProgram(self):
        #self.keyHandler(1)
        #num=self.charBuffer.get()
        print(self.ctrl.readProgram())
        return self


class keyFuncs(kCtrlObj):
    """utility functions eg meta functions such as : cmd and the like"""
    def __init__(self, modestate):
        super().__init__(modestate)
        self.modestate=modestate
    def help(self):
        self.modestate.updateModeDict()
        printFD(self.modestate.helpDict)
        #self.doneCB()
        return self
    def esc(self):
        return 0


def main():
    esp=espFuncs(None,None,None,None)
    #mcc=mccFuncs(None,None,None,None)

if __name__=='__main__':
    main()
