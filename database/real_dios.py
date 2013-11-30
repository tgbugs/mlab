#see steps.py and rig/metadatasources.py for inspiration
import os
import glob
from numpy import mean
from sqlalchemy.orm import object_session
from database.dataio import Get, Set, Bind, Read, Write, Analysis, Check #FIXME make these decorators for a do() function? this should enable reusable chaining with doccumentation?
#should the decorator(properties) be how we do default kwargs or should we just define them locally and persist those?
from database.models import Setter, Getter, Binder, Reader, Writer, Analyzer, Checker, MetaDataSource, DataFile
from time import sleep
from database.imports import printD

#decoratos

def getter(**kwargs):
    #use kwargs to set the properties of the getter
    def getter_dec(function):
        def persist(): #the logic to persist the function
            pass
        def put_in_dict(): #the logic to put the function in dioDict
            pass
        def wrapped(**func_kwargs):
            print('do something')
            return function(**func_kwargs)
        return wrapped
    return getter_dec


###--------
### dataios
###--------

#TODO really need to clean up the underlying data structure so that units and dimensions are transparent :/

#a janky metadata writer :/
class Write_MetaData(Write):
    MappedClass=Writer
    #from database.models import ?????? as MappedWriter #BALLS TODO looks like I need to rework MetaData :/
    #TODO do we really need dependencies for this? I don't think so since there are just SO many things
    #TODO also this sucks because I have to write down the name of every bloody dataio and check the kwarg for a write :/
    MappedWriter=type('MetaData',(object,),{}) #FIXME this is to make persist work right

    def write(self,writeTarget=None,autocommit=False,**kwargs):
        self.MappedWriter=writeTarget.MetaData
        session=object_session(writeTarget)
        kwargs['metadatasource_id']=session.query(self.MappedClass).filter_by(name=kwargs['last_getter']) #FIXME we REALLY need to clean up the dicts when we're done or shit is going to get UGLY
        kwargs['value']=kwargs[kwargs['last_getter']]
        #XXX NOTE: 'last_getter' does happen to be super useful though since that way we can seemlessly write to multiple objects using value=kwargs[kwargs['last_getter']]
        super().write(writeTarget=writeTarget,autocommit=autocommit,**kwargs)
        kwargs.pop('value') #ICK

#dealing with the TYPE orthogonally from the UNIT, this is NOT the best way... FIXME
class Get_float(Get):
    pass
class Get_bool(Get):
    pass
class Get_int(Get):
    pass

###
#BASIC

class Check_deps_done(Check):
    """ Use for checkpoint steps basically acts as flow control """
    MappedClass=Checker
    #check_function=lambda **kwargs:True
    @staticmethod
    def check_function(**kwargs):
        return True
    


###
#TRM
class Get_trmDoneNB(Get): #FIXME threading nightmare
    """ get step done/in position/state achieved without blocking """
    MappedClass=Getter
    ctrl_name='trmFuncs'
    function_name='getDoneNB'
    hardware='keyboard'

class trm_get(Get):
    """ baseclass to manage key requests"""
    def do(self,**kwargs):
        #print('*** 84 in real_dios.py',getattr(self.ctrl,self.function_name))
        printD(self.function_name,self.ctrl.modestate.modeKRDict[self.function_name])
        #if hasattr(getattr(self.ctrl,self.function_name),'keyRequester'):
        try:
            count=self.ctrl.modestate.modeKRDict[self.function_name]
            try:
                self.ctrl.modestate.krdLock.acquire()

                #printD(self.ctrl.modestate.keyRequestDict[self.function_name])
                printD(count)
                self.ctrl.modestate._keyRequest+=count
                #self.ctrl.modestate.keyRequestDict[self.function_name]
            except:
                raise
            finally:
                self.ctrl.modestate.krdLock.release()
        except:
            pass

        return super().do(**kwargs)

