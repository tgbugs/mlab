import re
import datetime
import inspect as ins
from sys import stdout,stdin
from time import sleep
from rig.ipython import embed

try: 
    from sqlalchemy.orm import object_session #FIXME vs database.imports?
    from database.decorators import Get_newest_id, datafile_maker, new_abf_DataFile, hardware_interface, is_mds, new_DataFile, get_local_extension_path #FIXME get rid of these
    from database.standards import Get_newest_file
except:
    # assume we are running without database support at that we are not accidentally going to call something and crash
    pass

from threading import RLock, Thread
from rig.gui import takeScreenCap #FIXME

try:
    from matplotlib.pyplot import figure,plot,axis,savefig,switch_backend,annotate
except:
    #only used in espFunc
    pass
#from IPython import embed
try:
    import rpdb2
except:
    pass

try:
    from debug import TDB,ploc
    tdb=TDB()
    printD=tdb.printD
    printFD=tdb.printFuncDict
    tdb.off()
except:
    printD=print
    printFD=print

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
                self.krdLock.acquire()
                self._kr_not_done+=1
                printD(self._kr_not_done)
                out=function(self,*args,**kwargs)
            except:
                #self._kr_not_done-=1
                raise
                #printD('an error has occured while calling func!')
            finally:
                self._kr_not_done-=1 #moved this here to prevent weird errors?
                printD(self._kr_not_done)
                self.krdLock.release()
                assert self._kr_not_done >= 0 ,'utoh! _kr_not_done < 0 !'
                printD('kr_not_done=',self._kr_not_done)
                if not self._kr_not_done: #TODO prevent multiple unlocks
                    self._releaseKR()
            return out
        return wrapper() #FIXME this seems to be needed to prevent some other race condition >_<
    _keyRequest.keyRequester=True
    _keyRequest.__name__=function.__name__
    _keyRequest.__doc__=function.__doc__
    if hasattr(function,'is_mds'):
        _keyRequest.is_mds=True
    return _keyRequest

###
#class decorator
def hasKeyRequests(cls):
    cls.keyRequesters=[]
    cls._kr_not_done=0 #FIXME will we get nasty threading collisions here?
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
    def __init__(self, modestate):
        self.charBuffer=modestate.charBuffer
        #self.releaseKeyReq=modestate.releaseKeyRequest #FIXME don't even have to do this, @keyRequest can do it for me! :)
        #I probably do not need to pass key handler to thing outside of inputManager...
        #yep, not used anywhere, but I supose it could be used for submodes... we'll leave it in
        self.setMode=modestate.setMode
        self.__mode__=self.__class__.__name__
        self.keyThread=modestate.keyThread

        self._kr_not_done=0
        self._releaseKR=modestate.releaseKeyRequest
        self.krdLock=modestate.krdLock
        self.keyRequesters=[]
        for name,method in ins.getmembers(self):
            #printD(name,method)
            if ins.ismethod(method) and hasattr(method,'keyRequester'):
                self.keyRequesters.append(name)
                modestate.registerKeyRequest(self.__class__.__name__,name)

        #some way to pass the state along to other controllers XXX REQUIRED FOR CLASS DECORATORS TO WORK XXX
        def dat_get_write_targets():
            #return modestate.ctrlDict['datFuncs'].getWriteTargets()
            return self.getWriteTargets()
        def dat_get_df_subjects():
            #return modestate.ctrlDict['datFuncs'].getDFSubjects()
            return self.getDFSubjects()
        def dat_new_df():
            #return modestate.ctrlDict['datFuncs'].newDataFileCallback()
            return self.newDataFileCallback()
        self._wt_getter=dat_get_write_targets
        self._sub_getter=dat_get_df_subjects #name needs to match for decorators to work >_<
        self._new_datafile=dat_new_df

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
            if char == '\n' or char == '\r':
                printD('done')
                stdout.write('\n\r')
                stdout.flush()
                break
            charHand(char)
            stdout.write('\r%s'%prompt+str(ib)+' '*ib.pop_filler())
            stdout.write('\r%s'%prompt+ib.str_to_pos)
            stdout.flush()
        if not self.keyThread.is_alive():
            raise IOError('Key thread is not alive!')
        else:
            #print(str(ib))
            return str(ib)

    @keyRequest
    def getString(self,prompt='string> '):
        print("Please enter a string.",)
        return self.__getChars__(prompt)

    @keyRequest
    def getFloat(self,prompt='float> '):
        print('Please enter a floating point value.',)
        while self.keyThread.is_alive():
            string=self.__getChars__(prompt)
            try:
                out=float(string)
                return out
            except:
                print('Could not convert value to float, try again!')

    @keyRequest
    def getInt(self,prompt='int> '):
        print('please enter an integer',)
        while self.keyThread.is_alive():
            string=self.__getChars__(prompt)
            try:
                out=int(string)
                return out
            except ValueError as e:
                print(e,'Try again!')
                #print('could not convert value to int, try again!')

    @keyRequest
    def getBool(self,prompt='Boolean: hit space for True, anything else for False.'):
        print(prompt)
        true_key=' '
        #self.keyHandler(1) #requesting key passthrough
        out=self.charBuffer.get() == true_key
        return out

    def cleanup(self):
        """ this is the final super().cleanup() """
        try:
            super().cleaup()
        except:
            pass

try:
    from database.models import Person, Project, ExperimentType, Experiment, Cell, Slice, Mouse, DataFile, Repository, DataFileSource
    from datetime import datetime
    from database.imports import NoResultFound, MultipleResultsFound
except:
    #only needed for dat funcs, split these damned things out into their own files
    pass
