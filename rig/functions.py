import re
import datetime
import inspect as ins
from sys import stdout,stdin
from time import sleep
from debug import TDB,ploc
from rig.ipython import embed
from database.decorators import new_abf_DataFile
#from IPython import embed
try:
    import rpdb2
except:
    pass

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdb.off()

#file to consolidate all the different functions I want to execute using the xxx.Control classes
#TODO this file needs a complete rework so that it can pass data to the database AND so that it can be used by keyboard AND so that it can be used by experiment scripts... means I may need to split stuff up? ;_;
#TODO rig control vs experiment control... these are technically two different 'modes' one is keyboard controlled the other is keyboard initiated...
#TODO ideally I want to do experiments the same way every time instead of allowing one part here and another there which is sloppy so those are highly ordered...
#TODO BUT I need a way to fix things, for example if the slice moves and I need to recalibrate the slice position (FUCK, how is THAT going to work out in metadata)

#TODO all of these are configured for terminal output only ATM, ideally they should be configged by whether they are called from keyboard or from experiment... that seems... reasonable??! not very orthogonal...
#mostly because when I'm running an experiment I don't want to accientally hit something or cause an error

#TODO split in to send and recieve?!?

#TODO datasource/expected datasource mismatch

#dec for telling the program to run the function in the same thread
def sameThread(function):
    def _sameThread(self,*args,**kwargs):
        out=function(self,*args,**kwargs)
        return out
    _sameThread.sameThread=True
    _sameThread.__name__=function.__name__
    return _sameThread


#static method for adding a function as a key requester
def keyRequest(function): #FIXME sometimes we want to release a kr EARLY!
    def _keyRequest(self,*args,**kwargs):
        def wrapper():
            try:
                self._kr_not_done+=1 #this enables keyRequesters to call eachother safely if they are in the same class
                out=function(self,*args,**kwargs)
                self._kr_not_done-=1
            except:
                self._kr_not_done-=1
                raise
                #printD('an error has occured while calling func!')
            finally:
                printD('_kr_not_done=',self._kr_not_done)
                if not self._kr_not_done: #TODO prevent multiple unlocks
                    self._releaseKR()
                    assert self._kr_not_done >= 0, 'oh no! _kr_not_done is negative!!'
            return out
        return wrapper() #FIXME this seems to be needed to prevent some other race condition >_<
    _keyRequest.keyRequester=True
    _keyRequest.__name__=function.__name__
    return _keyRequest

###
#class decorator
def hasKeyRequests(cls):
    cls.keyRequesters=[]
    cls._kr_not_done=False #FIXME will we get nasty threading collisions here?
    def init_wrap(init):
        def __init__(self,modestate,*args):
            self._releaseKR=modestate.releaseKeyRequest
            for name in self.keyRequesters:
                modestate.registerKeyRequest(cls.__name__,name)
            init(self,modestate,*args)
        return __init__
    cls.__init__=init_wrap(cls.__init__)

    for name,method in cls.__dict__.items(): #register keyRequesters
        if hasattr(method,'keyRequester'):
            #printD('got one!',name)
            cls.keyRequesters.append(name)
    return cls

class kCtrlObj:
    """key controller object"""

    def __init__(self, modestate, controller=None):
        self.charBuffer=modestate.charBuffer
        #self.releaseKeyReq=modestate.releaseKeyRequest #FIXME don't even have to do this, @keyRequest can do it for me! :)
        #I probably do not need to pass key handler to thing outside of inputManager...
        #yep, not used anywhere, but I supose it could be used for submodes... we'll leave it in
        self.setMode=modestate.setMode
        self.__mode__=self.__class__.__name__
        self.keyThread=modestate.keyThread
        self.ctrl=controller

    def cleanup(self):
        pass