class Get_trmDoneORFail(Get):
    """ Get step done or step failed should be used for any external report of a failed step """
    MappedClass=Getter
    ctrl_name='trmFuncs'
    function_name='getDoneFailNB'
    hardware='keyboard'

class Get_trmBool(trm_get):
    """ get bool via rigio """
    MappedClass=Getter
    ctrl_name='trmFuncs'
    function_name='getBool'
    hardware='keyboard'

class Get_trmString(trm_get):
    """ get string via rigio """
    MappedClass=Getter
    ctrl_name='trmFuncs'
    function_name='getString'
    hardware='keyboard'

class Get_trmInt(trm_get):
    """ get int via rigio """
    MappedClass=Getter
    ctrl_name='trmFuncs'
    function_name='getInt'
    hardware='keyboard'

class Get_trmFloat(trm_get):
    """ get float via rigio """
    MappedClass=Getter
    ctrl_name='trmFuncs'
    function_name='getFloat'
    hardware='keyboard'

class Get_trm_dist_um(Get_trmFloat):
    """ get a distance in um via terminal input """
    MappedClass=MetaDataSource
    mcKwargs={'prefix':'u','unit':'m','mantissa':0}

        



###
#ESP
class Get_espX(Get):
    """ Gets the X position from the esp300"""
    MappedClass=MetaDataSource
    mcKwargs={'prefix':'m','unit':'m','mantissa':5} #FIXME this is a horrible use case, it makes it easy to make a ton of them, but it makes everything super hard to read ;_;
    ctrl_name='espControl'
    function_name='getX'
    hardware='esp300'


class Get_espY(Get):
    """ Gets the Y position from the esp300"""
    MappedClass=MetaDataSource
    mcKwargs={'prefix':'m','unit':'m','mantissa':5}
    ctrl_name='espControl'
    function_name='getY'
    hardware='esp300'


class Bind_espXY(Bind): #FIXME experimental... requires dependent classes to reside together atm
    """ gets espx and espy and binds them into an (x,y) tuple"""
    MappedClass=Binder
    out_format=['Get_espX','Get_espY'] #FIXME need to change how we do dataio deps vs step deps
        #dataio deps seem like they should just blindly get, but do note that there may be missing kwargs!
    def __init__(self,session,ctrlDict):
        self.depDict={} #FIXME why not just load up all the dataios in a dict and get them by name?
            #do it in parallel for steps... do that, but not right now, and this way is more mem eff?
        for dio in self.out_format:
            self.depDict[dio]=globals()[dio](session=session,ctrlDict=ctrlDict)
        super().__init__(session,ctrlDict=ctrlDict)
    def bind(self,**kwargs):
        out=[]
        for kw in self.out_format: #FIXME figure out how to do with w/o a for loop! (collections maybe?)
            out.append(self.depDict[kw].do(**kwargs)[kw]) #FIXME this kwargs passing... >_< stepname dataio name conflicts and all the rest ;_;
        return out

class Bind_dep_vals(Bind): #FIXME
    """ poop """
    #ctrl_name='espControl' #FIXME
    MappedClass=Binder
    #dependencies=['Get_pia_xy_1','Get_pia_xy_2','Get_pia_xy_3','Get_pia_xy_4']
    out_format=['Get',''] #FIXME this needs to take step names too?
    def bind(self,**kwargs):
        return kwargs['dep_vals']

class _Bind_espXY(Bind):
    """ poop """
    MappedClass=Binder
    dependencies=['Get_espX','Get_espY']
    out_format=['Get_espX','Get_espY']
    def validate(self):
        #TODO FIXME need some way to make sure that all the units match or convert the units...
            #which requires somehow passing mcKwargs along >_< damn it I KNEW it was going to be
            #weird breaking up the getters from everything that needed to check units :/
        #TODO well since we know that units are central to this whole thing, maybe we can just
            #integrate them in at a very basic level? yeah, that might work!
            #OFF TO MODIFY Getter to handle this better than that mess of MDS

        #FIXME ARGH@!!!! everything is totally backwards ;_; if only the previous step could just call the next two steps and be done with it >_<
        #TODO maybe a decorator that will log all the information to the database?!?! for a specific function!?
        #or better yet just code that says "this function is actually a getter! or a setter! or xyz"
            #and then we can just write normal code inside a step instead of having to write a new dataio every bloody time we want to change a single variable...
            #eeeehhhh maybe? think about it for the future
        pass


