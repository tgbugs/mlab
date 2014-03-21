#!/usr/bin/env python3.3
import os
import socket
import numpy as np
from scipy import integrate, optimize #for quad or simps or whatever
from neo import AxonIO
from rig.ipython import embed
import pylab as plt
import gc


from multiprocessing import Process,Pipe
def spawn(f):
    def fun(pipe,x):
        pipe.send(f(x))
        pipe.close()
    return fun
def parmap(f,X):
    """ Function to make multiprocessing work correctly """
    pipe=[Pipe() for x in X]
    proc=[Process(target=spawn(f),args=(c,x)) for x,(p,c) in zip(X,pipe)]
    [p.start() for p in proc]
    [p.join() for p in proc]
    return [p.recv() for (p,c) in pipe]

def get_abf_path():
    """ return the abf path for a given computer """
    if os.name=='posix':
        abfpath='/mnt/str/tom/mlab_data/clampex/'
    elif socket.gethostname()=='andromeda':
        abfpath='D:/clampex/'
    else:
        abfpath='D:/tom_data/clampex/'
    return abfpath

def load_abf(filepath):
    raw=AxonIO(filename=filepath)
    block=raw.read_block(lazy=False,cascade=True)
    segments=block.segments
    header=raw.read_header()
    return raw,block,segments,header

def build_waveform(header):
    chans_on=header['nWaveformEnable'] #turns out I just havent properly updated neo at lab >_<
    header['nWaveformSource']

    nloops=header['lEpisodesPerRun']
    len_base=header['lNumSamplesPerEpisode']
    base=np.zeros_like(len_base)

    #epoch property list

    wave=np.vstack(( #or is it hstack...
    header['nEpochType'], #1 is step, 2 is ramp

    header['fEpochInitLevel'], #val
    header['fEpochLevelInc'], #val_inc

    header['lEpochInitDuration'], #time
    header['lEpochDurationInc'], #time_inc
    ))

    header['lPreTriggerSamples'] #not sure what this is actually for...

    header['nDigitalEnable']
    header['nActiveDACChannel']
    header['nDigitalValue']
    header['nDigitalHolding']

    #start_samp=header['lSynchArrayPtr']

    #sample_offset=header['nFileStartMillisecs'] #FIXME where is this number hiding!!!
    #sample_offset=200
    #sample_offset=header['lActualAcqLength']*(200/12000)
    sample_offset=7816 #TODO figure out where these bloody things come from :/

    def get_val_samp(loop_n,et,val,vi,samps,si):
        value=val+vi*loop_n
        nsamples=samps+si*loop_n
        return value,nsamples

    def build_traces(nloops,wave):
        channels={}
        for chan in range(len(chans_on)):
            channels[chan]=[]
            for loop_n in range(nloops):
                samps_start=0
                trace=np.zeros(len_base/2)
                for epoch in range(10*chan,10*(chan+1)):
                    value,samps_delta=get_val_samp(loop_n,*wave[:,epoch])
                    #print(epoch,value,samps_delta)
                    trace[samps_start+sample_offset:samps_start+samps_delta+sample_offset]=value
                    samps_start+=samps_delta
                channels[chan].append(trace)
        return channels

    return build_traces(nloops,wave)



def find_rs_test(header):
    enabled=header['nWaveformEnable'] #turns out I just havent properly updated neo at lab >_<
    step_size=header['fEpochInitLevel']
    cmds_steps=[ step_size[:10] , step_size[10:] ] #split the command channels in half
    volts=[]
    step_indexes=[]
    for command in cmds_steps:
        count=0
        is_on=enabled[count]
        if not is_on:
            break #FIXME this will throw off the index if the 2nd waveform is enabled I think?
        for step in command:
            if step != 0: #find the first value > 0 append it and stop
                volts.append(step)
                step_indexes.append(count)
                break
            count+=1
    #print('header volts',volts)
    #print('header step indexes', step_indexes)
    base_samples=header['lEpochInitDuration']
    cmds_durations=[ base_samples[:10], base_samples[10:] ]
    #print('header durations ',cmds_durations)
    lengths=[ cd[index] for cd,index in zip(cmds_durations,step_indexes) ]

    header['fEpochLevelInc']
    header['nEpochType'] #1 is step?


    header['nWaveformSource']
    header['nDigitalEnable']
    header['nDigitalHolding']

    prot_name=header['sProtocolPath'].split(b'/')[-1].decode('utf-8')
    starts=[get_protocol_offsets(prot_name)]*2
    #print('hdeater slv',starts,lengths,volts)

    return starts,lengths,volts