@hasKeyRequests
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
        self.current_program=''
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
    def getStatus(self,outputs=None): #TODO outputs... should be able to output to as many things as I want... probably should be a callback to simplify things elsewhere? no?!?!
        status=self.ctrl.GetStatus()
        print(status)
        return self

    @keyRequest
    def load(self,key=None):
        if not key:
            print('Please enter the program to load')
            key=self.charBuffer.get()
        try:
            path=self.programDict[key]
            #printD(path)
            self.ctrl.LoadProtocol(path.encode('ascii'))
            self.current_program=path
            print('%s loaded!'%path)
        except BaseException as e:
            print(e)
            #print('Program not found')
            #raise
        return self

    @new_abf_DataFile
    def record(self):
        #RECORD=109, RERECORD=110, VIEW=108
        try:
            self.ctrl.StartAcquisition(109)
            print('Running %s'%self.current_program)
        except:
            raise
        return self

    def view(self):
        #RECORD=109, RERECORD=110, VIEW=108
        try:
            self.ctrl.StartAcquisition(108)
            print('Viewing %s'%self.current_program)
        except:
            raise
        finally:
            return self
    
    def stop_rec(self):
        self.ctrl.StopAcquisition()
        print('Stopping curren acquistion')


    #input only
    def startMembTest(self):
        self.ctrl.StartMembTest(120)
        self.ctrl.StartMembTest(121)
        return self


@hasKeyRequests
class datFuncs(kCtrlObj): 
    #interface with the database TODO this should be able to run independently?
    """Put ANYTHING permanent that might be data in here"""
    #from database.sessions import get_pg_sessionmaker
    #pg_sessionmaker=get_pg_sessionamaker()
    #session=pg_sessionmaker
    from database.models import Person, ExperimentType, Experiment, Cell, Slice, Mouse
    def __init__(self,modestate,*args):
        super().__init__(modestate)
        self.session=modestate.session
        #self.__getChars2__=modestate.ikFuncDict['trmFuncs'].__getChars__
        self.c_person=self.session.query(self.Person).filter(self.Person.FirstName=='Tom',self.Person.LastName=='Gillespie').one()
        self.c_project=self.c_person.projects[0] #FIXME

    #@keyRequest
    #def __getChars2__(self,prompt=None): #compile name collisions >_<
        #return self.modestate.trm_io.__getChars__(prompt)

    #@keyRequest
    def newExperiment(self): #FIXME this fails because of how dictMan works...
        types=self.session.query(self.ExperimentType).all()
        print('please enter the type of experiment, available types are: %s'%[t.abbrev for t in types])
        type_=None
        #type_string=self.__getChars2__('type>')
        type_=[t for t in types if t.abbrev==type_string]
        if type_:
            self.session.add(self.Experiment(type_id=type_[0],project_id=self.c_project,person_id=self.c_person))
            self.session.commit()
        else:
            print('Invalid type: experiment not created')

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
        
        #associated metadata sources
        #self.state1DataSource=None


    def inpWait(self): #XXX depricated
        #wait for keypress to move to the next program, this may need to spawn its own thread?
        raise DeprecationWarning('please use trmFuncs.getKbdHit()')

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