class Set_espXY(Set):
    """ A dynamic setter do(pos=(x,y)) is the proper calling convention"""
    #TODO this needs to be followed/acompanied by a Write of the set values?
        #or is there some way we can store this in the step record????
    #weird case where the value that we set is going to vary instead of being defined by the class :/
        #lot of those actually, TODO a way to effectively record that in the step record
        #could definately reduce the number of entries...
    #XXX answer: write ctrl_kwargs to the step record! do_kwargs???
    #XXX XXX actually NOPE! not an issue, because we are going to GET the espXY again when we need it!
        #so all we really need to know is that it was set and the changes will be picked up
        #and we *should* have a record anyway, maybe for setting channels or something we need that
    MappedClass=Setter
    ctrl_name='espControl'
    function_name='setPos'
    hardware='esp300'
    #TODO kwargs for do(**kwargs) should be pos=(x,y)


###
#MCC
mds_bool_kwargs={'prefix':'','unit':'bool'}

#TODO this seems like it migth be a good place to implemnt units/conversions?
#FIXME if we are just using function_name and ctrl_name to get all of this, we *could* just store it in the database since these classes are really just supposed to be for doccumentation and THESE shouldnt need to change
class _Get_mcc(Get):
    """ I AM ONE WITH THE VOID """
    MappedClass=MetaDataSource
    ctrl_name='mccControl'
    dependencies=['Set_mccChannel']
    hardware=''


class Get_mccHoldEnable(_Get_mcc): #FIXME how do we want to deal with channels??!?! At the step level.
    """ Get whether holding is enabled for the active channel"""
                                        #damn it needless complications again >_<
    mcKwargs=mds_bool_kwargs
    function_name='GetHoldingEnable'
    hardware=''


class Get_mccHolding(_Get_mcc): #FIXME ARGH HATE MCC
    """ Get the holding voltage/amerage for the active channel"""
    mcKwargs={'prefix':'','unit':'V','mantissa':3} #FIXME DAMN IT MAN this depends on the mode :(
    function_name='GetHolding'
    hardware=''


class Get_mccPSGain(_Get_mcc):
    """ Get the gain for the primary signal"""
    mcKwargs={'prefix':'','unit':'num'}
    function_name='GetPrimarySignalGain'
    hardware=''


class Get_PSLPF(_Get_mcc):
    """Low pass filter for primary signal"""
    mcKwargs={'prefix':'','unit':'Hz'}
    function_name='GetPrimarySignalLPF'
    hardware=''

class Get_mccPipetteOffset(_Get_mcc):
    """ Get Pipette offset for active channel"""
    mcKwargs={'prefix':'','unit':'V','mantissa':5}
    function_name='GetPipetteOffset'
    hardware=''

#TODO add more later


#FIXME NOTICE: setters are only useful in combination, don't just blindly reproduce stuff !
class _Set_mcc(Set):
    """ YOU SEE NOTHING """
    MappedClass=Setter
    ctrl_name='mccControl'
    #modes: V=0, I=1, IeZ=2


class Set_mccAll_IeZ(_Set_mcc): #FIXME not actually all
    """ Sets num=n headstages to current clamp with no injected current"""
    num=2 #number of headstages, making this easy to track do we need a way to persist arbitrary thigns?
    def set(self,**kwargs):
        num=kwargs.get('num',self.num)
        for i in range(num):
            self.ctrl.selectMC(i)
            self.ctrl.SetMode(2)