def compute_test_pulse_statistics(trace,start=7816,length=4000,milivolts=5):
    """ Passed the massimo seal of looks about right"""
    #FIXME the values here need to have the correct gains applied
    #TODO units!
    unit=trace.dimensionality.string
    #print(unit)
    if unit != 'pA': #Rs doesnt exist for current clamp, (bridge balance etc)
        return [None]*10

    #set up our data
    end=start+length
    dt=1/trace.sampling_rate.base #seconds
    times=np.array([i*dt for i in range(length)])
    signal=trace.base[start:end] #pA or mV ususally


    #fit a single exponential to find Tau
    fit_start=np.argmax(signal)
    fit_start_index=start+fit_start #yay for being able to add intervals with zero based indexing
    rest_baseline=np.mean(trace.base[:start])
    fit_times=times[fit_start:]
    fit_samples=signal[fit_start:]
    try:
        fit_times=np.float64(fit_times)
        fit_samples=np.float64(fit_samples)
        A,moTau,C=nlin_exp_fit(fit_times,fit_samples)#+abs(rest_baseline)) #XXX trace must be gt zero!, except that 0007 isnt anywhere close >_<
        Tau=-1/moTau
        #print(A,Tau,C)
        min_=np.min(fit_samples)
        max_=np.max(fit_samples)

        if Tau < 0:
            fit=single_exp(times,A,Tau,C) #FIXME dont need all these?
            print('ERROR! probably trying to fit noise') 
            #plt.plot(times,fit)
            #plt.plot(times,signal)
            #plt.show()
            #embed()
            return [None]*10
        else:
            pass
    except (RuntimeError,TypeError) as e:
        #plt.plot(times,signal,'r-')
        #plt.show()
        A,Tau,C=1,1,1
        print('Fit failed, probably trying to fit noise! Setting crap values')
        #print(e)


    #principles of Rs calculation
    #Tau=R*C
    #R=Tau/C
    #C=Q/milivolts
    #Q=integral(I)
    
    #baseline_target_start=-int(length/10)
    fit=single_exp(times,A,Tau,C) #FIXME dont need all these?
    #print(fit)
    close_to_C=(np.max(fit)-C)*.01+C #3% of the interval between max and steadystate away from steady state
    pulse_baseline_start=-sum(fit < close_to_C)
    #print(pulse_baseline_start)
    pulse_baseline=np.mean(signal[pulse_baseline_start:]) #FIXME use min???


    Q=integrate.simps(signal-pulse_baseline,times) #should be in pico coulombs if I'm integrating picoamps
    #Q_bad=integrate.simps(signal-min(signal[fit_start:]),times) #should be in pico coulombs if I'm integrating picoamps
    #print('Charge in pC',Q)#,Q_bad)
    Cap=Q/milivolts #-12/-3 = -9 => nanofarads
    Cap=Cap
    Rs=(Tau/Cap)*1000 #1000MO/GO #seconds/nanofarads 1/1E-9 => 9 == GO

    Rs_pA_step=signal[fit_start]-rest_baseline
    Rs_est=(milivolts/Rs_pA_step)*1000 #1000MO/1GO

    Rm_pA_step=pulse_baseline-rest_baseline #fit baseline should alwasy be less than int baseline, so int-fit
    Rm=(milivolts/Rm_pA_step)*1000 #1000MO/1GO #mV / pA ; -3 / -12 => 9 GO?

    #print('Rm step',Rm_pA_step,'pA')
    #print('Rs step',Rs_pA_step,'pA')
    #print('Rm=',Rm)
    #print('Rs_est=',Rs_est)
    #print('Rs=',Rs)

    return A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index

