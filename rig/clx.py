from ctypes import *
import os
import inspect as ins
from debug import TDB
from time import sleep
#import rpdb2
#rpdb2.settrace()

tdb=TDB()
printD=tdb.printD
printFuncDict=tdb.printFuncDict
tdbOff=tdb.tdbOff

#developed for api version 1.0.0.5

#ptypes
c_int_p=POINTER(c_int)
c_uint_p=POINTER(c_uint)
c_bool_p=POINTER(c_bool)
c_double_p=POINTER(c_double)

#utility function for type casting and returning the value at a pointer
def val(ptr, ptype):
    return cast(ptr,ptype)[0]

errdict={\
    # General error codes.
    4000:'CLXMSG_ERROR_NOERROR',\
    4001:'CLXMSG_ERROR_OUTOFMEMORY',\
    4002:'CLXMSG_ERROR_CLAMPEXNOTOPEN',\
    4003:'CLXMSG_ERROR_INVALIDDLLHANDLE',\
    4004:'CLXMSG_ERROR_MSGTIMEOUT',\
    4005:'CLXMSG_ERROR_PROTOCOLPATHNOTSET',\
    4006:'CLXMSG_ERROR_PROTOCOLCANNOTLOAD',\
    4007:'CLXMSG_ERROR_PROTOCOLNOTVALID',\
    4008:'CLXMSG_ERROR_PROTOCOLCANNOTLOADWHENRECORDING',\
    4009:'CLXMSG_ERROR_DIALOGOPEN',\
    4010:'CLXMSG_ERROR_STOPIGNOREDWHENIDLE',\
    4011:'CLXMSG_ERROR_UNKNOWNACQMODE',\
    4012:'CLXMSG_ERROR_CACHEISEMPTY',\
    4013:'CLXMSG_ERROR_ZEROPOINTSSPECIFIED',\
    4014:'CLXMSG_ERROR_INVALIDPARAMETER',\
    # Membrane Test error codes.
    5000:'CLXMSG_ERROR_MEMB_RESPONSECLIPPED',\
    5001:'CLXMSG_ERROR_MEMB_RESPONSERECTIFIED',\
    5002:'CLXMSG_ERROR_MEMB_SLOWRISETIME',\
    5003:'CLXMSG_ERROR_MEMB_NOPEAKFOUND',\
    5004:'CLXMSG_ERROR_MEMB_BADRESPONSE',\
    5005:'CLXMSG_ERROR_MEMB_TAUTOOFAST',\
    5006:'CLXMSG_ERROR_MEMB_TAUTOOSLOW',\
    5007:'CLXMSG_ERROR_MEMB_TOOFEWPOINTS',\
    5008:'CLXMSG_ERROR_MEMB_NOPULSESPECIFIED',\
    5009:'CLXMSG_ERROR_MEMB_HOLDINGOUTOFRANGE',\
    5010:'CLXMSG_ERROR_MEMB_PULSEOUTOFRANGE',\
    5011:'CLXMSG_ERROR_MEMB_CANNOTSTARTMORETHANONE',\
    5012:'CLXMSG_ERROR_MEMB_ALREADYSTARTED',\
    5013:'CLXMSG_ERROR_MEMB_ALREADYCLOSED',\
    5014:'CLXMSG_ERROR_MEMB_INVALIDOUTPUTDAC',\
    }

def errPrint(pnErr):
    """returns false if there was an error and prints it"""
    errval=val(pnErr,c_int_p)
    if errval==4000:
        return 1
    else:
        raise(errdict[errval])
        #printD(errdict[errval],context=5)
        #return 0