class datFuncs(kCtrlObj): #FIXME split this out into expFuncs and datFuncs?
    #interface with the database TODO this should be able to run independently?
    """Put ANYTHING permanent that might be data in here"""
    def __init__(self,modestate,*args,person_id=None,project_id=None,**kwargs):
        super().__init__(modestate,**kwargs)
        #self.Session=modestate.Session #FIXME maybe THIS was the problem?
        #session=self.Session()
        self.c_person=self.session.query(Person).filter_by(id=person_id).one()
        self.c_project=self.session.query(Project).filter_by(id=project_id).one() #FIXME the person could not be on the project
        self.getUnfinished() #FIXME huge problem: keyRequests are registered AFTER this >_<
        self.c_datafile=None
        #self.session=session #FIXME
        self.sLock=RLock() #a lock for the session, see if we need it
        #session.close()

    """
    def getRepoDFS(self,extension,dfs_name='clampex 9.2',url=None): #FIXME make this persistent on init?? TODO fix this so that it actually gets the dfs >_<
        if not url:
            hostname,fpath=get_local_extension_path(extension)
            url='file://%s/%s'%(hostname,fpath)
        init_sess=self.session
        repo=init_sess.query(Repository).filter_by(url=url).first() #FIXME try/except?
        dfs=init_sess.query(DataFileSource).filter_by(name=dfs_name).first()
        if not repo or not dfs:
            if not repo:
                init_sess.add(Repository(url=url))
            if not dfs:
                #dfs=DataFileSource(name='lol wut!?',extension=extension,docstring='a whoknows!') #FIXME TODO generalize!
                #init_sess.add(dfs)
                raise IOError('Need to do something about DFSes') #TODO need to figure out what to do with this
            try:
                init_sess.commit()
            except:
                init_sess.rollback()
                raise
        #print(repo,dfs.name)
        return repo,dfs
    """

    def add_com_sess(self,obj_to_add):
        self.session.add(obj_to_add)
        try:
            self.session.commit()
        except:
            print('[!] %s could not be added! Rolling back!'%obj_to_add)
            self.session.rollback()
            raise


    def getUnfinished(self): #FIXME it is possible to get cells or slices w/o experiment...
        def queryUnf(obj):
            return self.session.query(obj).filter(obj.endDateTime==None)

        #experiemtns
        try:
            equery=queryUnf(Experiment) #FIXME it is possible for there to be more than one unfinished experiment!
            allexp=equery.all()
            if not allexp:
                self.c_experiment=None
                self.c_target=None
            elif len(allexp)>1:
                #print([ (e.id,e.type,e.startDateTime) for e in allexp])
                #eid=self.getInt('Please enter an experiment id')
                #self.c_experiment=equery.get(eid) #FIXME
                self.c_experiment=allexp[-1]
                print('WARNING: multiple unfinished! Experiment set to %s. Change it if you need to!'%self.c_experiment)
            else:
                self.c_experiment=equery[0]
                self.c_target=self.c_experiment
                print('Got unfinished experiment ',repr(self.c_experiment.strHelper()))
        except:
            raise

        #slices
        try:
            allsli=queryUnf(Slice).all()
            if not allsli:
                self.c_slice=None
            else:
                self.c_slice=allsli[-1]
                self.c_target=self.c_slice
                if len(allsli)>1:
                    print('WARNING: multiple unfinished! Slice set to %s. Change it if you need to!'%self.c_slice.strHelper())
                print('Got unfinished slice ',self.c_slice.strHelper())
        except NoResultFound:
            self.c_slice=None
        #cells
        try:
            cells=queryUnf(Cell).join(Experiment,Cell.experiments).filter(Experiment.id==self.c_experiment.id).join(Slice,Cell.parent).filter(Slice.id==self.c_slice.id).all()
            self.c_cells=cells
            if cells:
                print('Got unfinished cells ',[c.strHelper() for c in cells])
                self.c_target=self.c_cells[0]
        except AttributeError: #catch NoneType
            self.c_cells=[]
        #datafiles #TODO

    @keyRequest
    def setWriteTargets(self):
        print('slice','cell','exp','data')
        type_=self.__getChars__('target> ')
        if type_ == 'exp':
            self.c_target=self.c_experiment
        elif type_ == 'slice':
            self.c_target=self.c_slice
        elif type_ == 'cell':
            print('cell number 0-n amongst current cells n probably <=3')
            index=self.getInt('cell #> ')
            if index >= len(self.c_cells):
                index=len(self.c_cells)-1
            self.c_target=self.c_cells[index]
        elif type_ == 'data':
            self.c_target=self.c_datafile
        else:
            print('not a type, try fiddling with ipython if you really need to spec soemthing')


    def getDFSubjects(self):
        """ used to pass the current cells to the new_abf_DataFile decorator """
        return self.c_cells
    
    def getWriteTargets(self): #XXX NOTE XXX there is only a SINGLE write target at a time now!
        targets=[] #FIXME change calling methods to match
        target=self.c_target
        #try:
            #iter(target)
            #targets.extend(target)
        #except TypeError:
        targets.append(target)

        return targets

    def get_df_statistics(self):
        """ calculate and rpint the test pulse statistics and hopefully save them to the database? """
        from database.abf_analysis import print_tp_stats
        print_tp_stats(self.c_datafile.full_url[8:])
        
    def print_write_target(self):
        print(repr(self.c_target))
        try:
            iter(self.c_target)
            for t in self.c_target:
                self.session.refresh(t)
                print(t.metadata_)
                print(t.notes)
                try:
                    print(t.datafiles)
                except:
                    pass
        except:
            self.session.refresh(self.c_target)
            print(self.c_target.metadata_)
            print(self.c_target.notes)

    def set_slice_md(self,markDict): #FIXME seems like this might be related to our errors?
        self.c_slice.markDict=markDict
        self.session.add(self.c_slice)
        #print(self.c_slice.markDict)
        try:
            self.session.commit()
        except:
            session.rollback()
            raise

    def printAll(self):
        print(self.c_person.strHelper())
        print(repr(self.c_project))
        print(repr(self.c_experiment))
        print(repr(self.c_slice))
        print(self.c_cells)
        print(repr(self.c_datafile))
        print('target:',repr(self.c_target))

    def newDataFileCallback(self):
        new_df=self.session.query(DataFile).order_by(DataFile.creationDateTime.desc()).first()
        printD('c_datafile set to %s'%new_df)
        self.c_datafile=new_df
        self.c_target=new_df
    
    def newDataFile(self,extension,experiment,subjects=[],dfs=None): #FIXME need other selectors eg: repository >_<
        repo,dfs=self.getRepoDFS(extension)
        #experiment=Get_newest_id(Experiment) #FIXME unfinished?
        rpath=repo.path
        if rpath[2] == ':':
            rpath = rpath[1:] #FIXME stupid windows paths
        filename=Get_newest_file(rpath,extension) #FIXME this can be faster than the snapshot! FIXME race conditions!!!!
        print(filename,'will be added to the current experiment!')
        new_df=DataFile(filename=filename,url=repo.url,datafilesource_id=dfs.id,
                            experiment_id=experiment.id,Subjects=subjects)

        self.add_com_sess(new_df)
        return new_df

    @keyRequest
    def newNote(self): #FIXME need a way to hit a single cell
        note=self.__getChars__('note> ')
        #try:
            #iter(self.c_target)
            #for t in self.c_target:
                #n=t.Note(note,t)
                #self.session.add(n)
        #except:
        n=self.c_target.Note(note,self.c_target)
        self.session.add(n)
        #finally:
        self.session.commit()

    @keyRequest
    def newExperiment(self): #FIXME this fails because of how dictMan works...
        session=self.session
        #session=self.Session()
        types=session.query(ExperimentType).all()
        print('please enter the type of experiment, available types are: %s'%[t.abbrev for t in types])
        type_=None
        type_string=self.__getChars__('type>')
        type_=[t for t in types if t.abbrev==type_string]
        if self.c_experiment: #FIXME this is here to prevent keyhandler from going haywire
            #if session.query(Experiment).get(self.c_experiment.id): #FIXME if an experiment is deled elsewhere
            print('[!] You already have an experiment, end the current one first!')
            return self
            #else:
                #self.c_experiment=None #FIXME actually noat an issue it would seem
                #print('[!] It would seem that you current expeirment got deleted...')
        if type_:
            if type_[0].abbrev=='patch':
                se=session.query(Experiment).join(ExperimentType,Experiment.type).filter(ExperimentType.abbrev=='slice').order_by(Experiment.id.desc()).first()
                if not se:
                    print('[!] There is no slice experiment on record! Please add one!')
                    return self
            experiment=Experiment(type_id=type_[0],project_id=self.c_project,person_id=self.c_person)
            session.add(experiment)
            try: 
                session.commit()
                self.c_experiment=experiment
                self.c_target=experiment
                print('New experiment added = %s'%self.c_experiment.strHelper())
            except :
                print('[!] experiment NOT added')
                session.rollback() #FIXME could be dangerous? if others are in the session?
            finally:
                #session.close()
                pass
        else:
            print('Invalid type: experiment not created')
        return self
    #newExperiment.keyRequester=True

    def newSlice(self):
        if self.c_slice:
            #raise BaseException('You already have a slice on the rig!')
            print('[!] You already have a slice on the rig!')
            return self
        elif not self.c_experiment:
            print('[!] You have not added an experiment!')
            return self
        session=self.session
        #session=self.Session()
        ge=session.query(Experiment).join(ExperimentType,Experiment.type).filter(ExperimentType.abbrev=='slice').order_by(Experiment.id.desc()).first()
        if not ge:
            print('[!] There is no slice experiment on record! Please add one!')
            return self
        slice_=Slice(generating_experiment_id=ge)
        slice_.experiments.append(self.c_experiment)
        session.add(slice_)
        try:
            session.commit()
            self.c_slice=slice_
            self.c_target=slice_
            print('New slice added = %s'%repr(self.c_slice))
        except:
            session.rollback()
        finally:
            #session.close()
            pass

    def newCell(self):
        if not self.c_experiment:
            print('[!] Cells dont really belong in slice prep experiments')
            return self
        elif self.c_experiment.type.abbrev=='slice':
            print('[!] Cells dont really belong in slice prep experiments')
            return self
        if len(self.c_cells) >=2:
            print('[!] You already have 2 cells! New rig eh?')
            return self
        if not self.c_slice:
            print('You do not have a slice on the rig!')
            return self
            #raise BaseException('You do not have a slice on the rig!')
        #self.__getChars__('headstage>')
        cell=Cell(parent_id=self.c_slice.id,generating_experiment_id=self.c_experiment)
        cell.experiments.append(self.c_experiment)
        session=self.session
        #session=self.Session()
        session.add(cell)
        try:
            session.commit()
            self.c_cells.append(cell)
            self.c_target=cell #FIXME
            print('New cell added = %s'%repr(cell))
        except:
            session.rollback()
        finally:
            #session.close()
            pass
    #newCell.keyRequester=True
    
    @keyRequest #FIXME?
    def getBrokenIn(self):
        if self.getBool('Hit space if you broke in otherwise fail!'):
            #TODO metadata on breakin?
            print('Yay!')
        else:
            print('Your failure has been noted.')
            #self.c_target.notes.append('FAILURE MESSAGE') #TODO
            self.headstage_state[self.c_target.headstage]=None #FIXME dangerous :(
            self.endCell(self.c_target) #FIXME make sure this works?
        return self

    def endDataFile(self):
        if not self.c_datafile:
            print('No datafile to end')
            return None
        self.c_datafile=None
        self.c_target=self.c_cells[0]

    def endCell(self,cell=None): #TODO I think it might be worth having a c_cell in addition??!?
        if not self.c_cells:
            print('No cell to end.')
            return self
        if not cell and type(self.c_target) is not Cell:
            print('Current target is not a cell!')
            return self
        elif not cell: #FIXME
            cell=self.c_target

        cell.endDateTime=datetime.now()
        self.session.commit()
        self.c_cells.remove(cell)
        self.headstage_state[cell.headstage]=None #FIXME TODO need to track this with experiment state or something in case of chrashes
        print('Ended cell %s'%cell.strHelper())
        if self.c_cells:
            self.c_target=self.c_cells[0] #FIXME
        else:
            self.c_target=self.c_slice
        return self

    def endSlice(self): #TODO location in the pfa well?
        if not self.c_slice:
            print('No slice to end.')
            return self
        if self.c_cells:
            print('You still have cells! Please end them first!')
            return self
        self.c_slice.endDateTime=datetime.now()
        session=self.session
        #session=self.Session()
        #session.add(self.c_slice)
        session.commit()
        print('Ended slice %s'%self.c_slice.strHelper())
        self.c_slice=None
        self.c_target=self.c_experiment

    def endExperiment(self):
        if not self.c_experiment:
            print('No experiment to end.')
            return self
        if self.c_slice:
            print('[!] You still have slices! End them first!')
            return self
        self.c_experiment.endDateTime=datetime.now()
        session=self.session
        #session=self.Session()
        #session.add(self.c_experiment)
        session.commit()
        print('Ended experiment %s'%self.c_experiment.strHelper())
        self.c_experiment=None
        self.c_target=None
    
