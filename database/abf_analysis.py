#!/usr/bin/env python3.3
import os
import numpy as np
from scipy import integrate, optimize #for quad or simps or whatever
from neo import AxonIO
from rig.ipython import embed
import pylab as plt

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

def find_rs_test(header):
    enabled=header['nWaveformEnable']
    step_size=header['fEpochInitLevel']
    cmds_steps=[ step_size[:10] , step_size[10:] ]
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

    fig=plt.figure(figsize=(10,5),frameon=False)
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

def plot_raw_aligned(block):
    segments=block.segments
    number_segments=len(segments)
    number_analog_signals=len(segments[0].analogsignals)

    number_subplots=number_analog_signals

    plt.figure()
    for segment in segments:
        for i in range(number_subplots):
            plt.subplot(number_subplots,1,i+1)
            plt.plot(segment.analogsignals[i].base)
            plt.title('%s'%block.file_origin)

def plot_raw_serries(block):
    pass

def get_protocol_offsets(protocol_name):
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

def print_tp_stats(filepath):
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
    
def get_segments(path,fn):
    fp=path+fn
    try:
        raw=AxonIO(fp)
        header=raw.read_header()
    except FileNotFoundError as e:
        print(e)
        return None,None,None,None
    starts,lengths,volts=find_rs_test(header)
    if not volts:
        return None,None,None,None
    else:
        segments=raw.read_block().segments
    #dict_callback(fn,segments,starts,lengths,volts)
    return segments,starts,lengths,volts

def main():
    from sqlalchemy.orm import Session
    from database.table_logic import logic_StepEdge
    from database.engines import engine
    from database.models import Cell, DataFile
    session=Session(engine)
    logic_StepEdge(session)

    path=get_abf_path()
    filenames=[f[0] for f in session.query(DataFile.filename).all()]
    #filenames=[f.filename for f in session.query(Cell).get(66).datafiles]
    #filenames= ['2013_12_13_0038.abf']
    #filenames= ['2013_12_13_0038.abf']
    #filenames= ['2013_12_13_0007.abf']
    #filenames= ['2013_12_13_0022.abf'] #breaks with 2*rest_baseline
    #filenames= ['2013_12_13_0006.abf'] #4th trace breaks with rest_baseline
    #filenames= ['2013_12_02_0003.abf'] #test for no waveforms

    #filepaths = [path+filename for filename in filenames]

    #from threading import Thread
    #from queue import Queue

    #q=Queue()

    #seg_dict={}
    #def dict_callback(filename,segments,starts,lengths,volts):
        #seg_dict[filename]=segments,starts,lengths,volts
        #print(filename)
        #q.task_done()

    #for fn in filenames:
        #fp=path+fn
        #monkey_business(path,fn,dict_callback)
        #print(fn)
        #new_thread=Thread(target=monkey_business,args=(path,fn,dict_callback))
        #q.put(new_thread)
        #t=q.get()
        #t.start()
    

    def plot_stuff(args):
        path,fn=args
        segments,starts,lengths,volts=get_segments(path,fn)
        if not segments:
            return None
        sigit=range(len(starts))
        for segment in segments:
            for analogsignal,i in zip(segment.analogsignals,sigit):
                A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index=compute_test_pulse_statistics(analogsignal, starts[i], lengths[i], volts[i])
                if Tau:
                    fig=plot_tp_stats(analogsignal,starts[i],lengths[i],A,Tau,C,Q,Rs,Rs_est,Rm,rest_baseline,pulse_baseline,fit_start_index,fn)
                    spath='/tmp/'+fn[:-4]+'_'+str(segment.index)+'.png'
                    print(spath)
                    fig.savefig(spath,bbox_inches='tight', pad_inches=0)
                    plt.close()

    
    from multiprocessing import Process,Pipe
    from datetime import datetime

    def spawn(f):
        def fun(pipe,x):
            pipe.send(f(x))
            pipe.close()
        return fun
    def parmap(f,X):
        pipe=[Pipe() for x in X]
        proc=[Process(target=spawn(f),args=(c,x)) for x,(p,c) in zip(X,pipe)]
        [p.start() for p in proc]
        [p.join() for p in proc]
        return [p.recv() for (p,c) in pipe]

    
    items=[(path,fn) for fn in filenames]
    print(len(items))
    #items=items[:320]
    #items=items[320:640]
    items=items[640:975]
    #items=items[900:920]
    start=datetime.now()
    parmap(plot_stuff, items)#, seg_dict.items()) #HOLY FUCK
    end=datetime.now()
    print(start,end,(end-start))
    #items=[(fn,tup) for fn,tup in seg_dict.items()]
    #for fn,tup in seg_dict.items():
        #nt=Thread(target=asdf,args=(fn,tup))
        #nt.start()


    #q.join()



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