#main class
class clxControl: #clxmsg
    def __init__(self):
        #load the clx msg dll
        clxDllPath='C:/Axon/pCLAMP9.2/3rd Party Support/AxClampexMsg/' #change this to match install loc
        #or put it in the same folder with your code! NOPE doesnt work!
        try:
            olddir=os.getcwd()
            os.chdir(clxDllPath)
            self.aDLL=windll.AxClampexMsg #magic!
            os.chdir(olddir)
        except:
            print('Clampex DLL not found! Check your install path!')
            return None

        #_pointers: these will all be reused over and over again because none of these functions should ever be called from more than one thread
        self._pnError=byref(c_int(4000))

        #create the messenger
        #self.hClxmsg=self.CreateObject() #FIXME

        #wrap all the methods from the API to try to prevent the nasty crashing
        class wrap:
            def __init__(self,pre,call,post):
                self.start=pre
                self.do=call
                self.stop=post
            def go(self,*args):
                self.start()
                out=self.do(*args)
                self.stop()
                return out
        mems=ins.getmembers(self)
        excluded=['cleanup', 'DestroyObject', 'CreateObject', '__init__']
        funcs=[func for func in mems if ins.ismethod(func[1]) and func[0] not in excluded]
        #printFuncDict(funcs)
        for tup in funcs:
            setattr(self,tup[0],wrap(self.CreateObject,tup[1],self.DestroyObject).go)

        #if everything goes well create the rest of the pointers
        self._pnPointer=byref(c_int(0))
        self._puPointer=byref(c_uint(0))
        self._pbPointer=byref(c_bool(0))
        self._pdPointer=byref(c_double(0))

    def POST(self):
        print('CLX POST',self.GetStatus())
        return self.GetStatus()

    def cleanup(self):
        """called in __exit__ to make sure we have no memory leeks"""
        try:
            self.DestroyObject()
            print('hClxmsg successfully removed, no memory leaks here!')
        except:
            print('since all of this is now wrapped, hClxmsg should NEVER exist at cleanup')



    #==============================================================================================
    # DLL creation/destruction functions
    #==============================================================================================

    # Check on the version number of the API interface.
    #def CheckAPIVersion(self):
        #self.aDLL.CLXMSG_CheckAPIVersion(LPCSTR pszQueryVersion)

    # Create the clampex message handler object.
    def CreateObject(self):
        self.hClxmsg=self.aDLL.CLXMSG_CreateObject(self._pnError)
        return self.hClxmsg

    # Destroy the clampex message handler object.
    def DestroyObject(self):
        return self.aDLL.CLXMSG_DestroyObject(self.hClxmsg) #returns none...

    #==============================================================================================
    # General functions
    #==============================================================================================

    # Set timeout in milliseconds for messages to Clampex.
    def SetTimeOut(self, u):
        uTimeOutMS=c_uint(u)
        self.aDLL.CLXMSG_SetTimeOut(self.hClxmsg, uTimeOutMS, self._pnError)
        return errPrint(self._pnError)

    #==============================================================================================
    # Acquisition functions
    #==============================================================================================

    # Request Clampex to load protocol.
    def LoadProtocol(self,filePath):
        #example path sting, will test others "C:\\Axon\\Params\\es sine.pro"
        #probably should be a byte string so b'' but test, actually ctypes is good
        _pszFilename=c_char_p(filePath)
        self.aDLL.CLXMSG_LoadProtocol(self.hClxmsg, _pszFilename, self._pnError)
        return errPrint(self._pnError)

    # Request the Clampex status.
    def GetStatus(self):
        statusDict={\
        0:'CLAMPEX IS NOT RUNNING',\
        100:'CLXMSG_ACQ_STATUS_IDLE',\
        101:'CLXMSG_ACQ_STATUS_DIALOGOPEN',\
        102:'CLXMSG_ACQ_STATUS_TRIGWAIT',\
        103:'CLXMSG_ACQ_STATUS_VIEWING',\
        104:'CLXMSG_ACQ_STATUS_RECORDING',\
        105:'CLXMSG_ACQ_STATUS_PAUSEVIEW',\
        106:'CLXMSG_ACQ_STATUS_PAUSED',\
        }
        self.aDLL.CLXMSG_GetStatus(self.hClxmsg, self._puPointer, self._pnError)
        return statusDict[val(self._puPointer, c_uint_p)]

    # Initiate Clampex REPEAT.
    def SetRepeat(self, b):
        bRepeat=c_bool(b)
        self.aDLL.CLXMSG_SetRepeat(self.hClxmsg, bRepeat, self._pnError)
        return errPrint(self._pnError)

    # Initiate Clampex VIEW, RECORD or RERECORD.
    def StartAcquisition(self, u):
        uMode=c_uint(u)
        self.aDLL.CLXMSG_StartAcquisition(self.hClxmsg, uMode, self._pnError)
        return errPrint(self._pnError)

    # Initiate Clampex STOP.
    def StopAcquisition(self):
        self.aDLL.CLXMSG_StopAcquisition(self.hClxmsg, self._pnError)
        return errPrint(self._pnError)

    #==============================================================================================
    # Telegraph functions
    #==============================================================================================

    # Gets the specified telegraph value
    def GetTelegraphValue(self, chan, it):
        """DO NOT NEED THIS HAVE MCC"""
        uChan=c_uint(chan)
        uTelItem=c_uint(it)
        self.aDLL.CLXMSG_GetTelegraphValue(self.hClxmsg, uChan, uTelItem, self._pfPointer, self._pnError)
        return val(self._pfPointer, c_f)

    # Gets the specified telegraph instrument name
    def GetTelegraphInstrument(self, chan, size):
        """DO NOT NEED THIS HAVE MCC"""
        uChan=c_uint(chan)
        uSize=c_uint(size)
        _pszInstrument=byref(c_char_p(b''))
        self.aDLL.CLXMSG_GetTelegraphInstrument(self.hClxmsg, uChan, _pszInstrument, uSize, self._pnError)
        return val(_pszInstrument, c_char_p)

    #==============================================================================================
    # Membrane Test functions
    #==============================================================================================

    # Start the Clampex membrane test.
    def StartMembTest(self, u):
        uOut=c_uint(u) #this one will require the constants...
        self.aDLL.CLXMSG_StartMembTest(self.hClxmsg, uOut, self._pnError)
        return errPrint(self._pnError)

    # Close the Clampex membrane test.
    def CloseMembTest(self, u):
        uOut=c_uint(u)
        self.aDLL.CLXMSG_CloseMembTest(self.hClxmsg, uOut, self._pnError)
        return errPrint(self._pnError)

    # Set the Clampex membrane test holding.
    def SetMembTestHolding(self):
        self.aDLL.CLXMSG_SetMembTestHolding(self.hClxmsg, dHolding, self._pnError)
        return errPrint(self._pnError)

    # Get the Clampex membrane test holding.
    def GetMembTestHolding(self):
        self.aDLL.CLXMSG_GetMembTestHolding(self.hClxmsg, self._pdPointer, self._pnError)
        return val(self._pdPointer, c_d)

    # Set the Clampex membrane test pulse height.
    def SetMembTestPulseHeight(self):
        self.aDLL.CLXMSG_SetMembTestPulseHeight(self.hClxmsg, dPulseHeight, self._pnError)
        return errPrint(self._pnError)

    # Get the Clampex membrane test pulse height.
    def GetMembTestPulseHeight(self):
        self.aDLL.CLXMSG_GetMembTestPulseHeight(self.hClxmsg, self._pdPointer, self._pnError)
        return val(self._pdPointer, c_d)

    # Flush the membrane test cache.
    def FlushMembTestCache(self):
        self.aDLL.CLXMSG_FlushMembTestCache(self.hClxmsg, self._pnError)
        return errPrint(self._pnError)

    # Get the current size of the membrane test cache.
    def GetMembTestCacheSize(self):
        self.aDLL.CLXMSG_GetMembTestCacheSize(self.hClxmsg, self._puPointer, self._pnError)
        return val(self._puPointer, c_u)

    # Set the maximum membrane test cache size.
    def SetMembTestCacheMaxSize(self, u):
        uMaxSize=c_uint(u)
        self.aDLL.CLXMSG_SetMembTestCacheMaxSize(self.hClxmsg, uMaxSize, self._pnError)
        return errPrint(self._pnError)

    # Get the average membrane test cache data for the number of entries specified by *puCount
    def GetMembTestCacheData(self):
        _pdAvRt=byref(c_double(0))
        _pdAvCm=byref(c_double(0))
        _pdAvRm=byref(c_double(0))
        _pdAvRa=byref(c_double(0))
        _pdAvTau=byref(c_double(0))
        _pdAvHold=byref(c_double(0))
        _puCount=self._puPointer
        self.aDLL.CLXMSG_GetMembTestCacheData(self.hClxmsg, _pdAvRt, _pdAvCm, _pdAvRm, _pdAvRa, _pdAvTau, _pdAvHold, _puCount, self._pnError)
        return val(_pdAvRt,c_double_p), val(_pdAvCm,c_double_p), val(_pdAvRm,c_double_p), val(_pdAvRa,c_double_p), val(_pdAvTau,c_double_p), val(_pdAvHold,c_double_p), val(_puCount,c_uint_p)

    # Scales the membrane test Y axis
    def ScaleMembTestYAxis(self, u):
        uScale=c_uint(u)
        self.aDLL.CLXMSG_ScaleMembTestYAxis(self.hClxmsg, uScale, self._pnError)
        return errPrint(self._pnError)
    # Set the membrane test update rate in Hertz
    def SetMembTestRate(self):
        self.aDLL.CLXMSG_SetMembTestRate(self.hClxmsg, dRate, self._pnError)
        return errPrint(self._pnError)

    # Get the membrane test update rate in Hertz
    def GetMembTestRate(self):
        self.aDLL.CLXMSG_GetMembTestRate(self.hClxmsg, self._pdPointer, self._pnError)
        return val(self._pdPointer, c_d)

    # Set the membrane test averaging state and number of edges per average.
    def SetMembTestAveraging(self, u):
        uNumEdges=c_uint(u)
        bAveraging=c_bool(b)
        self.aDLL.CLXMSG_SetMembTestAveraging(self.hClxmsg, bAveraging, uNumEdges, self._pnError)
        return errPrint(self._pnError)

    # Get the membrane test averaging state and number of edges per average.
    def GetMembTestAveraging(self):
        self.aDLL.CLXMSG_GetMembTestAveraging(self.hClxmsg, self._pbPointer, self._pnError)
        return val(self._pbPointer, c_b)

    #==============================================================================================
    # Seal Test functions
    #==============================================================================================
    def StartSealTest(self, u):
        uOut=c_uint(u) #this one will require the constants...
        self.aDLL.CLXMSG_StartSealTest(self.hClxmsg, uOut, self._pnError)
        return errPrint(self._pnError)

    # Get the current size of the seal test cache.
    def GetSealTestCacheSize(self):
        self.aDLL.CLXMSG_GetSealTestCacheSize(self.hClxmsg, self._puPointer, self._pnError)
        return val(self._puPointer, c_u)

    # Set the maximum seal test cache size.
    def SetSealTestCacheMaxSize(self, u):
        uMaxSize=c_uint(u)
        self.aDLL.CLXMSG_SetSealTestCacheMaxSize(self.hClxmsg, uMaxSize, self._pnError)
        return errPrint(self._pnError)

    # Flush the seal test cache.
    def FlushSealTestCache(self):
        self.aDLL.CLXMSG_FlushSealTestCache(self.hClxmsg, self._pnError)
        return errPrint(self._pnError)

    # Get the average seal test cache data for the number of entries specified by *puCount
    def GetSealTestCacheData(self):
        self.aDLL.CLXMSG_GetSealTestCacheData(self.hClxmsg, self._pdPointer, self._puPointer, self._pnError)
        return val(self._pdPointer, c_d), val(self._uPointer, c_u)

    # Set the Clampex seal test holding.
    def SetSealTestHolding(self):
        self.aDLL.CLXMSG_SetSealTestHolding(self.hClxmsg, dHolding, self._pnError)
        return errPrint(self._pnError)
    # Set the Clampex seal test pulse height.
    def SetSealTestPulseHeight(self):
        self.aDLL.CLXMSG_SetSealTestPulseHeight(self.hClxmsg, dPulseHeight, self._pnError)
        return errPrint(self._pnError)

    #==============================================================================================
    # Error functions
    #==============================================================================================

    # Errors etc.
    #def BuildErrorText(self):
        #self.aDLL.CLXMSG_BuildErrorText(self.hClxmsg, int nErrorNum, LPSTR sTxtBuf, UINT uMaxLen)

