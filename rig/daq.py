""" A command line program to control the pattern the LED plays when triggered.
    This MUST be running in order to trigger the LED.
    If no wave is specified the type will be a square wave.
    Hit escape or q twice to exit (or that special key once).
Usage:
    daq.py [--on=<ms> --off=<ms> --rep=<int> --minV=<V> --maxV=<V>]
    daq.py [wave (--square | --ramp | --cos) --on=<ms> --off=<ms> --rep=<int> --minV=<V> --maxV=<V>]
    daq.py -h | --help
Options:
    -h, --help               Print this. [default:1 ]
    -o, --on=<ms>            on ms  [default: 1]
    -f, --off=<ms>           off ms [default: 0]
    -r, --rep=<int>          reps   [default: 1]
    -u, --minV=<V>           minV   [default: 0]
    -l, --maxV=<V>           maxV   [default: 4.2]
    -s, --square
    -a, --ramp
    -c, --cos
"""
    #dqa.py <on>
    #daq.py <off>
    #daq.py <rep>
    #daq.py <wave>
    #daq.py <minV>
    #daq.py <maxV>
    #-on=<ms>            number of ms on  [default:1]
    #-off=<ms>           number of ms off [default:0]
    #-rep=<reps>         number of reps   [defalut:1]
    #-wave=<name>        desired waveform [default:'square']
    #-minV=<V>           Min voltage to send to the LED. NOTE: results in max intensity [default:0]
    #-maxV=<V>           Max voltage to send to the LED. NOTE: results in min intensity [default:4.2]
#(s | square) | (r | ramp) | (c | cos)
from ctypes import *
import numpy as np
import threading
#import time
#import pdb
#from tomsDebug import *
from rigcontrol import rigIOMan
from rig.key import keyListener
from queue import Queue
from docopt import docopt

def parse_args(args):
    print(args)
    if args['--square']:
        waveName='LEDsquarePulse'
    elif args['--ramp']:
        waveName='LEDlinRamp'
    elif args['--cos']:
        waveName='LEDcos'
    else:
        waveName='LEDsquarePulse' #default to square pulse

    on_ms=float(args['--on'][0])
    off_ms=float(args['--off'][0])
    reps=int(args['--rep'][0])
    #waveForm=args['--wave'][0]
    minV=float(args['--minV'][0])
    maxV=float(args['--maxV'][0])
    return minV,maxV,on_ms,off_ms,waveName,reps

ni=windll.nicaiu

int32=c_long
uInt32=c_ulong
uInt64=c_longlong
float64=c_double

TaskHandle=uInt32 #define the TaskHandle type; this is typedef void* irl?
signalID=int32 #this is used to keep track of signals for call backs

#signals used by the daq
DAQmx_Val_FiniteSamps=signalID(10178)
DAQmx_Val_Rising=signalID(10280)
DAQmx_Val_Volts=signalID(10348)
DAQmx_Val_GroupByChannel=c_bool(0)
DAQmx_Val_DoNotAllowRegen=signalID(10158) # Not Allow Regeneration
DAQmx_Val_OnBrdMemEmpty=signalID(10235) # Onboard Memory Empty

#unused
DAQmx_Val_ChangeDetectionEvent=signalID(12511) # Change Detection Event
DAQmx_Val_ChanPerLine=int32(0)   # One Channel For Each Line
DAQmx_Val_ChanForAllLines=int32(1)   # One Channel For All Lines
DAQmx_Val_Sine=signalID(14751) # Sine
DAQmx_Val_ContSamps=signalID(10123)
DAQmx_Val_AllowRegen=signalID(10097) # Allow Regeneration
DAQmx_Val_OnBrdMemHalfFullOrLess=signalID(10239) # Onboard Memory Half Full or Less
DAQmx_Val_OnBrdMemNotFull=signalID(10242) # Onboard Memory Less than Full
DAQmx_Val_WaitInfinitely=float64(-1.0)