def plot_tp_stats(analogsignal,start,length,A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index,fn='lolwut'):
    end=start+length
    times=analogsignal.times.base[start:end]
    signal=analogsignal.base[start:end]
    lrt=times[0],times[-1] #used for plotting lines

    dt=1/analogsignal.sampling_rate
    zeroed_times=np.array([i*dt for i in range(end-fit_start_index)])
    #print(zeroed_times)
    fit_times=times[fit_start_index-start:end]
    fit=single_exp(zeroed_times,A,Tau,C)

    fig=plt.figure(figsize=(20,10),frameon=False)
    plt.title(analogsignal.segment.block.file_origin+' Tau= %3.2f, Q=%3.2f Rs= %3.2f, Rs_est= %3.2f, Rm= %3.2f'%(Tau*1000,Q,Rs,Rs_est,Rm) )
    plt.xlabel(analogsignal.times.units)
    plt.ylabel(analogsignal.units)
    plt.plot( times, signal, 'b-' , label='trace' ) #plot the signal
    plt.plot( fit_times, fit, 'r-', label='fit' ) #plot the fit and add the rest baseline back in (in addition to C)
    plt.plot( lrt, [rest_baseline]*2, 'c-', label='mean rest' ) #plot the rest baseline
    plt.plot( lrt, [pulse_baseline]*2, 'g-', label='mean pulse' ) #plot the pulse baseline
    plt.legend()
    plt.xlim(lrt)
    plt.ylim((pulse_baseline-100,pulse_baseline+400))

    return fig

def plot_all_tp_stats(segments,starts,lengths,volts):
    sigit=range(len(starts))
    fn=segments[0].block.file_origin
    for segment in segments:
        for analogsignal,i in zip(segment.analogsignals,sigit):
            A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index=compute_test_pulse_statistics(analogsignal, starts[i], lengths[i], volts[i])
            print(A,Tau,C)
            if Tau:
                fig=plot_tp_stats(analogsignal,starts[i],lengths[i],A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index,fn)
                spath=get_tmp_path()+fn[:-4]+'_'+str(segment.index)+'_tp.png'
                print(spath)
                fig.savefig(spath,bbox_inches='tight', pad_inches=0)
                fig.clf()
                plt.close()
                del(fig)
                gc.collect()

def single_exp(t,A,Tau,C):
    return A*np.exp(-t/Tau)+C

def _single_exp(t,A,moTau,C):
    """ used for computation to prevent stupid bugs in curve_fit"""
    return A*np.exp(t*moTau)+C

def nlin_exp_fit(t,y):
    opt_params, parm_cov = optimize.curve_fit(_single_exp,t,y,maxfev=20000)
    A,moTau,C = opt_params
    return A,moTau,C

def lin_exp_fit(t,y,C=0):
    y=y-C
    y=np.log(y)
    Tau, A_log = np.polyfit(t,y,1)
    A=np.exp(A_log)
    return A,Tau,C

def plot_raw_aligned(segments):
    number_segments=len(segments)
    number_analog_signals=len(segments[0].analogsignals)
    fn=segments[0].block.file_origin

    number_subplots=number_analog_signals

    figure=plt.figure(figsize=(20,20))
    for segment in segments:
        for i in range(number_subplots):
            plt.subplot(number_subplots,1,i+1)
            plt.plot(segment.analogsignals[i].base)
            plt.title('%s'%fn)
    plt.close()
    return figure

def plot_raw_serries(block):
    pass

def get_protocol_offsets(protocol_name): #TODO maintain the manual one elsewhere?
    """ as I have found no way to find the initial samples before the first step in a protocol we do it manually :/ """
    OFFSETS={
    '01_led_whole_cell_voltage.pro':7816,
    'current_step_-100-1000.pro':0,
    '1_led_loose_patch.pro':0,
    '1_led_loose_cell.pro':0,
    }
    return OFFSETS[protocol_name]

import struct
def struct_read(binary,format,offset=None):
    if offset is not None:
        binary.seek(offset)
    return struct.unpack(format, binary.read(struct.calcsize(format)))