#@datafile_maker#@hardware_interface('Digidata 1322A')
class clxFuncs(kCtrlObj):
    def __init__(self, modestate, clx=None, **kwargs):
        #if not clx:
            #clx=kwargs['clx']
        try:
            if clx.__class__.__name__ is not 'clxControl':
                raise TypeError('wrong controller type %s'%clx.__class__)
        except:
            raise
        #from clx import clxControl
        self.clx=clx

        super().__init__(modestate,**kwargs)
        #self.initController(clxmsg)
        #printD('clx ctrl',self.clx)
        #self.clxCleanup=self.cleanup
        self.programDict={}
        self.current_program=''
        #self.wrapDoneCB()
        if not self.getStatus():
            self.TESTING=1
            print('WARNING: CLAMPEX IS RUNNING IN FAKE MODE')
            func=lambda *args,**kwargs: print('POOPBUTT')
            self.loadfile=func
            self.load=func
            self.record=func
            self.view=func
            self.stop_rec=func



    #class only
    def readProgDict(self,progDict):
        self.programDict=progDict
        return self

    def setProtocolPath(self,protoPath):
        print('PROTOCOL PATH SET %s'%protoPath)
        self.protocolPath=protoPath

    def cleanup(self):
        super().cleanup()
        try:
            self.clx.DestroyObject()
            print(self.clx.__class__,'handler destroyed')
        except:
            pass
            #print('this this works the way it is supposed to the we should never have to destory the object')


    #input with output
    def getStatus(self,outputs=None): #TODO outputs... should be able to output to as many things as I want... probably should be a callback to simplify things elsewhere? no?!?!
        status=self.clx.GetStatus()
        print(status)
        if status == 'CLAMPEX IS NOT RUNNING':
            return 0
        else:
            return 1

    def wait_till_done(self):
        gs=self.clx.GetStatus
        while gs() != 'CLXMSG_ACQ_STATUS_IDLE' and self.keyThread.is_alive():
            sleep(.001) #FIXME
        print('Done recording')

    def loadfile(self,filename):
        try:
            filepath=self.protocolPath+filename
            print(filepath)
            self.clx.LoadProtocol(filepath.encode('ascii'))
            self.current_program=filepath
            print('%s loaded!'%filepath)
        except BaseException as e:
            print(e)

    #@keyRequest
    def load(self,key):
        #if not key:
            #print('Please enter the program to load')
            #key=self.charBuffer.get()
        try:
            filename=self.programDict[key]
            filepath=self.protocolPath+filename
            self.clx.LoadProtocol(filepath.encode('ascii'))
            self.current_program=filepath
            print('%s loaded!'%filepath)
        except BaseException as e:
            print(e)
            #print('Program not found')
            #raise
        return self

    #@new_abf_DataFile() #XXX deprecated
    def record(self):
        #RECORD=109, RERECORD=110, VIEW=108
        try:
            self.clx.StartAcquisition(109)
            print('Running %s'%self.current_program)
        except:
            raise
        return self

    def view(self):
        #RECORD=109, RERECORD=110, VIEW=108
        try:
            self.clx.StartAcquisition(108)
            print('Viewing %s'%self.current_program)
        except:
            raise
        finally:
            return self
    
    def stop_rec(self):
        self.clx.StopAcquisition()
        print('Stopping curren acquistion')


    #input only
    def startMembTest(self):
        self.clx.StartMembTest(120)
        self.clx.StartMembTest(121)
        return self