def CHK(err):
    """a simple error checking routine"""
    if err < 0:
        buf_size = 100
        buf = create_string_buffer(b'\000' * buf_size)
        ni.DAQmxGetErrorString(err,byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
    if err > 0:
        buf_size = 100
        buf = create_string_buffer(b'\000' * buf_size)
        ni.DAQmxGetErrorString(err,byref(buf),buf_size)
        raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))
#
#probably best to just create a new task on demand? or have them all up and ready to go? I got the ram...
class trigWaveTask:
    """a class for holding waveforms to be triggered off digital input and played via AO"""
    #could make a waveform dictionary... AWE YEAH DICTS
    def __init__(self,waveform,sampRate=10000.0,triggerTerminal=b'PFI0',ao=b'Dev1/ao0'):
        #class handling
        self.is_active=0

        #convert the waveform so it can be written to the nidaq
        self.numPoints=len(waveform)
        self.dur=self.numPoints/sampRate #max duration of an active run
        float64Array=float64*self.numPoints
        self.wave=float64Array(*tuple(waveform))

        #initilize our Task and setup up the AO channel and the DI trigger
        self.task=TaskHandle(0)
        CHK(ni.DAQmxCreateTask(b'',byref(self.task)))
        minV,maxV=-5,5 #set the voltage limts
        CHK(ni.DAQmxCreateAOVoltageChan(self.task, ao, b'', float64(minV), float64(maxV), DAQmx_Val_Volts, None))

        #CHK(ni.DAQmxSetWriteRegenMode(task_test,DAQmx_Val_DoNotAllowRegen))
        #CHK(ni.DAQmxSetAODataXferReqCond(task_test,b'Dev1/ao0',DAQmx_Val_OnBrdMemEmpty))

        CHK(ni.DAQmxCfgSampClkTiming(self.task,b'',float64(sampRate),DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,uInt64(self.numPoints)))
        CHK(ni.DAQmxCfgDigEdgeStartTrig(self.task,triggerTerminal,DAQmx_Val_Rising))

        #write the data to the buffer so that it's ready to go
    def start(self):
        #set the write here because otherwise it will block up the buffer for other tasks
        CHK(ni.DAQmxWriteAnalogF64(self.task,int32(self.numPoints),c_bool(0),float64(-1),DAQmx_Val_GroupByChannel,self.wave,None,None))
        self.is_active=1
        running=0
        while self.is_active:
            if not running:
                CHK(ni.DAQmxStartTask(self.task))
            running=ni.DAQmxWaitUntilTaskDone(self.task,float64(.1)) #1 sec timeout so we can check is_acitve, adjust accordingly
            if not running: #this has to be here or else the task just sits there and never resets
                CHK(ni.DAQmxStopTask(self.task))
        ni.DAQmxStopTask(self.task) #when we break out of the loop the task could still be running so stop it
    def stop(self):
        if self.is_active:
            self.is_active=0
            ni.DAQmxWaitUntilTaskDone(self.task,float64(self.dur+.001)) #make sure a running stimulation finishes, no trucating!
        else:
            ni.DAQmxStopTask(self.task) #remove the CHK if you know its going to error
    def cleanup(self):
        self.stop()
        CHK(ni.DAQmxClearTask(self.task))


def makeWave(minV,maxV,milisecs,waveFunc): #import this for easymode? along with the waveFuncs probably...
    #FIXME make it so the voltage limits are passed on to the AO channel settings throw an error?
    if milisecs <= 10:
        sampRate=100000.0 #100kHz to prevent aliasing
    else:
        sampRate= 10000.0 #10kHz is fine for most stuff
    samples=(sampRate*milisecs)/1000
    wave=waveFunc(minV,maxV,samples)
    Task=trigWaveTask(wave,sampRate)
    Thrd=threading.Thread(target=Task.start)
    return Task,Thrd