def print_tp_stats(filepath): #FIXME this only works if there is only ONE epoch
#FIXME also need to make all of these things work with NEGATIVE test pulses! (just use the sign on the step)
    raw=AxonIO(filepath)
        #raw,block,segments,header=load_abf(filepath)
    try:
        header=raw.read_header()
    except FileNotFoundError:
        return None
    starts,lengths,volts=find_rs_test(header)
    #TODO match commands to the proper recording channels (analog signals)
    if not volts: #implies that none of the waveforms was on
        return None
    else:
        segments=raw.read_block().segments
    sigit=range(len(starts))
    Taus,Rss,Rs_ests,Rms=[],[],[],[]
    for segment in segments:
        for analogsignal,i in zip(segment.analogsignals,sigit):
            A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index=compute_test_pulse_statistics(analogsignal, starts[i], lengths[i], volts[i])
            Taus.append(Tau)
            Rss.append(Rs)
            Rs_ests.append(Rs_est)
            Rms.append(Rm)
    Taus=['%3.2f '%(t*1000) for t in Taus if t ]
    Rss=['%3.2f '%t for t in Rss if t ]
    Rs_ests=['%3.2f '%t for t in Rs_ests if t ]
    Rms=['%3.2f '%t for t in Rms if t ]
    print('Taus',Taus)
    print('Rses',Rss)
    print('Rs_ests',Rs_ests)
    print('Rms',Rms)
    return Taus,Rss,Rs_ests,Rms
    
def get_segments_with_step(filepath):
    try:
        raw=AxonIO(filepath)
        header=raw.read_header()
    except FileNotFoundError as e:
        print(e)
        del(raw)
        return None,None,None,None
    starts,lengths,volts=find_rs_test(header)
    if not volts:
        return None,None,None,None
    else:
        segments=raw.read_block().segments
    del(raw)
    return segments,starts,lengths,volts

def get_tmp_path(): #FIXME move to utils or something
    hostname=socket.gethostname()
    if os.name == 'posix':
        return '/tmp/'
    else: #'nt'
        if hostname=='HILL_RIG':
            return 'D:/tmp' #rig comp
        elif hostname == 'andromeda':
            return 'C:/tmp/' #a poor substitue but whatever
        elif hostname == 'athena':
            return  None #'T:/asdf/' #FIXME

def main():

    test_files=[
        '2013_12_13_0045.abf',
        '2013_12_13_0046.abf',
        '2013_12_13_0047.abf',
        '2013_12_13_0048.abf',
        '2013_12_13_0049.abf',
        '2013_12_13_0050.abf',
        '2013_12_13_0051.abf',
        '2013_12_13_0052.abf',
        '2013_12_13_0053.abf',
        '2013_12_13_0054.abf',
    ]
    more=[
        '2013_12_13_0055.abf',
        '2013_12_13_0056.abf',
        '2013_12_13_0057.abf',
        '2013_12_13_0058.abf',
        '2013_12_13_0059.abf',
        '2013_12_13_0060.abf',
        '2013_12_13_0061.abf',
        '2013_12_13_0062.abf',
        '2013_12_13_0063.abf',
        '2013_12_13_0064.abf',
        '2013_12_13_0065.abf',
        '2013_12_13_0066.abf',
        '2013_12_13_0067.abf',
        '2013_12_13_0068.abf',
    ]
    dat_dir='/home/tom/mlab_data/clampex/'
    #test_files=os.listdir(dat_dir)

    fig=plt.figure(figsize=(10,10))
    for filename in test_files:
        raw=AxonIO(dat_dir+filename)
        header=raw.read_header()
        print(repr(header))
        blk=raw.read_block()
        chans=build_waveform(header)
        n_chans=len(chans)
        scale=40
        for chan,traces in chans.items():
            plt.subplot(4,1,chan*2+1)
            for s in blk.segments:
                plt.plot(s.analogsignals[chan].base,'r-',linewidth=.5)
            plt.xlim(0,len(traces[0])/scale)
            plt.subplot(4,1,(chan+1)*2)
            plt.title(chan)
            tmax=0
            for trace in traces:
                plt.plot(trace,'k-')
                nmax=np.max(trace)
                if nmax > tmax:
                    tmax = nmax
            #plt.ylim(-1.2*tmax,1.2*tmax)
            plt.xlim(0,len(traces[0])/scale)
        plt.savefig('/tmp/test%s.png'%filename[-8:-4])
        plt.clf()

    