#@hardware_interface('mc1') #FIXME or is it software interface?
class mccFuncs(kCtrlObj): #FIXME add a way to get the current V and I via... telegraph?
    def __init__(self, modestate, mcc=None, **kwargs):
        #if not mcc:
            #mcc=kwargs['mcc']
        try:
            if mcc.__class__.__name__ is not 'mccControl':
                raise TypeError('wrong controller type')
        except:
            raise
        #from mcc import mccControl
        self.mcc=mcc

        super().__init__(modestate,**kwargs) #better error messages?
        #self.initController(mccmsg)
        self.MCCstateDict={}
        #self.wrapDoneCB()
        self.headstage_state={ chan:0 for chan in range(mcc.mcNum)}
        
        #associated metadata sources
        #self.state1DataSource=None

    def setGain(self,value=1):
        self.mcc.SetPrimarySignalGain(value)
        print('Primary signal gain set to %s'%value)
        return self

    def allGain(self,value=1):
        self.mcc.selectMC(0)
        self.mcc.SetPrimarySignalGain(value)
        self.mcc.selectMC(1)
        self.mcc.SetPrimarySignalGain(value)
        return self

    def setMCCState(self,stateList):
        """ ste the mcc state from a mcc state dict list """
        for state in stateList:
            self.mcc.selectMC(state['Channel'])
            self.mcc.SetMode(state['mode'])
            self.mcc.SetHolding(state['Holding'])
            self.mcc.SetHoldingEnable(state['HoldingEnable'])
            self.mcc.SetPrimarySignal(state['PrimarySignal'])
            self.mcc.SetPrimarySignalGain(state['PrimarySignalGain'])
            self.mcc.SetPrimarySignalLPF(state['PrimarySignalLPF'])
        return self

    def getMCCState(self): #FIXME this function and others like it should probably be called directly by dataman?
        printD('hMCCmsg outer',self.mcc.hMCCmsg)
        def base(state):
            state['HoldingEnable']=self.mcc.GetHoldingEnable()
            state['Holding']=self.mcc.GetHolding()
            state['PrimarySignal']=self.mcc.GetPrimarySignal()
            state['PrimarySignalGain']=self.mcc.GetPrimarySignalGain() #also in abf file and already handled by AxonIO
            state['PrimarySignalLPF']=self.mcc.GetPrimarySignalLPF() #also in abf file
            state['PipetteOffset']=self.mcc.GetPipetteOffset()

            #XXX ONLY RELEVANT FOR MODE 0 (VC)
            state['FastCompCap']=self.mcc.GetFastCompCap()
            state['SlowCompCap']=self.mcc.GetSlowCompCap()
            state['FastCompTau']=self.mcc.GetFastCompTau()
            state['SlowCompTau']=self.mcc.GetSlowCompTau()
            state['SlowCTX20Enable']=self.mcc.GetSlowCompTauX20Enable()

            #XXX ONLY RELEVANT FOR MODE 1 (IC)
            state['BridgeBalEnable']=self.mcc.GetBridgeBalEnable()
            state['BridgeBalResist']=self.mcc.GetBridgeBalResist()

        #modeDict={0:vc,1:ic,2:iez}
        stateList=[]
        for i in range(self.mcc.mcNum):
            self.mcc.selectMC(i)
            state={} #FIXME: make this a dict with keys as the name of the value? eh would probs complicate
            state['Channel']=i #might be suprflulous but it could simplify the code to read out stateList
            mode=self.mcc.GetMode()
            state['mode']=mode
            #modeDict[mode](state)
            base(state)
            stateList.append(state)
            #print()
            #print(state)

        self.MCCstateDict[datetime.utcnow()]=stateList
        #print(stateList)
        return stateList

    def stateToDataFile(self): #AAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH SO BAD FIXME
        #XXX DEPRECATED
        #datFunc=self.modestate.ctrlDict['datFuncs']
        df=self.c_datafile
        stateList=self.getMCCState()
        df.mddictlist=stateList
        datFunc.session.commit()
        return self #IF THIS WORKS I WILL BUY A HAT AND EAT IT WAIT I ALREADY HAVE A HAT


    def printMCCstate(self):
        print(re.sub('\), ',')\r\n',str(self.MCCstateDict)))
        return self


    def set_hs0(self):
        print('Setting headstage 0')
        self.mcc.selectMC(0)
        self.current_headstage=0
        return self
    def set_hs1(self):
        print('Setting headstage 1')
        self.mcc.selectMC(1)
        self.current_headstage=1 #TODO use this to link cells to the headstage!
        return self
    def set_hsAll(self): #FIXME
        self.ALL_HS=True

    def autoOffset(self):
        self.mcc.AutoPipetteOffset()
    def autoCap(self):
        self.mcc.AutoFastComp()
        self.mcc.AutoSlowComp()
    def setVCholdOFF(self):
        self.mcc.SetMode(0)
        self.mcc.SetHoldingEnable(0)
    def setVCholdON(self):
        self.mcc.SetMode(0)
        self.mcc.SetHoldingEnable(1)

    def setVChold(self,holding_volts):
        #print(holding_volts)
        self.mcc.SetMode(0)
        print(holding_volts)
        self.mcc.SetHolding(float(holding_volts))
        h=self.mcc.GetHolding()
        print(h)
        #sleep(.001) #FIXME trying to figure out why holding set to -1000mV
        #self.mcc.SetHoldingEnable(1)
    def setICnoHold(self):
        self.mcc.SetMode(1)
        self.mcc.SetHoldingEnable(0)

    def allVChold(self,holding_volts):
        self.mcc.selectMC(0)
        self.mcc.SetMode(0)
        self.mcc.SetHolding(float(holding_volts))
        #self.mcc.SetHoldingEnable(1)
        self.mcc.selectMC(1)
        self.mcc.SetMode(0)
        self.mcc.SetHolding(float(holding_volts))
        #self.mcc.SetHoldingEnable(1)
        return self

    def allIeZ(self):
        self.mcc.selectMC(0)
        self.mcc.SetMode(2)
        self.mcc.selectMC(1)
        self.mcc.SetMode(2)
        return self
    def allVCnoHold(self):
        #try:
        self.mcc.selectMC(0)
        self.mcc.SetMode(0)
        self.mcc.SetHoldingEnable(0)
        self.mcc.selectMC(1)
        self.mcc.SetMode(0)
        self.mcc.SetHoldingEnable(0)
        #except:
            #raise BaseException
        return self
    def allVChold_60(self):
        self.mcc.selectMC(0)
        self.mcc.SetMode(0)
        self.mcc.SetHolding(-.06)
        self.mcc.SetHoldingEnable(1)
        self.mcc.selectMC(1)
        self.mcc.SetMode(0)
        self.mcc.SetHolding(-.06)
        self.mcc.SetHoldingEnable(1)
        return self
    def allICnoHold(self):
        self.mcc.selectMC(0)
        self.mcc.SetMode(1)
        self.mcc.SetHoldingEnable(0)
        self.mcc.selectMC(1)
        self.mcc.SetMode(1)
        self.mcc.SetHoldingEnable(0)
        return self
    def testZtO(self,holding_voltage):
        self.mcc.selectMC(0)
        self.mcc.SetMode(1)
        self.mcc.SetHoldingEnable(0)
        self.mcc.selectMC(1)
        self.mcc.SetMode(0)
        self.mcc.SetHolding(float(holding_voltage))
        self.mcc.SetHoldingEnable(1)
        return self
    def testOtZ(self,holding_voltage):
        self.mcc.selectMC(0)
        self.mcc.SetMode(0)
        self.mcc.SetHolding(float(holding_voltage))
        self.mcc.SetHoldingEnable(1)
        self.mcc.selectMC(1)
        self.mcc.SetMode(1)
        self.mcc.SetHoldingEnable(0)
        return self
    def zeroVChold_60(self):
        self.mcc.selectMC(0)
        self.mcc.SetMode(0)
        self.mcc.SetHolding(-.06)
        self.mcc.SetHoldingEnable(1)
        return self
    def oneVChold_60(self):
        self.mcc.selectMC(1)
        self.mcc.SetMode(0)
        #self.mcc.poops(1) #awe, this is broken now due to something
        self.mcc.SetHolding(-.06)
        self.mcc.SetHoldingEnable(1)
        return self
    def cleanup(self):
        super().cleanup()
        try:
            self.mcc.DestroyObject()
            print(self.mcc.__class__,'handler destroyed')
        except:
            pass