def makeTrain(minV,maxV,on_ms,off_ms,on_wf,off_wf,repeats):
    #TODO ability to control the intensity of each pulse?
    if min(on_ms,off_ms) <= 10:
        sampRate=100000.0 #100kHz to prevent aliasing
    else:
        sampRate= 10000.0 #10kHz is fine for most stuff
    on_samples=(sampRate*on_ms)/1000
    off_samples=(sampRate*off_ms)/1000
    on_wave=on_wf(minV,maxV,on_samples)
    off_wave=off_wf(minV,maxV,off_samples) #this works correctly with 0
    single_period=np.concatenate([on_wave,off_wave])
    all_periods=np.array([])
    for i in range(repeats):
        all_periods=np.concatenate([all_periods,single_period])
    assert len(all_periods)==len(single_period)*repeats, 'lengths dont match'
    Task=trigWaveTask(all_periods,sampRate)
    Thrd=threading.Thread(target=Task.start)
    return Task,Thrd



###
#Define waveforms

def LEDlinRamp(minV,maxV,samples):
    wave=np.linspace(maxV,minV,samples)
    wave[-1]=maxV #restore to initial value at end
    return wave

def LEDoff(minV,maxV,samples):
    wave=np.ones(samples)*maxV
    return wave

def LEDsquarePulse(minV,maxV,samples):
    wave=np.ones(samples)*minV
    wave[-1]=maxV #restore to initial value at end
    return wave

def LEDcos(minV,maxV,samples): #FIXME need a way to deal with periodic stuff in the future...
    base=np.linspace(0,np.pi*2,samples)
    shift=(maxV-minV)/2
    wave=np.cos(base)*shift+shift
    return wave

def main():
    args=docopt(__doc__)
    minV,maxV,on_ms,off_ms,waveName,reps=parse_args(args)
    waveFunc=globals()[waveName]

    DAQTask,DAQThrd=makeTrain(minV,maxV,on_ms,off_ms,waveFunc,LEDoff,reps)

    ms=2
    waveFuncs=[LEDsquarePulse,LEDlinRamp,LEDcos]
    waveDict={}

    for wf in waveFuncs:
        #XXX NOTE XXX 4.2 is the minimum voltage need to turn off the LED
        #waveDict[wf.__name__]=makeWave(0,4.2,ms,wf) #LOL DICT OF THREADS
        #waveDict[wf.__name__]=makeWave(4.2,4.2,ms,wf) #LOL DICT OF THREADS
        waveDict[wf.__name__]=makeWave(0,4.2,ms,wf) #maximum intensity
        waveDict[wf.__name__]=makeWave(4.1,4.2,ms,wf) #min V to evoke LED is 4.1

    #Trains
    #(1,4,LEDsquarePulase,LEDoff,5)
    #waveDict['LED_Train_sp_o1_f4_r5']

    #start our keyhandler so we can break shit
    charBuffer=Queue()
    #modestate=rigIOMan(charBuffer)
    class KH:
        def __init__(self):
            self.stopflag=0
        def keyHandler(self):return not self.stopflag
    kh=KH()
    keyHandler=kh.keyHandler
    kbdThrd=threading.Thread(target=keyListener,args=(charBuffer,keyHandler,)) #lambda:0 will exit on first keyhit leaving cb clean
    kbdThrd.start()

    #DAQTask,DAQThrd=waveDict['LEDsquarePulse'] #this could be very useful for launching these from keyboard or pairing to .pro files; one problem is the max/min and ms... balls gen on the fly?
    #DAQTask,DAQThrd=waveDict['LEDcos'] #this could be very useful for launching these from keyboard or pairing to .pro files; one problem is the max/min and ms... balls gen on the fly?
    DAQThrd.start()
    while kbdThrd.is_alive():
        key=charBuffer.get() #don't use the secrete escape key, it breaks this, should be fine in the other
        if key=='esc' or key=='q' or key=='@':# FIXME
            kh.stopflag=1
            break
    DAQTask.cleanup()
    DAQThrd.join()
    kbdThrd.join()
    #threading.current_thread().join(kbdThrd)


if __name__=='__main__':
    main()