@hasKeyRequests
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
        self.modestate=modestate
        self.setMoveDict()
        #self.event=modestate.event
        
        #associated metadatasources:
        #self.EspXDataSource=None
        #self.EspYDataSource=None

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

    @keyRequest
    def mark(self): #FIXME
        """mark/store the position of a cell using a character sorta like vim"""
        stdout.write('\rmark:')
        stdout.flush()
        key=self.charBuffer.get()
        #printD('we got the key from charBuffer')
        if key in self.markDict:
            print('Mark %s is already being used, do you want to replace it? y/N'%(key))
            yeskey=self.charBuffer.get()
            #self._releaseKR() #XXX
            if yeskey=='y' or yeskey=='Y':
                self.markDict[key]=self.ctrl.getPos()
                print(key,'=',self.markDict[key])
            else:
                print('No mark set')
        elif key=='esc':
            self.unmark()
        else:
            #self._releaseKR() #XXX
            self.markDict[key]=self.ctrl.getPos()
            print(key,'=',self.markDict[key])
        #self.keyHandler(getMark) #fuck, this could be alot slower...
        return self
    #mark.keyRequester=True

    @keyRequest
    def unmark(self):
        #self.doneCB()
        try:
            mark=self.charBuffer.get()
            pos=self.markDict.pop(mark)
            print("umarked '%s' at pos %s"%(mark,pos))
        except KeyError:
            pass
        return self

    @keyRequest #FIXME we may actually want to use the manual version here due to BsetPos...
    def gotoMark(self): #FIXME
        #self.doneCB()
        stdout.write('\rgoto:')
        stdout.flush()
        key=self.charBuffer.get()
        #self._releaseKR() #XXX
        if key in self.markDict:
            print('Moved to: ',self.ctrl.BsetPos(self.markDict[key])) #AH HA! THIS is what is printing stuff out as I mvoe FIXME I removed BsetPos at some point and now I need to add it... back? or what
        else:
            print('No position has been set for mark %s'%(key))
        return self
    #gotoMark.keyRequester=True

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
            #print(self.ctrl._cX,self.ctrl._cY)
        else:
            print('Not in fake mode! Not moving!')
        return self

    #callback to break out of display mode
    def _gd_break_callback(self):
        print('leaving disp mode!')
        self._gd_exit=1
        self.modestate.keyActDict['esc']=self._gd_old_esc
        self._gd_old_esc=None
        del(self._gd_old_esc)
        self.modestate.keyActDict[self._gd_own_key]=self.getDisp
        self._gd_own_key=None
        del(self._gd_own_key)

    #@keyRequest #just added the getDisp.keyRequester=True at the bottom and we're good to go
    def getDisp(self):
        """BLOCKING stream the displacement from a set point"""
        #self.doneCB()
        from numpy import sum as npsum #FIXME should these go here!?
        from numpy import array as arr
        print('entering disp mode')

        if not len(self.markDict):
            self.mark()
        else:
            self._releaseKR() #XXX release whether we got it or not

        def get_key(_dict,func):
            for key,value in _dict.items():
                if value == func:
                    return key
            raise KeyError('key not found!')


        self._gd_old_esc=self.modestate.keyActDict['esc']
        self._gd_own_key=get_key(self.modestate.keyActDict,self.getDisp)
        printD('get disp key:',self._gd_own_key)

        self._gd_exit=0
        self.modestate.keyActDict['esc']=self._gd_break_callback #FIXME probably going to need some try:finally:
        self.modestate.keyActDict[self._gd_own_key]=lambda:print('already in disp mode!')

        def format_str(string,width=9):
            missing=width-len(string)
            return string+' '*missing
        dist1=1
        print(list(self.markDict.keys()))
        while self.keyThread.is_alive() and not self._gd_exit: #FIXME may need a reentrant lock here to deal w/ keyboard control
            pos=self.markDict.values()
            dist=(npsum((arr(self.ctrl._BgetPos()-arr(list(pos))))**2,axis=1))**.5 #FIXME the problem here is w/ _BgetPos()
            if dist1!=dist[0]:
                #names='%s \r'%(list(self.markDict.keys())) #FIXME sadly, it seems there is no way ;_;
                #stdout.write('\r'+''.join(map('{:1.5f} '.format,dist)))
                stdout.write('\r'+''.join([format_str('{:1.5f}'.format(d)) for d in dist]))
                stdout.flush()
                dist1=dist[0]

            #try:
                #key=self.charBuffer.get_nowait()
                ##FIXME this should go AFTER the other bit to allow proper mode changing
                #if key=='q' or key=='esc': #this should be dealt with through the key handler...
                    #print('\nleaving displacement mode')
                    #break
                #elif key: #FIXME HOW DOES THIS EVEN WORK!?!??!
                    ##printD('breaking shit')
                    #try:
                        #func=self.modestate.keyActDict[key] #FIXME WOW BAD
                        #printD(func.__name__)
                        #if func.__name__ !='getDisp': #FIXME this isnt catching it because lambda
                            #from threading import Thread
                            #a=Thread(target=func)
                            #a.start()
                    #except:
                        #printD('should have keyHandled it')
            #except:
                #pass
        printD('done! loops broken!')
        return self
    getDisp.keyRequester=True

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
        tdb.on()
        printFD(self.modestate.helpDict)
        tdb.off()
        #self.doneCB()
        return self
    def esc(self):
        return 0