#@hardware_interface('ESP300')
class espFuncs(kCtrlObj):
    def __init__(self, modestate, esp=None, **kwargs):
        #if not esp:
            #esp=kwargs['esp']
        try:
            if esp.__class__.__name__ is not 'espControl':
                raise TypeError('wrong controller type')
        except:
            raise
        #from esp import espControl
        self.esp=esp


        super().__init__(modestate,**kwargs)
        self.markDict={} #FIXME
        self.posDict={} #FIXME
        #self.initController(npControl)
        self.modestate=modestate
        self.setMoveDict()
        self.move_list=[]
        self.motor_on=False
        #self.event=modestate.event
        
        #associated metadatasources:
        #self.EspXDataSource=None
        #self.EspYDataSource=None

    #@is_mds('m','m','ESP300',5)
    def getPos(self):
        """ get the (x,y) position of the eps300 """
        #may want to demand a depth input (which can be bank)
        #try:
        pos=self.esp.getPos()
        #self.doneCB()
        self.posDict[datetime.now()]=pos #FIXME dat should handle ALL of this internally
        print(pos)
        #except:
            #printD('oops')
            #raise
        return list(pos)

    def motorToggle(self):
        self.esp.motorToggle()

    def printPosDict(self):
        #self.doneCB()
        print(re.sub('\), ',')\r\n',str(self.posDict)))
        return self

    def set_move_list(self,move_list): #FIXME TODO should probably be saved at the... slice level?
        self.move_list=move_list
        self._current_move_list_index=0
        self._current_move_list_pos=0

    def moveNext(self):
        if not self.move_list:
            print('No movelist! not moving')
            return None
        else:
            #stdout.write('\rMoving to next position')
            #stdout.flush()
            self.esp.BsetPos(self.move_list[self._current_move_list_pos])
            if self._current_move_list_pos + 1 < len(self.move_list):
                self._current_move_list_pos+=1
            else:
                print('Move list is done! Resetting to the start!')
                self._current_move_list_pos=0

    @keyRequest
    def mark(self): #FIXME seems like this might be where the crashes are coming from?
        """mark/store the position of a cell using a character sorta like vim"""
        try:
            #slice_md=self.modestate.ctrlDict['datFuncs'].c_slice.markDict
            slice_md=self.c_slice.markDict
            self.markDict=slice_md
        except AttributeError:
            pass
        stdout.write('\rmark> ')
        stdout.flush()
        key=self.charBuffer.get()
        #printD('we got the key from charBuffer')
        if key in self.markDict:
            print('Mark %s is already being used, do you want to replace it? y/N'%(key))
            yeskey=self.charBuffer.get()
            #self._releaseKR() #XXX
            if yeskey=='y' or yeskey=='Y':
                self.markDict[key]=self.esp.getPos()
                print(key,'=',self.markDict[key])
            else:
                print('No mark set')
        elif key=='esc':
            self.unmark()
        else:
            #self._releaseKR() #XXX
            self.markDict[key]=self.esp.getPos()
            print(key,'=',self.markDict[key])
        #self.keyHandler(getMark) #fuck, this could be alot slower...
        try:
            #self.modestate.ctrlDict['datFuncs'].set_slice_md(self.markDict) #FIXME WARNING
            self.set_slice_md(self.markDict) #FIXME WARNING
        except AttributeError:
            pass
            #raise
        return self
    #mark.keyRequester=True

    @keyRequest
    def unmark(self):
        #self.doneCB()
        try:
            mark=self.charBuffer.get()
            pos=self.markDict.pop(mark)
            print("umarked '%s' at pos %s"%(mark,pos))
            try:
                #self.modestate.ctrlDict['datFuncs'].set_slice_md(self.markDict)
                self.set_slice_md(self.markDict) #FIXME WARNING
            except:
                raise
        except KeyError:
            stdout.write('\n')
            stdout.flush()
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
            print('Moved to: ',self.esp.BsetPos(self.markDict[key])) #AH HA! THIS is what is printing stuff out as I mvoe FIXME I removed BsetPos at some point and now I need to add it... back? or what
        else:
            print('No position has been set for mark %s'%(key))
        return self
    #gotoMark.keyRequester=True

    @keyRequest
    def mark_to_movelist(self,step_um=None,number=None,points=[]):
        marks='origin','target'
        if len(points) != len(marks):
            points=getMarks(marks)

        from rig.calcs import random_vector_points, vector_points, random_vector_ret_start
        #moves=vector_points(*args,number=number,spacing=step/1000) #.05 mm = 50um
        #moves=random_vector_points(*args,number=number,spacing=step/1000) #.05 mm = 50um

        moves=random_vector_ret_start(*points,number=number,spacing=step_um/1000)

        self.set_move_list(moves)
        return self

    @keyRequest
    def mark_to_cardinal(self,step_um=25,number=8,points=[]): #FIXME need a way to reload marks at startup!
        from numpy.random import shuffle
        from rig.calcs import vector_points, intersperse

        marks='start','dorsal','ventral','medial','lateral'
        if len(points) != len(marks):
            points=getMarks(marks)

        base=[points[0]]
        for point in points[1:]:
            pts=vector_points(points[0],point,number=number,spacing=step_um/1000)[1:] #drop the origin
            base.extend(pts)

        shuffle(base)
        moves=[points[0]] #we need our first calibration point
        moves.extend([m for m in intersperse(base,points[0])])
        moves.append(points[0]) #add the last validation origin point
        #print(moves)
        #print(len(moves))
        self.set_move_list(moves)
        #return moves
        return self

    @keyRequest
    def getMarks(self,marks=[1,2,3]):
        points=[]
        for i in range(len(marks)):
            stdout.write(marks[i]+'> ')
            stdout.flush()
            key=self.charBuffer.get()
            stdout.write(key)
            stdout.flush()
            if key in self.markDict:
                points.append(self.markDict[key]) #x,y,x,y
                stdout.write('\n')
                stdout.flush()
            else:
                raise IOError('Mark not found exiting.')
                #return None
        return points

    @keyRequest
    def mark_to_spline(self,step_um=100,number=10,points=[]):
        from rig.calcs import get_moves_from_points
        from numpy.random import shuffle
        from analysis.abf_analysis import get_tmp_path #FIXME

        marks='start','one','two','three','four','five'
        if len(points) != len(marks):
            points=self.getMarks(marks)

        moves=get_moves_from_points(points,points[0],number,step_um/1000,switch_xy=True) #XXX NOTE THE SWITCH XXX
        start=-moves[0][0],moves[0][1]+.1

        shuffle(moves)
        self.set_move_list(moves)

        def _plot(start,moves,points): #TODO thread this
            switch_backend('Agg')
            figure(figsize=(4,4))
            plot(start[0],start[1],'yo')
            [plot(-m[0],m[1],'ro') for m in points]
            [plot(-m[0],m[1],'go') for m in moves]
            axis('equal')
            cellids=''.join(['%s_'%c.id for c in self.c_cells])
            savefig(get_tmp_path()+'/s%s_c%spts_mvs.png'%(self.c_slice.id,cellids),bb_inches='tight',pad_inches=0) #FIXME copies
            print(moves)
            print(len(moves))
        pltThrd=Thread(target=_plot,args=(start,moves,points))
        pltThrd.start()
        return self

    def makeNewMoveList(self,move_pattern=None,number=None,step_um=None,points=[]):
        make_func={'spline':self.mark_to_spline,'line':self.mark_to_movelist,'cross':self.mark_to_cardinal}[move_pattern]

        if not step_um:
            step_um=self.getFloat('step um>')
        if not number:
            number=self.getInt('number>')

        if not make_func(step_um,number,points):
            raise IOError('No move dict set!')

    @staticmethod
    def plotMarks(slice_id,markDict):
        from analysis.abf_analysis import get_tmp_path #FIXME
        from numpy import vstack
        asdf=vstack(markDict.values()) 
        switch_backend('Agg')
        figure(figsize=(4,4))
        plot(-asdf[:,0],asdf[:,1],'ko')
        for mark,(x,y) in markDict.items():
            annotate(
                '%s'%mark, xy=(-x,y) , xytext=(5,5),
                textcoords = 'offset points', ha = 'right', va = 'bottom',
                #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                #arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'),
            )
        axis('equal')
        path=get_tmp_path()
        savefig(path+'/s%s_markdict.png'%slice_id,bb_inches='tight',pad_inches=0)
        
    def printMarks(self):
        """print out all marks and their associated coordinates"""
        try:
            #slice_md=self.modestate.ctrlDict['datFuncs'].c_slice.markDict
            slice_md=self.c_slice.markDict #should work coop...

            self.markDict=slice_md
            pltThrd=Thread(target=self.plotMarks,args=(self.c_slice.id,self.markDict))
            pltThrd.start()
        except AttributeError:
            pass
        print(re.sub('\), ','),\r\n ',str(self.markDict)))
        return self

    def fakeMove(self):
        #self.doneCB()
        if self.esp.sim:
            from numpy import random #only for testing remove later
            a,b=random.uniform(-10,10,2) #DO NOT SET cX or cY manually
            self.esp.setPos((a,b))
            #print(self.esp._cX,self.esp._cY)
        else:
            print('Not in fake mode! Not moving!')
        return self

    #callback to break out of display mode
    def _gd_break_callback(self): #XXX showDisp now
        print('leaving disp mode!')
        self._gd_exit=1
        self.modestate.keyActDict['esc']=self._gd_old_esc
        self._gd_old_esc=None
        del(self._gd_old_esc)
        self.modestate.keyActDict[self._gd_own_key]=self.showDisp
        self._gd_own_key=None
        del(self._gd_own_key)

    #@keyRequest #just added the getDisp.keyRequester=True at the bottom and we're good to go
    def showDisp(self):
        """BLOCKING stream the displacement from a set point"""
        #self.doneCB()
        from numpy import sum as npsum #FIXME should these go here!?
        from numpy import array as arr
        print('entering disp mode')

        if not len(self.markDict):
            try:
                #self.markDict.update(self.modestate.ctrlDict['datFuncs'].c_slice.markDict)
                self.markDict.update(self.c_slice.markDict)
            except:
                pass #in the event there is no slice we don't really need to tell anyone
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
        self._gd_own_key=get_key(self.modestate.keyActDict,self.showDisp)
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
            dist=(npsum((arr(self.esp._BgetPos()-arr(list(pos))))**2,axis=1))**.5 #FIXME the problem here is w/ _BgetPos()
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
    showDisp.keyRequester=True

    def setSpeedDef(self):
        #self.doneCB()
        self.esp.setSpeedDefaults()
        return self

    def cleanup(self):
        super().cleanup()
        self.esp.cleanup()
        return self

    def setMoveDict(self,moveDict={'w':'up','s':'down','a':'left','d':'right'}):
        self.moveDict=moveDict
        return self

    def move(self): #FIXME this does not work in displacement mode because modestate.key is always i
        key=self.modestate.key
        #printD(key)
        if key.isupper(): #shit, this never triggers :(
            #printD('upper')
            self.esp.move(self.moveDict[key.lower()],.05) #FIXME
        else:
            #printD('lower')
            self.esp.move(self.moveDict[key.lower()],.1)
        return self

    def printError(self):
        print('Error:',self.esp.getErr().decode('utf-8'))
        return self
    def readProgram(self):
        #self.keyHandler(1)
        #num=self.charBuffer.get()
        print(self.esp.readProgram())
        return self



