import re
import datetime
import inspect as ins
from sys import stdout
from time import sleep
from tomsDebug import TDB,ploc
import rpdb2
#rpdb2.settrace()

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdbOff=tdb.tdbOff

#file to consolidate all the different functions I want to execute using the xxx.Control classes

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
            from mccpy import mccmsg
            self.ctrl=mccmsg()
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
        from clx import Control
        super().__init__(modestate,Control)
        #self.initController(clxmsg)
        #printD('clx ctrl',self.ctrl)
        #self.clxCleanup=self.cleanup
        self.programDict={}
        #self.wrapDoneCB()
    def readProgDict(self,progDict):
        self.programDict=progDict
        return self

    def getStatus(self):
        status=self.ctrl.GetStatus()
        print(status)
        return self

    def startMembTest(self):
        self.ctrl.StartMembTest(120)
        self.ctrl.StartMembTest(121)
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

    def cleanup(self):
        super().cleanup()
        try:
            self.ctrl.DestroyObject()
            print(self.ctrl.__class__,'handler destroyed')
        except:
            pass
            #print('this this works the way it is supposed to the we should never have to destory the object')


class datFuncs(kCtrlObj): 
    #FIXME this is not working right... it needs to be able to go out and get data on its own... eg when a new abf file appears in the directory it needs to be able to ask for the information to annotate that with... ALTERNATELY if I get the pclamp interface working then I can probably just do everything top down since I will control the entire experiment anyway and can do everything in sequce so dataman can just be a container :D I like that... having the datastructure be passive is probably a good idea, put all the stuff that deals with backup and saving and organization there, just pass data to it, which is sort of how it works right now since all the functions just play back the available data right now
    #dataMan is the UR bot... datFuncs can get things from the dat, but dataMan should exist at the bottom
    #esp since kbdListner is really also another kCtrlObj that coordinates all the ohter ctrl objects, witness that it also needs to readCfg...
    """Put ANYTHING permanent that might be data in here"""
    def __init__(self, modestate):
        super().__init__(modestate)
        self.markDict={}
        self.posDict={}
        self.MCCstateDict={}
        #self.wrapDoneCB()
        self.updateModeDict()
        #FIXME
        #this class should be the one to get data out of dataman
        #dataman should have a method 'saveData' that takes the source class (self) and the data and stores it

    def getUserInputData(self):
        """Sadly there is still some data that I can't automatically collect"""
        #get cell depths FROM SAME STARTING POINT??? measure this before expanding tissue with internal???
        return self



class mccFuncs(kCtrlObj): #FIXME add a way to get the current V and I via... telegraph?
    def __init__(self, modestate):
        from mcc import Control
        super().__init__(modestate,Control)
        #self.initController(mccmsg)
        self.MCCstateDict={}
        #self.wrapDoneCB()
        self.updateModeDict()

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
        from esp import Control
        super().__init__(modestate,Control)
        self.markDict={} #FIXME
        self.posDict={} #FIXME
        #self.initController(npControl)
        self.updateModeDict()
        self.modestate=modestate
        self.setMoveDict()
        #self.event=modestate.event


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
        printD('we got the key from charBuffer')
        if key in self.markDict:
            print('Mark %s is already being used, do you want to replace it? y/N'%(key))
            self.keyHandler(1)
            key=self.charBuffer.get()
            if key=='y':
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
            print('Moved to: ',self.ctrl.BsetPos(self.markDict[key])) #AH HA! THIS is what is printing stuff out as I mvoe
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
            print(self.ctrl.cX,self.ctrl.cY)
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
        while self.keyThread.is_alive():
            self.keyHandler(1) #call this up here so the pass through is waiting
            dist=(npsum((arr(self.ctrl._BgetPos()-arr(list(self.markDict.values()))))**2,axis=1))**.5 #FIXME the problem here is w/ _BgetPos()
            if dist1!=dist[0]:
                stdout.write('\r'+printArray(dist,fixed=1)) #FIXME if the terminal is too narrow it will scroll :(
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

    def move(self):
        key=self.modestate.key
        if key.isupper(): #shit, this never triggers :(
            #printD('upper')
            self.ctrl.move(self.moveDict[key.lower()],.2) #FIXME
        else:
            #printD('lower')
            self.ctrl.move(self.moveDict[key.lower()],.1)
        return self
    def printError(self):
        print(self.ctrl.getErr())
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


def printArray(array, fixed=0): #fixme move this somehwere?
    outstr='['
    for i in array:
        if not fixed:
            outstr+=' %1.5f'%(i)
        else: 
            outstr+=' %1.5F'%(i)
    outstr+=']'
    return outstr


#utility functions

def main():
    esp=espFuncs(None,None,None,None)
    #mcc=mccFuncs(None,None,None,None)

if __name__=='__main__':
    main()
