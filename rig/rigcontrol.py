import threading
import warnings
from queue import Queue,Empty

from rig.functions import * #FIXME add __all__ to functions
from rig.keybinds import keyDicts
from rig.dictMan import makeModeDict

from rig.key import keyListener
from rig.clx import clxControl
from rig.esp import espControl
from rig.mcc import mccControl
from rig.trm import trmControl

#TODO need to integrate stuff from experiments, but maybe it makes sense to do that elsewhere somehow?
#since they will need to be integrated with keys to launch them or something

class rigIOMan:
    """Terminal input manager, control the rig from a terminal window"""
    def __init__(self,keyDicts,session_maker, globs):
        self.globs=globs #for passing in to for openIPyton and embed()
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


        self.keyThread=threading.Thread(target=keyListener,args=(self.charBuffer,self.keyHandler,self.cleanup))
        self.keyThread.start()
        #self.keyThread=keyThread

        self.initControllers() #these need charBuffer and keyThread to work
        self.setMode('rig')
        self.Session=session_maker

        #TODO add a way for keys to enter programatic control mode, they will still need keyinput though

    def ipython(self,globs):
        locals().update(globs) #SUPER unkosher but seems safe from tampering
        embed()

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
                print('mode has been set to \'%s\' with keyActDict='%(mode))
                self.currentMode=mode
                return self
            except KeyError:
                if mode != 'init':
                    print('failed to set mode \'%s\' did you write a mode dict for it?'%(mode))
                self.setMode(self.currentMode)
                return self
        else:
            print(self.currentMode)
            return self

    def keyHandler(self,keyRequest=0): #FIXME still confusing
        do = lambda globs: self.ipython(globs)
        self.keyActDict['i'] = lambda: do(self.globs) #FIXME this could explode all over the place
            #FIXME FIXME this is a hack, I don't think this is a good or safe way to do ANYTHING
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
                raise Warning('cleaup for',kFunc,'failed')
        print('done!')

    def initControllers(self): #FIXME
        #load the drivers so that they aren't just hidden in the Funcs
        controllers=clxControl,espControl,mccControl,trmControl
        ctrlDict={}
        for ctrl in controllers:
            try:
                inited=ctrl()
                print('[OK]',inited.__class__.__name__)
                ctrlDict[ctrl.__name__]=inited
            except:
                #warnings.warn('[!] %s failed to init'%ctrl.__name__,UserWarning,0)
                print('[!] %s failed to init'%ctrl.__name__)
     
        ctrlBindingDict={
                'clxControl':clxFuncs,
                'espControl':espFuncs,
                'mccControl':mccFuncs,
                'trmControl':trmFuncs,
        }
        for key in ctrlDict.keys():
            initedFunc=ctrlBindingDict[key](self,ctrlDict[key])
            self.ikFuncDict[initedFunc.__mode__]=initedFunc

        FUNCS=datFuncs,keyFuncs
        for func in FUNCS:
            initedFunc=func(self)
            self.ikFuncDict[initedFunc.__mode__]=initedFunc

        self.updateModeDict() #bind keys to functions
        self.ctrlDict=ctrlDict #FIXME make more explicit
        return ctrlDict

   
def main():
    from database.engines import sqliteMem
    Session=None #TODO
    rigIO=rigIOMan(keyDicts,Session)


if __name__=='__main__':
    main()