#@datafile_maker
class guiFuncs(kCtrlObj): #FIXME GOD DAMN IT now hardware interfaces and datafile makers are not sufficient because this gui could interface with a ton of stuff >_<
    #@new_DataFile('jpg') #TODO integrate this with the device and stick it in a dedicated paths config file, could look it up by program but...
    def getCameraImage(self): #XXX: getSub_getCameraImage via df maker
        takeScreenCap()
        sleep(1) #ICK some day a callback FIXME



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


#@hardware_interface('keyboard')
class trmFuncs(kCtrlObj): #FIXME THIS NEEDS TO BE IN THE SAME THREAD
    def __init__(self, modestate):
        self._keyThread=modestate.keyThread
        self.keyLock=modestate.keyLock
        self.modestate=modestate #need this to det the current modestate
        super().__init__(modestate)
        #def printwrap(func):
            #def wrap(*args,**kwargs):
                #out=func()
                #printD(out)
                #return out
            #wrap.__name__=func.__name__
            #return wrap
        #for name in self.ctrl.__dir__():
            #if name[:3]=='get':
                #setattr(self,name,printwrap(getattr(self.ctrl,name)))
        #for name in self.__dir__():
            #if name[:3]=='get':
                #setattr(self,name,printwrap(getattr(self,name)))
                #setattr(getattr(self,name),'__name__',name)

    #@is_mds('u','m','BX51WI',0)
    @keyRequest
    def getDistance_um(self):
        """ get a distance in um in this case read from the olympus bx51wi wheel """
        value=self.getFloat('distance um> ')
        return value

    @keyRequest
    def getKbdHit(self,prompt='Hit any key to advance.'):
        print(prompt)
        key=self.charBuffer.get()
        if key == '@': #nasty hack for dealing w/ exits FIXME
            raise IOError('Program has terminated!')
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
    def command(self): #TODO
        """ vim : mode """
        #TODO figure out where to move the command dict...
        #cmdDict={'ipython':'ipython'} #can't put ipython here due to race conditions
        cmdDict={}
        def parse_command(com_str): #TODO
            if com_str=='\n':
                return None
            def match_key(com_str):
                printD(com_str)
                matches = [key for key in cmdDict.keys() if key[:len(com_str)]==com_str]
                matches.sort()
                return matches
            matches=match_key(com_str)
            printD(matches)
            try:
                if matches:
                    func=getattr(self,matches[0],lambda:None)
                else:
                    return None
            except:
                print('[!] no function found')
                return None
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
    #esp=espFuncs()
    #clx=clxFuncs()
    #mcc=mccFuncs(None,None,None,None)
    pass

__all__=(
    'clxFuncs',
    'mccFuncs',
    'espFuncs',
    'keyFuncs',
    'trmFuncs',
    'datFuncs',
    'guiFuncs',
)
if __name__=='__main__':
    main()
