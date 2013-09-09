from functions import *
from queue import Queue,Empty
from dictMan import *
from key import keyListener
from inspect import currentframe
import threading
from debug import TDB,ploc
from keybinds import keyDicts
try:
    import rpdb2
except:
    pass

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdbOff=tdb.tdbOff

class modeState:
    def __init__(self,charBuffer):
        def esc():return 1
        esc=lambda:1 #or should it be 0?
        self.ikCtrlDict={}
        self.modeDict={}
        self.currentMode='init'
        self.helpDict={}
        self.keyActDict={}
        self.keyActDict['\x1b']=esc
        self.charBuffer=charBuffer
        self.key=None #genius! now we don't even need have the stupid pass through!
        self.keyRequest=0
        self.keyDicts=keyDicts #could find a better way to pass this on to keyFuncs
        self.threadDict={}
        #self.cond=threading.Condition()

    def doneCB(self):
        #self.event.set()
        #self.cond.acquire()
        #self.cond.notify_all()
        #self.cond.release()
        pass

    def updateModeDict(self):
        self.helpDict,newMD=makeModeDict(self.ikCtrlDict,*keyDicts.values())
        self.modeDict=newMD
        try:
            self.keyActDict.update(self.modeDict[self.currentMode])
        except KeyError:
            #printD('oops couldnt set set the mode dict for currentMode')
            pass
        return self

    def setMode(self,mode=None):
        """poop"""
        if mode:
            try:
            #if 1:
                #print('\n'+re.sub('>, ',')\r\n',str(self.modeDict)))
                #print('setMode: debug test',self.modeDict[mode])
                self.keyActDict=self.modeDict[mode] #where mode is just defined by __mode__
                printD('mode has been set to \'%s\' with keyActDict='%(mode))
                #printFD(self.keyActDict)
                #printFD(self.keyActDict)
                self.currentMode=mode
                #print('\n'+re.sub('>, ',')\r\n',str(self.keyActDict)))
                return self
            except KeyError:
                #raise
                if mode != 'init':
                    printD('failed to set mode \'%s\' did you write a mode dict for it?'%(mode))
                self.setMode(self.currentMode)
                return self
            #else:
        else:
            print(self.currentMode)
            return self
        #if mode!='norm':
            #self.keyActDict['\x1b']=self.setMode

    def keyHandler(self,keyRequest=0):#,key=None): #FIXME the way this works is SUPER confusing
        #printD('keyHandler starting, mode', self.currentMode,'passthrough',passThrough)
        #printFD(self.modeDict)
        if keyRequest:
            self.keyRequest=1
            return 1
        if self.keyRequest:
            self.keyRequest=0
            return 1 #if a request is in then return before getting the function from the queue
        self.key=self.charBuffer.get()
        try:
            function=self.keyActDict[self.key]
            if function:
                calledThread=threading.Thread(target=function)
                calledThread.start()
        except (KeyError, TypeError, Empty) as e:
            pass
        return 1

    def loadModule(self,kCtrlObj):
        """Spin this off into a thread, a bit wierd, but ok"""
        #rpdb2.setbreak()
        kCtrlObj(self)

    def cleanup(self):
        for kCtrl in self.ikCtrlDict.values():
            try:
                kCtrl.cleanup()
            except:
                printD('cleaup for',kCtrl,'failed')
        printD(threading.active_count())
        printD(threading.enumerate())
        printD('done!')


def main():
    charBuffer=Queue()
    modestate=modeState(charBuffer)

    #rpdb2.start_embedded_debugger('poop',timeout=1)
    keyThread=threading.Thread(target=keyListener,args=(charBuffer,modestate.keyHandler,modestate.cleanup))
    keyThread.start() #this has to start before the others because they depend on it being alive to start their while loops!

    modestate.keyThread=keyThread

    kCtrlObjs=clxFuncs,datFuncs,keyFuncs,mccFuncs,espFuncs
    #kCtrlObjs=datFuncs,keyFuncs,mccFuncs,espFuncs
    for cls in kCtrlObjs:
        modestate.loadModule(cls) #the threading IN THE THINGS will take care of any problems we have you idiot



    #printFD(modestate.modeDict)
    while 1:
        try:
            modestate.setMode('rig')
            break
        except:
            pass

    #keyThread.join() #pretty sure this is what makes the program terminate properly? nope it just sits there being dumb

    #printD(threading.enumerate())




if __name__=='__main__':
    main()