@hasKeyRequests
class trmFuncs(kCtrlObj): #FIXME THIS NEEDS TO BE IN THE SAME THREAD
    def __init__(self, modestate):
        self._keyThread=modestate.keyThread
        self.keyLock=modestate.keyLock
        self.modestate=modestate #need this to det the current modestate
        super().__init__(modestate)
        def printwrap(func):
            def wrap(*args,**kwargs):
                out=func()
                printD(out)
                return out
            wrap.__name__=func.__name__
            return wrap
        #for name in self.ctrl.__dir__():
            #if name[:3]=='get':
                #setattr(self,name,printwrap(getattr(self.ctrl,name)))
        for name in self.__dir__():
            if name[:3]=='get':
                setattr(self,name,printwrap(getattr(self,name)))
                setattr(getattr(self,name),'__name__',name)

    @keyRequest
    def __getChars__(self,prompt=''):
        """ replacement for input()"""

        class inputBuffer:
            char_list=[]
            pos=0
            _filler=0 #used to make the display update correct
            def put(self,char):
                self.char_list.insert(self.pos,char)
                #if self._filler > 0: #don't need it is ok to overfill
                    #self._filler -= 1
                self.goR()
            def goR(self):
                if self.pos + 1 <= len(self.char_list):
                    self.pos += 1
            def goL(self):
                if self.pos -1 >= 0:
                    self.pos -= 1
            def home(self):
                self.pos = 0
            def end(self):
                self.pos = len(self.char_list)
            def backspace(self):
                if self.pos: #if we're already at zero dont go!
                    self._filler+=1
                    self.char_list.pop(self.pos-1)
                    self.goL()
            def delete(self):
                try:
                    self.char_list.pop(self.pos)
                    self._filler+=1
                except IndexError:
                    pass
            def __str__(self):
                return ''.join(self.char_list)
            @property
            def str_to_pos(self):
                return ''.join(self.char_list[:self.pos])
            def pop_filler(self):
                out=self._filler #ick this is terrible TODO FIXME
                self._filler=0
                return out

        ib=inputBuffer()

        cmddict={
        '[A':lambda:None,
        '[B':lambda:None,
        '[C':ib.goR,
        '[D':ib.goL,
        '\x7f':ib.backspace,
        '[3~':ib.delete,
        '[7~':ib.home,
        '[8~':ib.end,
        'esc':lambda:None,
        }

        def charHand(char):
            if cmddict.get(char):
                cmddict[char]()
            elif len(char) > 1:
                pass #prevents escape sequences from printing
            else:
                ib.put(char)

        #self.keyLock.acquire()
        stdout.write('\r%s'%prompt)
        while self.keyThread.is_alive():
            char=self.charBuffer.get()
            #printD('got a key:', char) 
            if char == '\n':
                break
                printD('done')
            charHand(char)
            stdout.write('\r%s'%prompt+str(ib)+' '*ib.pop_filler())
            stdout.write('\r%s'%prompt+ib.str_to_pos)
            stdout.flush()
        if not self.keyThread.is_alive():
            raise IOError('Key thread is not alive!')
        else:
            return str(ib)

    @keyRequest
    def getString(self):
        print("Please enter a string.",)
        return self.__getChars__('string> ')

    @keyRequest
    def getFloat(self):
        print('Please enter a floating point value.',)
        while 1:
            string=self.__getChars__('float> ')
            try:
                out=float(string)
                return out
            except:
                print('Could not convert value to float, try again!')

    @keyRequest
    def getInt(self):
        print('please enter an integer',)
        while 1:
            string=self.__getChars__('int> ')
            try:
                out=int(string)
                return out
            except ValueError as e:
                print(e,'Try again!')
                #print('could not convert value to int, try again!')

    @keyRequest
    def getKbdHit(self):
        print('Hit any key to advance.')
        self.charBuffer.get()
        return True

    def getDoneNB(self): #FIXME 
        print('Hit space when you are done') #FIXME
        try:
            old_func=self.modestate.keyActDict[' ']
        except:
            old_func=None

        self._gdnb_cb_done=False
        def callback():
            self._gdnb_cb_done=True

        self.modestate.keyActDict[' ']=callback
        while not self._gdnb_cb_done and self.keyThread.is_alive(): 
            sleep(.001) #FIXME
        printD('got it')
        
        if old_func:
            self.modestate.keyActDict[' ']=old_func #FIXME danger in x thread?
        else:
            self.modestate.keyActDict.pop(' ')
        return True
        
    def getDoneFailNB(self): #FIXME 
        print('Hit space for success or \ for failure') #FIXME use a reverse dict in keybinds
        #FIXME ick
        success=' '
        fail='\\'
        try:
            old_func=self.modestate.keyActDict[success]
        except:
            old_func=None
        try:
            old_fail=self.modestate.keyActDict[fail]
        except:
            old_fail=None

        self._gdnb_cb=0
        def callback():
            self._gdnb_cb=1 #'done'
        def fail_cb():
            self._gdnb_cb=2 #'fail'

        self.modestate.keyActDict[success]=callback
        self.modestate.keyActDict[fail]=fail_cb
        while not self._gdnb_cb and self.keyThread.is_alive():
            sleep(.001) #FIXME

        if self._gdnb_cb == 1:
            out=True
            printD('got success')
        else:
            out=False
            printD('got fail')
        
        if old_func:
            self.modestate.keyActDict[success]=old_func #FIXME danger in x thread?
        else:
            self.modestate.keyActDict.pop(success)
        if old_fail:
            self.modestate.keyActDict[fail]=old_fail #FIXME danger in x thread?
        else:
            self.modestate.keyActDict.pop(fail)
        return out

    def _getDoneFailNB(self): #FIXME 
        print('Hit space for success or \ for failure') #FIXME use a reverse dict in keybinds
        #FIXME ick
        succss=' '
        fail='\\'
        try:
            old_func=self.modestate.keyActDict[success]
        except:
            old_func=None
        try:
            old_fail=self.modestate.keyActDict[fail]
        except:
            old_fail=None

        self._gdnb_cb_done=False
        self._gdnb_cb_fail=False
        def callback():
            self._gdnb_cb_done=True
        def fail_cb():
            self._gdnb_cb_fail=True

        self.modestate.keyActDict[success]=callback
        while not self._gdnb_cb_done or not self._gdnb_cb_fail:
            sleep(.001) #FIXME
        printD('got it')

        if self._gdnb_cb_fail:
            out=False
        if self._gdnb_cb_done:
            out=True
        
        if old_func:
            self.modestate.keyActDict[success]=old_func #FIXME danger in x thread?
        else:
            self.modestate.keyActDict.pop(success)
        if old_fail:
            self.modestate.keyActDict[fail]=old_fail #FIXME danger in x thread?
        else:
            self.modestate.keyActDict.pop(fail)
        return out

    @keyRequest
    def getBool(self):
        print('Boolean: hit space for True, anything else for False.')
        true_key=' '
        #self.keyHandler(1) #requesting key passthrough
        out=self.charBuffer.get() == true_key
        return out

    @keyRequest
    def command(self): #TODO
        """ vim : mode """
        #TODO figure out where to move the command dict...
        #cmdDict={'ipython':'ipython'} #can't put ipython here due to race conditions
        cmdDict={}
        def parse_command(com_str): #TODO
            def match_key(com_str):
                printD(com_str)
                matches = [key for key in cmdDict.keys() if key[:len(com_str)]==com_str]
                matches.sort()
                return matches
            matches=match_key(com_str)
            printD(matches)
            func=getattr(self,matches[0],lambda:None)
            func()
            #printD(com_str,'TODO FIXME')
            return com_str
        print('command opened')
        com_str=self.__getChars__(':')
        return parse_command(com_str)

    def ipython(self):
        #TODO how to deal with imports...
        try:
            self.keyLock.acquire() #XXX lock acquire so ipython can have input priority
            #embed()
            printD('Not Implemented here due to threading and needing to hit one extra key to break the lock in keyListener')
        finally:
            self.keyLock.release() #XXX lock release

    def test(self):
        print('testing testing 123')

def main():
    esp=espFuncs(None,None,None,None)
    #mcc=mccFuncs(None,None,None,None)

__all__=(
    'clxFuncs',
    'mccFuncs',
    'espFuncs',
    'keyFuncs',
    'trmFuncs',
    'datFuncs',
)
if __name__=='__main__':
    main()
