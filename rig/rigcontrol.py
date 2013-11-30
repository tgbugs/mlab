#!/usr/bin/env python3.3
import threading
import warnings
from queue import Queue,Empty

from rig.ipython import embed

from rig.functions import * #__all__ has been set, update it
from rig.keybinds import keyDicts
from rig.dictMan import makeModeDict
from rig.key import keyListener
from rig.clx import clxControl
from rig.esp import espControl
from rig.mcc import mccControl

from debug import TDB,ploc
tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdb.off()

#TODO need to integrate stuff from experiments, but maybe it makes sense to do that elsewhere somehow?
#since they will need to be integrated with keys to launch them or something

class rigIOMan:
    """Terminal input manager, control the rig from a terminal window"""
    def __init__(self,keyDicts,session):
        #self.globs=globs #for passing in to for openIPyton and embed()
        self.keyDicts=keyDicts
        self.krdLock=threading.RLock()

        self.ikFuncDict={}
        self.kr_dict={} #dict of registered key requesting functions
        self.modeDict={}
        self.helpDict={}
        self.keyActDict={}
        self.keyRequestDict={} #store the number of requests per key
        self.trmRequestDict={} #TODO this can allow other threads that want to spawn ipython to hold?

        self._keyRequest=0 #used to keep a count of the number of outstanding key requests
        self.key=None #genius! now we don't even need have the stupid pass through!
        self.keyLock=threading.RLock() #used to allow ipython to work in linux
        self.currentMode='init'

        def esc():return 1
        self.keyActDict['esc']=esc

        self.charBuffer=Queue()


        self.keyThread=threading.Thread(target=keyListener,args=(self.charBuffer,self.keyHandler,self.keyLock,self.term_callback,self.cleanup))
        #self.keyThread=keyThread

        self.session=session #FIXME how do we ACTUALLy want to deal with this? I feel like I have isolated most of the database io that the keyboard interacts with to the dataios-write
            #but what if I want to query something on the fly? urg
            #just open a new terminal m8

        self.initControllers() #these need charBuffer and keyThread to work FIXME nope, dupe for ':':'cmd'
        self.setMode('rig')

        #TODO add a way for keys to enter programatic control mode, they will still need keyinput though
        #FIXME TODO
        self.ctrlDict.update(self.ikFuncDict) #FIXME temp hack to get trmFuncs through to the rest of the world
        self.locs={} #for passing locals into ipython
        #print(self.modeKRDict)
    def start(self):
        self.keyThread.start()

    def pass_locals(self,locs):
        self.locs=locs
    def term_callback(self,off,on):
        self.term_off=off
        self.term_on=on

    def ipython(self):
        locals().update(self.locs) #SUPER unkosher but seems safe from tampering
        try:
            self.term_off()
            self.keyLock.acquire()
            embed() #FIXME WHAT IS THIS WIZARDRY!? how is this even in the name space O_O
        finally:
            self.term_on()
            self.keyLock.release()

    def updateModeDict(self):
        #TODO keyDicts.values is where we will find the names of the functions that have been wrapped as keyRequests and that keybinding is what we need to hop on
        #all we need to do is pass in acquireKeyRequest and wrap the function when we make keyActDict
        self.helpDict,self.modeDict,self.modeKRDict=makeModeDict(self.ikFuncDict,self.kr_dict,*keyDicts.values())
        try:
            self.keyActDict.update(self.modeDict[self.currentMode])
            self.keyRequestDict.update(self.modeKRDict[self.currentMode])
        except KeyError:
            pass
        return self

    def setMode(self,mode=None):
        """poop"""
        if mode:
            try:
                self.keyActDict=self.modeDict[mode] #where mode is just defined by __mode__
                self.keyRequestDict=self.modeKRDict[mode]
                #printD(self.keyRequestDict)
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

    def registerKeyRequest(self,className,functionName):
        #if self.kr_dict.get(className): #really __mode__ but hey
        #printD(locals())
        try:
            self.kr_dict[className].append(functionName)
        except:
            self.kr_dict[className]=[functionName]
        #printD('kr_dict',self.kr_dict)

    #def acquireKeyRequest(self): #FIXME does this require locking? I don't think so because the passthrough will prevent a the thread from being spawned anyway unless something else trys to get() from charBuffer in which case wtf!
        #self.keyRequest=1
    def releaseKeyRequest(self): #callback to release a key request lock
        try:
            #printD('krdLock try')
            self.krdLock.acquire()
            #printD('krdLock acquire')
            self._keyRequest -= 1
            assert self._keyRequest >= 0, 'utoh key requests went below zero!'
        except:
            raise
            #raise BaseException('wtf is going on here')
        finally:
            printD('krdLock release')
            printD('key request released value =',self._keyRequest)
            self.krdLock.release()

    def print_keyRequest(self):
        try:
            self.krdLock.acquire()
            printD(self._keyRequest)
        except:
            raise
        finally:
            self.krdLock.release()

    def keyHandler(self):
        #self.print_keyRequest()
        if self._keyRequest > 0: #FIXME the currently cannot deal with multiple interspersed key requesters properly!
            #printD('key request has %s passing through'%self.keyRequest)
            return 1
        self.key=self.charBuffer.get() #if we're not in a key request get the key

        if self.key=='i':
            self.ipython()

        try:
            #printD('krdLock try')
            self.krdLock.acquire()
            #printD('krdLock acquire')
            #func_name=self.keyActDict[self.key].__name__
            self._keyRequest+=self.keyRequestDict.get(self.key,0) #get key requests for that key
                # and add that number of expected callbacks to requests
        except:
            raise
            #raise BaseException('wtf is going on here')
        finally:
            #printD('krdLock release')
            self.krdLock.release()

        try: #then call the function
            function=self.keyActDict[self.key]
            #if hasattr(function,'sameThread'):
                #function()
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
        controllers=clxControl,espControl,mccControl
        ctrlDict={}
        for ctrl in controllers:
            try:
                inited=ctrl()
                print('[OK]',inited.__class__.__name__)
                ctrlDict[ctrl.__name__]=inited
            except:
                #warnings.warn('[!] %s failed to init'%ctrl.__name__,UserWarning,0)
                #raise
                print('[!] %s failed to init'%ctrl.__name__) #XXX print

        #init trmFuncs since it really should be part of key...
        #self.trm_io=trmFuncs(self)
        #self.ikFuncDict['trmFuncs']=self.trm_io
        #self.ikFuncDict['trmFuncs']=lambda:raise DeprecationWarning('replace with reference to .trm_io please')
        #init the rest 
        ctrlBindingDict={
                'clxControl':clxFuncs,
                'espControl':espFuncs,
                'mccControl':mccFuncs,
        }
        for ctrl_name in ctrlDict.keys(): #initilize the function dicts
            initedFunc=ctrlBindingDict[ctrl_name](self,ctrlDict[ctrl_name]) #callback to register functions as keyRequesters happends here
            self.ikFuncDict[initedFunc.__mode__]=initedFunc


        FUNCS=keyFuncs,trmFuncs,datFuncs #must init dat after trm?
        for func in FUNCS:
            initedFunc=func(self) #callback to register functions as keyRequesters happends here
            self.ikFuncDict[initedFunc.__mode__]=initedFunc


        self.updateModeDict() #bind keys to functions
        self.ctrlDict=ctrlDict #FIXME make more explicit
        return ctrlDict

   
def main():
    from database.sessions import get_pg_sessionmaker
    pg_sm=get_pg_sessionmaker()
    session=pg_sm()
    rigIO=rigIOMan(keyDicts,session)
    rigIO.start()


if __name__=='__main__':
    main()