#==============================================================================================
# Error codes
#==============================================================================================

# General error codes.
CLXMSG_ERROR_NOERROR                         = 4000
CLXMSG_ERROR_OUTOFMEMORY                     = 4001
CLXMSG_ERROR_CLAMPEXNOTOPEN                  = 4002
CLXMSG_ERROR_INVALIDDLLHANDLE                = 4003
CLXMSG_ERROR_MSGTIMEOUT                      = 4004
CLXMSG_ERROR_PROTOCOLPATHNOTSET              = 4005
CLXMSG_ERROR_PROTOCOLCANNOTLOAD              = 4006
CLXMSG_ERROR_PROTOCOLNOTVALID                = 4007
CLXMSG_ERROR_PROTOCOLCANNOTLOADWHENRECORDING = 4008
CLXMSG_ERROR_DIALOGOPEN                      = 4009
CLXMSG_ERROR_STOPIGNOREDWHENIDLE             = 4010
CLXMSG_ERROR_UNKNOWNACQMODE                  = 4011
CLXMSG_ERROR_CACHEISEMPTY                    = 4012
CLXMSG_ERROR_ZEROPOINTSSPECIFIED             = 4013
CLXMSG_ERROR_INVALIDPARAMETER                = 4014

# Membrane Test error codes.
CLXMSG_ERROR_MEMB_RESPONSECLIPPED            = 5000
CLXMSG_ERROR_MEMB_RESPONSERECTIFIED          = 5001
CLXMSG_ERROR_MEMB_SLOWRISETIME               = 5002
CLXMSG_ERROR_MEMB_NOPEAKFOUND                = 5003
CLXMSG_ERROR_MEMB_BADRESPONSE                = 5004
CLXMSG_ERROR_MEMB_TAUTOOFAST                 = 5005
CLXMSG_ERROR_MEMB_TAUTOOSLOW                 = 5006
CLXMSG_ERROR_MEMB_TOOFEWPOINTS               = 5007
CLXMSG_ERROR_MEMB_NOPULSESPECIFIED           = 5008
CLXMSG_ERROR_MEMB_HOLDINGOUTOFRANGE          = 5009
CLXMSG_ERROR_MEMB_PULSEOUTOFRANGE            = 5010
CLXMSG_ERROR_MEMB_CANNOTSTARTMORETHANONE     = 5011
CLXMSG_ERROR_MEMB_ALREADYSTARTED             = 5012
CLXMSG_ERROR_MEMB_ALREADYCLOSED              = 5013
CLXMSG_ERROR_MEMB_INVALIDOUTPUTDAC           = 5014