def _main():
    from sqlalchemy.orm import Session
    from database.table_logic import logic_StepEdge
    from database.engines import engine
    from database.models import Cell, DataFile
    session=Session(engine)
    logic_StepEdge(session)

    path=get_abf_path()
    savepath=get_tmp_path() 
    filenames=[f[0] for f in session.query(DataFile.filename).all()]
    #filenames=[f.filename for f in session.query(Cell).get(66).datafiles]
    #filenames= ['2013_12_13_0038.abf']
    #filenames= ['2013_12_13_0038.abf']
    #filenames= ['2013_12_13_0007.abf']
    #filenames= ['2013_12_13_0022.abf'] #breaks with 2*rest_baseline
    #filenames= ['2013_12_13_0006.abf'] #4th trace breaks with rest_baseline
    #filenames= ['2013_12_02_0003.abf'] #test for no waveforms

    #filepaths = [path+filename for filename in filenames]

    def plot_stuff(args):
        path,fn=args
        print(path)
        segments,starts,lengths,volts=get_segments_with_step(path+fn)
        if segments:
            plot_all_tp_stats(segments,starts,lengths,volts)
        else:
            try:
                segments=AxonIO(path+fn).read_block().segments
            except FileNotFoundError as e:
                print(e)
                return None
        #fig=plot_raw_aligned(segments)
        #spath=savepath+fn[:-4]+'_al.png'
        #print(spath)
        #fig.savefig(spath,bbox_inches='tight', pad_inches=0)
        #fig.clf()
        #plt.close()
        #del(fig,segments)
        #gc.collect() #FIXME none of this seemes to make any difference for memory usage :/
                     #WELL on the otherhand it did reduce it enough to prevent the explosion...
   
    from datetime import datetime
    
    items=[(path,fn) for fn in filenames]
    print(len(items))
    itemss=[]
    #itemss.append(items[900:920])
    divs=33 #memory limits man :/
    divisions=np.int32(np.linspace(0,975,divs))
    for d in range(divs-3,divs-1):
        print(divisions[d],divisions[d+1])
        dl=divisions[d]
        dr=divisions[d+1]
        itemss.append(items[dl:dr])
    itemss.append(items[divisions[-1]:])
    #itemss.append(items[:320])
    #itemss.append(items[320:640])
    #itemss.append(items[640:975])
    if socket.gethostname() != 'athena':
        if len(items) < 30:
            raise OSError('seriously dude, check your memory, 32gigs is only barely enough for some of this')
    start=datetime.now()
    for item,i in zip(itemss,range(len(itemss))):
        print('starting batch %s'%i)
        #parmap(plot_stuff, item) #XXX WARNING!!! This will explode anything but athena
        #FIXME EOFError on andromeda? pickel error?
        print(item)
        [plot_stuff(j) for j in item] #super confusing since item is a list >_<
    end=datetime.now()
    print(start,end,(end-start))
    #items=[(fn,tup) for fn,tup in seg_dict.items()]
    #for fn,tup in seg_dict.items():
        #nt=Thread(target=asdf,args=(fn,tup))
        #nt.start()





    #for fn in filenames:
        #fp=path+fn
        #print('\n')
        #binary=open(fp,'rb')
        #lines=binary.readlines()
        #l1=binary.readline() #399
        #print(len(l1))
        #l2=binary.readline() #4499?? yes
        #print(len(l2)) #5132
        #print(l2[4499:])
        
        #print_tp_stats(fp)

        #try:
            #raw=AxonIO(fp)
            #header=raw.read_header()
        #except FileNotFoundError as e:
            #print(e)
        #print(header['sProtocolPath'])
        #print(header['nWaveformEnable'])
        #starts,lengths,volts=find_rs_test(header)
        #if not volts:
            #continue
        #else:
            #segments=raw.read_block().segments
        #TODO match commands to the proper recording channels (analog signals)
        #sigit=range(len(starts))
        #plts,Rs=compute_rs(segments[2].analogsignals[1],starts[0],lengths[0],volts[0])
        #if plts:
            #plts.title(fp)
            #plts.show()
        #for segment in segments:
            #for analogsignal,i in zip(segment.analogsignals,sigit):
                #A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index=compute_test_pulse_statistics(analogsignal, starts[i], lengths[i], volts[i])
                #if Tau:
                    #plot_tp_stats(analogsignal,starts[i],lengths[i],A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index,fn)
                    #spath='/tmp/'+fn[:-4]+'_'+str(segment.index)+'.png'
                    #print(spath)
                    #plt.savefig(spath,bbox_inches='tight', pad_inches=0)
                    #plt.close()
                    #plt.savefig(fn[-4]+'.png',bbox_inches='tight', pad_inches=0)

                    #plt.show()

        #plot_raw_aligned(block)
    #embed()
    #plt.show()

    #TODO 2013_12_13_0038.abf for testing

         



if __name__ == '__main__':
    main()