class Set_mccAllVnoHold(_Set_mcc):
    """ Sets num=n headstages to voltage clamp at 0mV"""
    num=2
    def set(self,**kwargs):
        num=kwargs.get('num',self.num)
        for i in range(num):
            self.ctrl.selectMC(i)
            self.ctrl.SetMode(0)
            self.ctrl.SetHoldingEnable(0)


###
#Checks

class Check_700B(Check): #TODO
    """ make sure not in demo and ??? """
    MappedClass=Checker
    def check(self,**kwargs):
        serial=self.ctrlDict['mccControl']._pszSerialNumber
        printD(serial)
        if serial != b'DEMO':
            return True


class Check_headstages(Check):
    """ make sure hs matches channels """
    MappedClass=Checker
    @staticmethod
    def check_function(**kwargs):
        pass
        return True
        #stimulate from a, check channel, make sure it matches
        #stimulate from b, check channel, make sure it matches

###
#Writers

class Get_clx_savedir_url(Get):
    """ get the path where abf file are saved """
    MappedClass=Getter
    def get(self,**kwargs):
        return '/home/tom/Dropbox/mlab/' #TESTING
        return 'D:/tom_data/clampex/' #this is the path in question

class Get_newest_abf(Get): #TODO check that name doesn match the previous?
    """ get the newest abf """
    MappedClass=Getter
    def _get(self,**kwargs): #FIXME doesnt work!
        path=kwargs['Get_clx_savedir_url']
        path=path.rstrip('/')+'/'
        filepath=max(glob.iglob(path+'*.abf'), key=os.path.getctime)
        file=filepath[len(path):]
        return file
        
    def get(self,**kwargs):
        files=os.listdir(kwargs['Get_clx_savedir_url'])
        abf_files=[file for file in files if file[-3:]=='abf']
        abf_files.sort() #FIXME make sure the filenames order correctly
        out=abf_files[-1] #get the last/newest file
        return out

class Write_clx_datafile(Write):
    """ recored the datafile in the database """
    MappedClass=Writer
    MappedWriter=DataFile
    writer_kwargs={} #TODO check the path

class Write_datafile_metadata(Write):
    """ write data to datafile """
    MappedClass=Writer
    MappedWriter=DataFile
    writer_kwargs={}

###
#Analysis

class Comp_spline_from_points(Analysis): #TODO
    """ compute spline from points """
    MappedClass=Analyzer
    @staticmethod
    def analysis_function(**kwargs):
        printD('dep_value',kwargs['dep_vals'])

class Comp_esp300_calib(Analysis): #TODO
    """ calc calibration data from expected distances """
    MappedClass=Analyzer
    @staticmethod
    def analysis_function(**kwargs):
        printD('dep_valse',kwargs['dep_vals'])

class Comp_stimulus_positions(Analysis): #TODO
    """ Given a spline and a starting point get positions """
    MappedClass=Analyzer
    @staticmethod
    def analysis_function(**kwargs):
        printD('dep_valse',kwargs['dep_vals'])

class Comp_mean_position(Analysis): #TODO
    """ compute the mean positition of a set of points """
    MappedClass=Analyzer
    @staticmethod
    def analysis_function(**kwargs):
        printD('dep_valse',kwargs['dep_vals'])
        return mean(kwargs['dep_vals']) #FIXME need a shape parameter??


"""
#can also just write custom def set(self) for some of the Setters don't have to follow the template
class Set_mccHolding_Off(_Set_mcc): #FIXME argh, don't tell me that I can't set the holding values without actually switching to that mode >_< god damn it fortunately everything is so fast that it should be to just switch and set
    function_name='SetHoldingEnable'
    func_kwargs={'b':0} #B is for boolean

class Set_mccHolding_On(_Set_mcc): #alternate way to handle this that lacks doccumentation :/
    def set(self):
        self.ctrl.SetHoldingEnable(1)

class Set_mccMode_V(_Set_mcc): #should steps reflect implementation details? such as HOW you get to a certain state for the mcc? URG
    def set(self):
        self.ctrl.SetMode(0)
"""