#==============================================================================================
# Function parameters
#==============================================================================================

# Parameters for CLXMSG_GetStatus(HCLXMSG hClxmsg, UINT *puStatus, int *pnError)
# *puStatus filled out as:
CLXMSG_ACQ_STATUS_IDLE             = 100 # acquisition is not in progress.
CLXMSG_ACQ_STATUS_DIALOGOPEN       = 101 # dialog is open in Clampex.
CLXMSG_ACQ_STATUS_TRIGWAIT         = 102 # acquisition is pending waiting for a trigger.
CLXMSG_ACQ_STATUS_VIEWING          = 103 # view-only acquisition is in progress.
CLXMSG_ACQ_STATUS_RECORDING        = 104 # acquisition is currently recording to disk.
CLXMSG_ACQ_STATUS_PAUSEVIEW        = 105 # recording has been paused, but display is left running.
CLXMSG_ACQ_STATUS_PAUSED           = 106 # recording has been paused - display stopped.
CLXMSG_ACQ_STATUS_DISABLED         = 107 # acquisition has been disabled because of bad parameters.

# Parameters for CLXMSG_StartAcquisition(HCLXMSG hClxmsg, UINT uMode, int *pnError)
# uMode filled in as:
CLXMSG_ACQ_START_VIEW              = 108 # acquire data with current protocol but do not save to file.
CLXMSG_ACQ_START_RECORD            = 109 # acquire data with current protocol and save to file. 
CLXMSG_ACQ_START_RERECORD          = 110 # acquire data with current protocol and save over last file.  
CLXMSG_ACQ_START_RERECORD_PROMPT   = 111 # acquire data with current protocol and save over last file but prompt before overwriting.

