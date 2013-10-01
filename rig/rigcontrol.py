from rig.functions import * #FIXME add __all__ to functions
from queue import Queue,Empty
from rig.dictMan import *
from rig.key import keyListener
from inspect import currentframe
import threading
from debug import TDB,ploc
from keybinds import keyDicts

from rig.clx import clxControl
from rig.esp import espControl
from rig.mcc import mccControl
try:
    import rpdb2
except:
    pass

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdbOff=tdb.tdbOff

class termInputMan:
    """Terminal input manager, control the rig from a terminal window"""
    def __init__(self,keyDicts):
        self.keyDicts=keyDicts

        self.ikFuncDict={}
        self.modeDict={}
        self.helpDict={}
        self.keyActDict={}

        self.keyRequest=0
        self.key=None #genius! now we don't even need have the stupid pass through!
        self.currentMode='init'

        def esc():return 1
        self.keyActDict['\x1b']=esc

        self.charBuffer=Queue()

        keyThread=threading.Thread(target=keyListener,args=(self.charBuffer,self.keyHandler,self.cleanup))
        keyThread.start()
        self.keyThread=keyThread

        #TODO add a way for keys to enter programatic control mode, they will still need keyinput though

    def updateModeDict(self):
        self.helpDict,self.modeDict=makeModeDict(self.ikFuncDict,*keyDicts.values())
        try:
            self.keyActDict.update(self.modeDict[self.currentMode])
        except KeyError:
            pass
        return self

    def setMode(self,mode=None):
        """poop"""
        if mode:
            try:
                self.keyActDict=self.modeDict[mode] #where mode is just defined by __mode__
                printD('mode has been set to \'%s\' with keyActDict='%(mode))
                self.currentMode=mode
                return self
            except KeyError:
                if mode != 'init':
                    printD('failed to set mode \'%s\' did you write a mode dict for it?'%(mode))
                self.setMode(self.currentMode)
                return self
        else:
            print(self.currentMode)
            return self

    def keyHandler(self,keyRequest=0): #FIXME still confusing
        if keyRequest:
            self.keyRequest=1
            return 1
        if self.keyRequest:
            self.key=self.charBuffer.queue[0] #TODO we can use this everywhere! no need for key requests!
            self.keyRequest=0
            return 1 #if a request is in then return before getting the function from the queue
        self.key=self.charBuffer.get() #FIXME self.key needs to update no matter what...
        try:
            function=self.keyActDict[self.key]
            if function:
                calledThread=threading.Thread(target=function)
                calledThread.start()
        except (KeyError, TypeError, Empty) as e:
            pass
        return 1

    def cleanup(self):
        for kFunc in self.ikFuncDict.values():
            try:
                kFunc.cleanup()
            except:
                printD('cleaup for',kFunc,'failed')
        print('done!')


def initControllers(termInputMan,progInputMan=None):
    #load the drivers so that they aren't just hidden in the Funcs
    controllers=clxControl,espControl,mccControl
    ctrlDict={}
    for ctrl in controllers:
        try:
            inited=ctrl()
            print(inited.__class__.__name__)
            ctrlDict[ctrl.__name__]=inited
        except:
            print('%s failed to init'%ctrl.__name__)
 
    ctrlBindingDict={
            'clxControl':clxFuncs,
            'espControl':espFuncs,
            'mccControl':mccFuncs
    }
    for key in ctrlDict.keys():
        initedFunc=ctrlBindingDict[key](termInputMan,ctrlDict[key])
        termInputMan.ikFuncDict[initedFunc.__mode__]=initedFunc

    FUNCS=datFuncs,keyFuncs
    for func in FUNCS:
        initedFunc=func(termInputMan)
        termInputMan.ikFuncDict[initedFunc.__mode__]=initedFunc

    termInputMan.updateModeDict() #bind keys to functions

   
def main():
    termIO=termInputMan(keyDicts)
    initControllers(termIO)

    #once all the startup threads are done, try to set the mode to rig
    while 1:
        try:
            termIO.setMode('rig')
            break
        except:
            pass


if __name__=='__main__':
    main()