# Parameters for CLXMSG_GetTelegraphValue(HCLXMSG hClxmsg, UINT uChan, UINT uTelItem, float *pfTelValue, int *pnError)
# uTelItem filled in as:
CLXMSG_TEL_CM                      = 112 # request the telegraphed whole cell capacitance.
CLXMSG_TEL_GAIN                    = 113 # request the telegraphed gain.
CLXMSG_TEL_MODE                    = 114 # request the telegraphed mode.
CLXMSG_TEL_FREQUENCY               = 115 # request the telegraphed low pass filter cutoff frequency.
CLXMSG_TEL_CMDSCALEFACTOR          = 116 # request the telegraphed command scale factor.
# *pfTelValue filled out as 
CLXMSG_TEL_MODE_VCLAMP             = 0   # mode is voltage clamp.
CLXMSG_TEL_MODE_ICLAMP             = 1   # mode is current clamp.
CLXMSG_TEL_MODE_ICLAMPZERO         = 2   # mode I=0.

# Parameters for CLXMSG_StartMembTest(HCLXMSG hClxmsg, UINT uOut, int *pnError)
# uOut filled in as:
CLXMSG_MBT_OUT0                    = 120 # start/close Membrane Test OUT0.
CLXMSG_MBT_OUT1                    = 121 # start/close Membrane Test OUT1.

# Parameters for CLXMSG_ScaleMembTestYAxis(HCLXMSG hClxmsg, UINT uScale, int *pnError)
# uScale filled in as:
CLXMSG_MBT_AUTOSCALE               = 130 # autoscale the Membrane Test Y axis.
CLXMSG_MBT_FULLSCALE               = 131 # fullscale the Membrane Test Y axis.

# size of telegraph instrument name string
CLXMSG_TEL_INSTRU_NAMESIZE         = 260

def main():
    #import pdb
    ctrl=clxmsg()
    #pdb.set_trace()
    printD(ctrl.GetStatus())
    printD(ctrl.StartMembTest(120))
    sleep(5)
    printD(ctrl.CloseMembTest(120))
    sleep(.5)
    printD(ctrl.StartMembTest(121))
    sleep(5)
    printD(ctrl.CloseMembTest(121))

    #ctrl.cleanup()

if __name__=='__main__':
    main()
