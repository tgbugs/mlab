#!/usr/bin/env python3.3
from rig.ipython import embed
import socket
import numpy as np
import gc
#import scipy as sci
import pylab as plt
from neo import AxonIO, AnalogSignal

from abf_analysis import get_abf_path, load_abf

#magic numbers!
_mu='\u03BC'

def pA(sig,gain): #XXX dep
    if sig.unit=='pA':
        return sig/gain
    else:
        raise TypeError('units werent pA')
def mV(pA_signal,clx_rescale=2): #XXX dep
    base=pA_signal.base
    out=AnalogSignal(base/clx_rescale,  units='mV', name=pA_signal.name,
                     sampling_rate=pA_signal.sampling_rate,
                     t_start=pA_signal.t_start,#*0,
                     channel_index=pA_signal.channel_index)
    return out  #FIXME the raw for the abf file seems to be pA no matter what to get mV divide by two?!
def V(pA_signal): #FIXME, only need this if the file is stopped half way through recording (wtf)
    out=mV(pA_signal)
    out.units='V'
    return out
def set_gain_and_time_func(gain=1,zero_times=False):
    def set_gain(sig):
        if zero_times:
            sig.t_start=sig.t_start*0
        return sig/gain
    return set_gain


def plot_signal(sig):
    plt.plot(sig.times.base,sig.base) #use base because Quantities is slow as BALLS
    plt.xlabel(sig.times.units)
    plt.ylabel(sig.units)


def plot_abf(filepath,signal_map): #FIXME need better abstraction for the sigmap
    raw,block,segments=load_abf(filepath)
    nseg=len(segments)
    plt.figure()
    for seg,n in zip(segments,range(nseg)):
        plt.title(block.file_origin)
        #plt.title('%s Segment %s'%(block.file_origin,n))
        nas=seg.size()['analogsignals']
        for anasig,i in zip(seg.analogsignals,range(nas)):
            plt.subplot(nas,1,i+1)
            stp=signal_map[i](anasig)
            plot_signal(stp)
            #plot_signal(anasig)

fADC_DO_0=9.5017
fADC_DA_0=24.7521
fDAC_scale_0=20

fADC_DO_1=2.1144
fADC_DA_1=4.2731
fDAC_scale_1=1

def transform_maker(offset,gain):#,scale):
    def t_signal(signal):
        rescale=(signal.base/gain)+offset
        #rescale=signal.base
        out=AnalogSignal(rescale, units=signal.units, name=signal.name,
                         sampling_rate=signal.sampling_rate,
                         t_start=signal.t_start,
                         channel_index=signal.channel_index)
        return out
    return t_signal


zero=transform_maker(0,400) #FIXME why is this *20 again? gain is only @ 20
one=transform_maker(0,5) #FIXME why do I need this!?

image_path='D:/tom_data/macroscope/'
#path='D:/tom_data/clampex/'
#path='/mnt/tgdata/clampex/'
path='D:/clampex/'
filenames=[
    '2013_12_04_0024.abf',
    '2013_12_04_0025.abf',
    '2013_12_04_0026.abf',
    '2013_12_04_0036.abf', #perfect pathalogical example
]

sig_map={0:set_gain_and_time_func(20,True),1:set_gain_and_time_func(1,True)}
sig_map_nt={0:set_gain_and_time_func(20,False),1:set_gain_and_time_func(1,False)} #FIXME why is the time doubled?

test_map={0:zero,1:one}

#[plot_abf(path+fn,sig_map_nt) for fn in filenames]
#[plot_abf(path+fn,test_map) for fn in filenames]
#raw,block,segments=load_abf(path+filenames[0])


def detect_spikes(array,thresh=3,max_thresh=5,threshold=None,space=5): #FIXME need an actual threshold?
    #TODO local max using f>=thrs s<thrs switch on the way down, and get the indexes and then call max() on it?
    try:
        iter(array.base)
        array=array.base
    except:
        pass

    avg=np.mean(array)
    std=np.std(array)
    if threshold:
        pass
    elif max(array) > avg+std*max_thresh:
        threshold=avg+thresh*std
    else:
        #print('guessing noise')
        threshold=avg+std*max_thresh
        if max(array) < threshold:
            #print('yep it was')
            return [],threshold

    first=array[:-space] #5 to hopefully prevent the weirdness with tiny fluctuations
    second=array[space:]
    base=len(first)-space
    def check_thrs(i):
        #for n in range((space+1)//2,space):
        for n in range(space):
            if (first[i+n]<=threshold and second[i+n]>threshold):
                pass
            else:
                return 0
        return 1
    s_list=[ i for i in range(base) if check_thrs(i) ]
    #s_list=[ i for i in range(base) if first[i]<=threshold and second[i]>threshold ]
    #s_list=[ i for i in range(base-1) if first[i]<=threshold and second[i]>threshold and first[i+1]<=threshold and second[i+1]>threshold ]
    #s_index=s_list[0::space] #take only the first spike #need the -1 to prevent aliasing?
    return s_list,threshold
    #return s_index

def detect_led(led_array):
    if led_array.base:
        led_array=led_array.base
    maxV=max(led_array)
    minV=min(led_array)
    if maxV-minV < .095:
        return [],base,maxV,minV
    half=maxV-(maxV-minV)/2
    led_on_index=np.where(led_array < half)[0]
    #led_on_index=np.where(led_array.base)[0]
    base=np.ones_like(led_on_index)
    return led_on_index,base,maxV,minV

def plot_count_spikes(filepath,signal_map): #FIXME integrate this with count_spikes properly
    """ useful for manual review """
    raw,block,segments,header=load_abf(filepath)
    if list(raw.read_header()['nADCSamplingSeq'][:2]) != [1,2]: #FIXME
        print('Not a ledstim file')
        return None,None
    nseg=len(segments)
    gains=header['fTelegraphAdditGain'] #TODO
    zero=transform_maker(0,20*gains[0]) #cell
    one=transform_maker(0,5) #led
    plt.figure()
    counts=[]
    for seg,n in zip(segments,range(nseg)):
        if len(seg.analogsignals) != 2:
            print('No led channel found.')
            continue
        plt.subplot(nseg,1,n+1)
        nas=seg.size()['analogsignals']
        signal=zero(seg.analogsignals[0])
        led=one(seg.analogsignals[1])
        led_on_index,base,maxV,minV=detect_led(led) #FIXME move this to count_spikes
        if not len(led_on_index):
            print('No led detected maxV: %s minV: %s'%(maxV,minV))
            continue
        sig_on=signal.base[led_on_index]
        sig_mean=np.mean(sig_on)
        sig_std=np.std(sig_on)
        #plt.plot(sig_std+sig_mean)
        sm_arr=base*sig_mean
        std_arr=base*sig_std

        thresh=3.3

        s_list=detect_spikes(sig_on,thresh,5)
        counts.append(len(s_list))

        [plt.plot(s,sig_on[s],'ro') for s in s_list] #plot all the spikes

        plt.plot(sig_on,'k-')
        plt.plot(sm_arr,'b-')
        plt.fill_between(np.arange(len(sm_arr)),sm_arr-std_arr*thresh,sm_arr+std_arr*thresh,color=(.8,.8,1))
        plt.xlim((0,len(sig_on)))

        plt.title('%s spikes %s'%(len(s_list),block.file_origin))
        #plt.title(block.file_origin)
        #plt.title('%s Segment %s'%(block.file_origin,n))
    return np.mean(counts),np.var(counts),counts

def count_spikes(filepath,signal_map): #TODO
    raw,block,segments,header=load_abf(filepath)
    nseg=len(segments)
    gains=header['fTelegraphAdditGain'] #TODO
    zero=transform_maker(0,20*gains[0]) #cell
    one=transform_maker(0,5) #led
    counts=[]
    for seg,n in zip(segments,range(nseg)):
        nas=seg.size()['analogsignals']
        signal=zero(seg.analogsignals[0])
        led=one(seg.analogsignals[1])
        led_on_index=np.where(led.base < led.base[0]-.05)[0]
        base=np.ones_like(led_on_index)
        sig_on=signal.base[led_on_index]

        thresh=3.3

        #print(filepath)
        s_list=detect_spikes(sig_on,thresh,5)
        counts.append(len(s_list))
    return np.mean(counts),np.var(counts),counts


#count_spikes(path+filenames[0],None)
#[count_spikes(path+fn,test_map) for fn in filenames]
#plt.show()
#embed()

def get_disp(origin,target):
    a2=(origin[0]-target[0])**2
    b2=(origin[1]-target[1])**2
    return (a2+b2)**.5

sqrt2=get_disp([0,0],[1,1])
#print('This should be square root of 2',sqrt2)
sqrt2=get_disp([0,0],[-1,-1])
#print('And so should this!',sqrt2)


def esp_fix_x(x_vector):
    """ the positive axis for the espX is on the left hand side so multiply by -1"""
    return -x_vector

from database.models import *
from database.engines import engine
from sqlalchemy.orm import Session #FIXME need logics
import os
import sys

session=Session(engine)
s=session

def get_metadata_query(MappedClass,id_,mds_name):
    MD=MappedClass.MetaData
    md_query=s.query(MD).filter_by(parent_id=id_).\
        join(MetaDataSource,MD.metadatasource).\
        filter_by(name=mds_name).order_by(MD.id)
    return md_query

    #name:spikes #FIXME make it so manual threshold works AND align all spikes from the detection forward
for_review={
    '03_0117':[0,0,0,0,0],
    '03_0121':[0,0,0,0,0],
    '03_0125':[0,0,0,0,0],
    '04_0007':[26,23,22,20,20],
    '04_0009':[28,25,22,20,19],
    '04_0010':[14,13,12,13,12],
    '04_0011':[19,18,16,15,15],
    '04_0012':[17,15,14,14,15],
    '04_0013':[17,19,17,17,16],
    '04_0014':[15,17,15,14,12],
    '04_0015':[11,9,11,11,11],
    '04_0031':[0,0,0,0,0],
}
reviews=['2013_12_'+review+'.abf' for review in for_review.keys()]
#[plot_count_spikes(path+fn,test_map) for fn in reviews]
reviewed={'2013_12_'+review+'.abf':list_ for review,list_ in for_review.items()}

to_ignore=[ #see LB1:81
    '03_0041', #aperature was closed
    '03_0042', #aperature about half open
    '08_0002', #something got recalibrated in the middle
    '08_0001', #shutter closed
    '08_0002', #shutter closed
    '08_0003', #shutter closed
    '08_0022', #min was at 0V so way more spikes #FIXME automate?
    '08_0023', #min was at 0V so way more spikes
    '08_0024', #min was at 0V so way more spikes
    '08_0025', #min was at 0V so way more spikes
    '08_0026', #min was at 0V so way more spikes
    '08_0027', #min was at 0V so way more spikes
    '08_0028', #min was at 0V so way more spikes
    '08_0053', #shutter open
    '08_0076', #accident with membrane test
    '08_0077', #accident with membrane test
    '10_0001', #was a test run with a completely open aperature
    '10_0010', #missing 3 channels not sure what happened
    '10_0011', #complete garbage and not even in the list for cell 36
    '10_0012', #somehow this was recorded as a control despite being even? thing it has to do with the problems above
]
to_ignore.extend(['10_0%s'%i for i in range(143,177)])  #lost the cell here
ignored=['2013_12_'+ignore+'.abf' for ignore in to_ignore]

#TODO threading with a callback that returns our numbers
from threading import Thread

class accumulator: #FIXME Queue??
    positions=[]
    distances=[]
    spike_means=[]
    spike_vars=[]
    def append(pos,dist,mean,var):
        self.positions.append(position)
        self.distances.append(dist)
        self.spike_means.append(mean)
        self.spike_vars.append(var)


def bin_dists(dist,mean,std,bin_width=.025): #FIXME return dont plot?
    shift=bin_width/2
    bin_lefts=np.arange(-shift,10*bin_width,bin_width)
    bin_dict={}
    for v in bin_lefts:
        bin_dict[v]=[]#[[],[]]
    for d,m,s in zip(dist,mean,std):
        left=bin_lefts[bin_lefts<=d][-1] #left inclusive
        #right=left+bin_width
        bin_dict[left].append(m)
        #bin_dict[left][1].append(s)
    for left_bin,means in bin_dict.items():
        new_mean=np.mean(means)
        new_std=np.std(means) #FIXME ignores the individual vars
        new_sem=new_std/np.sqrt(len(means))
        #plt.errorbar(left_bin+shift,new_mean,fmt='bo',ecolor=(.8,.8,1),yerr=new_std,capthick=2)
        plt.errorbar(left_bin+shift,new_mean,fmt='ko',ecolor=(.2,.2,.2),yerr=new_sem,capsize=8,capthick=4,elinewidth=3,markersize=20)
    return bin_dict

def get_cell_data(cid,abfpath):
    cell=s.query(Cell).get(cid)
    #DFMD=DataFile.MetaData
    #cell_pos=s.query(Cell.MetaData).filter_by(parent_id=cid).\
        #join(MetaDataSource,Cell.MetaData.metadatasource).\
        #filter_by(name='getPos').order_by(Cell.MetaData.id).first().value
    #print(cell_pos)
    #TODO get slice points
    slice_=cell.parent
    s_pos=get_metadata_query(Slice,slice_.id,'getPos').all()[:3]
    #print(s_pos)
    files=s.query(DataFile).join(Cell,DataFile.subjects).filter(Cell.id==cid).order_by(DataFile.creationDateTime).all()
    positions=[]
    dists=[]
    smeans=[] #for spike counts
    svars=[] #for spike counts
    counts={} #raw counts
    for filename,distance in cell.distances.items(): #XXX NOTE XXX not ordered
        if filename in ignored:
            continue
        filepath=abfpath+filename
        size=os.path.getsize(filepath)
        #print(size)
        if size != 10009088 or size != 2009088: #FIXME another way to detect filetype really just need a way to get the protocol
            #print(size)
            continue
        fp=s.query(DataFile).get(('file:///'+abfpath,filename)).position #FIXME ;_; add eq ne hash to datafile
        positions.append(fp)
        dists.append(distance)
        try:
            _scount=reviewed[filename]
            spike_mean=np.mean(_scount)
            spike_var=np.var(_scount)
        except KeyError:
            spike_mean,spike_var,_scount=count_spikes(filepath,None) #TODO OH NOSE MEMORY USAGE
        counts[filename]=_scount
        smeans.append(spike_mean)
        svars.append(spike_var)

    #TODO use a Queue to block on threads until all the spikes are gotten

    pos=np.array(positions)
    #embed()
    return cid,cell.position,pos,dists,smeans,svars,s_pos,counts

def get_cell_traces(cid,abfpath):
    cell=s.query(Cell).get(cid)
    filepaths=[]
    dists=[]
    files=cell.datafiles
    files.sort(key=lambda file:file.filename) #FIXME assuming not sorted
    for file in files:
        filename=file.filename
        distance=file.distances[cid]
        if filename in ignored:
            print(filename,'ignored')
            continue
        filepath=abfpath+filename #FIXME
        size=os.path.getsize(filepath)
        if size != 10009088 and size != 2009088: #FIXME another way to detect filetype really just need a way to get the protocol
            print(filepath,size)
            continue
        filepaths.append(abfpath+filename)
        dists.append(distance)
    return filepaths,dists

def plot_abf_traces(filepaths,dists,spikes=False,spike_func=lambda filepath:None,std_thrs=3,std_max=5,threshold_func=lambda filepath:None,cell_id=None,do_plot=False): #FIXME this is for 58 alternating
    #for filepath,distance in 
    from abf_analysis import parmap
    #from queue import Queue
    #args=zip(filepaths,dists)
    #[print(arg) for arg in args]

    #baseline_spikes=Queue()
    #baseline_spikes.put(mean_base)

    

    def dothing(args):
        fp1,fp2,d1,d2=args
        fn=fp1.split('/')[-1]
        figure=plt.figure(figsize=(20,20))
        spike_counts=[]
        spike_dist=None
        base_counts=[]
        base_dist=None
        for filepath,distance in zip((fp1,fp2),(d1,d2)):
            raw,block,segments,header=load_abf(filepath)
            if list(raw.read_header()['nADCSamplingSeq'][:2]) != [1,2]: #FIXME
                print('Not a ledstim file')
                return None,None

            #print(header['nADCSamplingSeq']) #gain debugging
            #print(header['nTelegraphEnable'])
            #print(header['fTelegraphAdditGain'])
            #gains=header['fTelegraphAdditGain'] #TODO
            #print(fn,gains)
            #TODO cell.headstage number?!
            #headstage_number=1 #FIXME
            #gain=gains[headstage_number] #FIXME the problem I think is still in AxonIO
            #zero=transform_maker(0,20*gain) #FIXME where does the first 20 come from !?
            #one=transform_maker(0,5) #led
            #one=transform_maker(0,10) #led no idea why the gain is different for these
            nseg=len(segments)
            for seg,n in zip(segments,range(nseg)):
                title_base=''
                if nseg == 1:
                    plt.subplot(6,1,6)
                    base_fp=filepath
                else:
                    dist_fp=filepath
                    plt.subplot(6,1,n+1)
                signal=seg.analogsignals[0].base
                units_sig=seg.analogsignals[0].units
                sig_times=seg.analogsignals[0].times.base
                units_sig_times=seg.analogsignals[0].times.units
                led=seg.analogsignals[1].base
                led_on_index,base,maxV,minV=detect_led(led) #FIXME move this to count_spikes
                if not len(led_on_index):
                    print('No led detected maxV: %s minV: %s'%(maxV,minV))
                    continue
                sig_on=signal[led_on_index]
                sig_on_times=sig_times[led_on_index] #FIXME may not be synch?
                sig_mean=np.mean(sig_on)
                sig_std=np.std(sig_on)
                #plt.plot(sig_std+sig_mean)
                sm_arr=base*sig_mean
                sm_arr_times=sig_on_times #[led_on_index]
                std_arr=base*sig_std
                
                #do spike detection
                if spikes:
                    spike_indexes,threshold=detect_spikes(sig_on,std_thrs,std_max,threshold_func(filepath))
                    spike_times=sig_on_times[spike_indexes]
                    if spike_func(filepath):
                        sc=spike_func(filepath)[seg.index]
                    else:
                        sc=len(spike_indexes)
                    if nseg == 1:
                        base_counts.append(sc)
                        base_dist=distance
                    else:
                        spike_counts.append(sc)
                        spike_dist=distance
                    #TODO find a way to associate the spikecount with the DataFile
                    plt.plot(spike_times,sig_on[spike_indexes],'ro')
                    title_base+='%s spikes '%(sc)

                
                if do_plot:
                    title_base+='%s $\mu$m from cell %s $\\verb|%s|$ '%(int(distance*1000),cell_id,block.file_origin[:-4])
                    #title_base+='gain = %s *20'%gain
                    plt.title(title_base)

                    plt.xlabel(units_sig_times)
                    plt.ylabel(units_sig)

                    #plt.xlabel(led.times.units)
                    #plt.ylabel(led.units)
                    #plt.plot(led.times.base[led_on_index],led.base[led_on_index])
                    lrf=(sig_on_times[0],sig_on_times[-1])
                    plt.plot(sig_on_times[::10],sig_on[::10],'k-',linewidth=1)
                    plt.plot(lrf,[sig_mean]*2,'b-', label = 'sig mean' )
                    plt.plot(lrf,[threshold]*2,'m-', label = 'threshold' )
                    plt.plot(lrf,[sig_mean+sig_std*std_max]*2,'y-', label = 'max thresh' )
                    if threshold_func(filepath):
                        plt.plot(lrf,[threshold_func(filepath)]*2,'g-', label = 'manual thresh' )
                    plt.fill_between(np.arange(len(sm_arr)),sm_arr-std_arr*std_thrs,sm_arr+std_arr*std_thrs,color=(.8,.8,1))
                    plt.xlim((sig_on_times[0],sig_on_times[-1]))
                    plt.legend(loc='upper right',fontsize='xx-small',frameon=False)
        
        spike_count_callback(base_counts,spike_counts,base_dist,spike_dist,dist_fp,base_fp)
        spath='/tmp/'+str(cell_id)+'_'+fn[:-4]+'.png'
        if do_plot:
            print(spath)
            plt.savefig(spath,bbox_inches='tight',pad_inches=0)
        #plt.show()
        figure.clf() #might reduce mem footprint
        plt.close()
        gc.collect()

    cont={}
    cont['base_dist_stats']=[]
    cont['spike_dist_stats']=[]
    cont['norm_dist_stats']=[]
    cont['bnorm_dist_stats']=[]
    spike_fn_dict={}
    args=[(f1,f2,d1,d2) for f1,f2,d1,d2 in zip(filepaths[0::2],filepaths[1::2],dists[0::2],dists[1::2])]
    def spike_count_callback(base_counts,spike_counts,base_dist,spike_dist,filepath,base_fp):
        mean_base=np.mean(base_counts)
        std_base=np.std(base_counts)
        mean_spikes=np.mean(spike_counts)
        std_spikes=np.std(spike_counts)
        norm_counts=spike_counts/mean_base #normalize the counts at distance by the mean base
        mean_norm=np.mean(norm_counts)
        std_norm=np.std(norm_counts)
        spike_fn_dict[filepath]=spike_counts
        spike_fn_dict[base_fp]=base_counts


        cont['base_dist_stats'].append((base_dist,mean_base,std_base))#,base_counts))
        cont['spike_dist_stats'].append((spike_dist,mean_spikes,std_spikes))#,spike_counts))
        cont['norm_dist_stats'].append((spike_dist,mean_norm,std_norm))#,norm_counts))
        #print(cont.base_dist_stats)
        #print(cont.spike_dist_stats)
        #print(cont.norm_dist_stats)
        #TODO add position...
    [dothing(arg) for arg in args] #bloody callbacks not working
    #parmap(dothing,args)

    b=np.array(cont['base_dist_stats'])
    #bdm=np.mean(b[:,0]) #get the mean distance for all the baselines
    bm=np.mean(b[:,1])
    bstd=np.std(b[:,1])
    base_normed=(b[:,1]-bm)/bstd #mean subtracted and divided by std
    bn_list=[(d,m,0) for d,m in zip(b[:,0],base_normed)]
    #bsem=bstd/np.sqrt(len(b[:,1]))
    cont['bnorm_dist_stats']=bn_list

    dist_stats=cont['base_dist_stats']#+cont['bnorm_dist_stats']
    plot_by_dist(dist_stats,cell_id,filepaths[-1][-8:-4])
    return cont,spike_fn_dict

def plot_by_dist(dist_stats,cell_id,end_file,yl='Normalized',yu='um'):
    normed=np.array(dist_stats)#np.array(cont['norm_dist_stats'])
    fig=plt.figure(figsize=(20,20))
    dist,mean,std,bin_width=normed[:,0],normed[:,1]*1000,normed[:,2],25
    shift=bin_width/2
    bin_lefts=np.arange(-shift,10*bin_width,bin_width)
    bin_dict={}
    print(mean)
    for v in bin_lefts:
        bin_dict[v]=[]#[[],[]]
    for d,m,s in zip(dist,mean,std):
        left=bin_lefts[bin_lefts<=d][-1] #left inclusive
        #right=left+bin_width
        bin_dict[left].append(m)
        #bin_dict[left][1].append(s)
    for left_bin,means in bin_dict.items():
        new_mean=np.mean(means)
        new_std=np.std(means) #FIXME ignores the individual vars
        new_sem=new_std/np.sqrt(len(means))
        #plt.errorbar(left_bin+shift,new_mean,fmt='bo',ecolor=(.8,.8,1),yerr=new_std,capthick=2)
        print('hell0')
        plt.errorbar(left_bin+shift,new_mean,fmt='ko',ecolor=(.2,.2,.2),yerr=new_sem,capsize=8,capthick=4,elinewidth=3,markersize=20)

    #plt.errorbar(normed[:,0]*1000,normed[:,1],yerr=normed[:,2],fmt='ko',ecolor=(1,1,1))
    #plt.xlim((.01,.250))
    #plt.ylim(0,1.5)
    format_axes(fig.axes[0],50,50)
    plt.yticks(np.arange(0,1.25,.25))
    plt.xticks(np.arange(0,225,25))
    plt.xlim(xmin=-2)
    plt.xlabel('Distance from cell body in um')
    plt.ylabel('%s spikes %s'%(yl,yu))
    plt.title('%s spikes as a function of distance for cell %s'%(yl,cell_id))
    fig.savefig('/tmp/norm_dist_%s_%s.png'%(cell_id,end_file),bbox_inches='tight',pad_inches=0)

def plot_cell_data(cid,cell_pos,df_pos,dists,smeans,svars,slice_pos):
    plt.figure()
    plt.title('Cell %s'%cid)
    bin_dists(dists,smeans,svars) #TODO
    #plt.bar(np.array(dists),smeans,np.ones_like(dists)*.025,color=(.8,.8,1),yerr=svars,align='center')

    plt.figure()
    plt.title('Cell %s'%cid)
    plt.plot(esp_fix_x(df_pos[:,0]),df_pos[:,1],'bo') #TODO these are flipped from reality!
    plt.plot(esp_fix_x(cell_pos[0]),cell_pos[1],'ro') #FIXME dake the math and shit out of here for readability 
    [plt.plot(esp_fix_x(p.value[0]),p.value[1],'go') for p in slice_pos] #plot the slice positions
    for count,x,y in zip(smeans,esp_fix_x(df_pos[:,0]),df_pos[:,1]):
       plt.annotate(
            '%s'%count,  #aka label
            xy = (x,y), xytext = (-20,20),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'),
       )

def get_dist_data(file,callback=None): #get data from a datafile
    #TODO
    callback()
    return

def get_n_before(n,filepaths,end_file):
    """ FILEPATHS MUST BE SORTED!!! """
    print(len(filepaths))
    #base=[0]*len(filepaths)
    index=filepaths.index(end_file)
    #for i in range(index-57,index+1):
        #base[i]=1
    #print(base)
    return np.arange(index-(n-1),index+1)


def notes():
    #_cell_endfile=review;threshold,max_above
    _36_0060=1,8,19,39,55;3,5

def threshold_maker(path,THRS_DICT={}):
    threshold_dict={path+k+'.abf':v for k,v in THRS_DICT.items()}
    def threshold_func(filepath):
        try:
            threshold=threshold_dict[filepath]
        except:
            threshold=None
        return threshold
    return threshold_func

THRS_DICT={ #FIXME may need to include sub channels?
    '2013_12_10_0019':.7,
    '2013_12_10_0039':1,
    '2013_12_10_0055':1,
    '2013_12_10_0069':1.5,
    '2013_12_10_0079':1.2,
    '2013_12_10_0088':0.9,
    '2013_12_10_0097':1.5,
    '2013_12_10_0189':2.7,
    '2013_12_10_0214':3.3,
    '2013_12_10_0216':3.27,
    '2013_12_10_0217':3.55,
    #'2013_12_10_0221':3.25,
    '2013_12_10_0222':3.4,
    '2013_12_10_0223':3.4,
    '2013_12_10_0225':3.7,
    #'2013_12_10_0226':3.45,
    '2013_12_10_0227':3.5,
    '2013_12_10_0233':3.41,
    '2013_12_11_0000':3.5,
    '2013_12_11_0074':1.2,
    '2013_12_11_0081':1.2,
    '2013_12_11_0083':1.5,
    '2013_12_11_0085':1.8,
    '2013_12_11_0089':2.5,
    '2013_12_11_0090':2.0,
    '2013_12_11_0092':2.2,
    '2013_12_11_0093':2.3,
    '2013_12_11_0094':2.5,
    '2013_12_11_0100':2.7,
    '2013_12_11_0102':2.7,
    '2013_12_11_0104':2.7,
    '2013_12_11_0116':3.0,
    '2013_12_11_0187':5.3,
    '2013_12_11_0186':5.2,
    '2013_12_11_0188':5.1,
    '2013_12_11_0190':5.1,
    '2013_12_11_0051':3.6,
    '2013_12_11_0052':3.7,
    '2013_12_11_0054':3.6,
    '2013_12_11_0056':3.6,
    '2013_12_11_0058':3.65,
    '2013_12_11_0185':5,
}

def make_spike_count_dict(path,COUNT_DICT={}):
    count_dict={path+k+'.abf':v for k,v in COUNT_DICT.items()}
    def count_func(filepath):
        try:
            count=count_dict[filepath]
        except:
            count=None #FIXME lenght?
        return count
    return count_func
COUNT_DICT={ #manual counts for traces that are super rough and I don't fell like down sampling right now
    '2013_12_10_0221':[8],
    '2013_12_10_0222':[7,7,6,7,5],
    '2013_12_10_0223':[6],
    '2013_12_10_0225':[6],
    '2013_12_10_0226':[6,5,5,4,6],
    '2013_12_10_0227':[5],
    '2013_12_10_0228':[3,3,3,3,3],
    '2013_12_10_0229':[6],
    '2013_12_10_0230':[4,5,5,4,4],
    '2013_12_10_0231':[6],
    '2013_12_10_0232':[3,3,3,3,4],
    '2013_12_10_0233':[6],
    '2013_12_11_0000':[8],
    '2013_12_11_0001':[2,0,0,2,2],
    '2013_12_11_0002':[8],
    '2013_12_11_0004':[8],
    '2013_12_11_0005':[6,6,6,6,6,6],
    '2013_12_11_0006':[6],
    '2013_12_11_0008':[8],
    '2013_12_11_0011':[7,7,6,5,6],
    '2013_12_11_0012':[6],
    '2013_12_11_0014':[8],
    '2013_12_11_0016':[8],
    '2013_12_11_0018':[9],
    '2013_12_11_0019':[8,7,5,7,7],
    '2013_12_11_0020':[7],
    '2013_12_11_0022':[8],
    '2013_12_11_0023':[2,2,2,2,1],
    '2013_12_11_0024':[8],
    '2013_12_11_0026':[10],
    '2013_12_11_0027':[5,4,5,4,4],
    '2013_12_11_0028':[8],
    '2013_12_11_0029':[3,3,3,3,3],
    '2013_12_11_0030':[7],
    '2013_12_11_0031':[6,7,7,7,7],
    '2013_12_11_0032':[7],
    '2013_12_11_0033':[3,4,5,4,4],
    '2013_12_11_0034':[9],
    '2013_12_11_0036':[9],
    '2013_12_11_0038':[9],
    '2013_12_11_0040':[9],
    '2013_12_11_0042':[8],
    '2013_12_11_0044':[8],
    '2013_12_11_0045':[6,6,5,6,5],
    '2013_12_11_0046':[7],
    '2013_12_11_0048':[9], #observe the 9 after nothing prior
    '2013_12_11_0049':[7,6,6,6,6],
    '2013_12_11_0050':[7],
    '2013_12_11_0166':[15],
    '2013_12_11_0170':[15],
    '2013_12_11_0178':[15],
    '2013_12_11_0186':[15],
    '2013_12_11_0189':[9,8,8,8,8],
    '2013_12_11_0195':[0,0,1,1,2],
    '2013_12_11_0196':[15],
    '2013_12_11_0197':[0,1,1,1,1],
    '2013_12_11_0200':[15],
    '2013_12_11_0202':[15],
    '2013_12_11_0204':[16],
    '2013_12_11_0207':[12,12,12,11,11],
    '2013_12_11_0208':[14],
}


def files_by_dist(files,dists,cid,endf):
    #all_files,dists=get_cell_traces(cid,abfpath)
    afd=[(file,dist) for file,dist in zip(files,dists)]
    #afd.sort(key=lambda tup: tup[1])
    fig=plt.figure(figsize=(20,20),frameon=False)
    for filepath,distance in afd:
        raw,block,segments,header=load_abf(filepath) #TODO fp segment dict like I had with queue/threading
        if len(segments)==1:
            continue
        for segment in segments:
            #for ass in segment.analogsignals:
            ass=segment.analogsignals[0]
            xs=np.linspace(0,.1,len(ass.times.base))+distance #center by distance
            #ys=(ass.base-np.min(ass.base))/(np.max(ass.base)-np.min(ass.base))-segment.index*1.5 #move down by segment number
            ys=(ass.base-np.mean(ass.base))/2.5+segment.index #move down by segment number
            plt.plot(xs[:len(xs)//14]*1000,ys[:len(ys)//14],'k-',label='%s'%distance)
    plt.ylim(-.2,5)
    plt.yticks(np.arange(0,5,1))
    plt.xlabel('Distance from cell body in $\mu$m. Normalized trial length')
    plt.ylabel('Amplitude and run number')
    plt.title('Example traces as a function of distance from cell %s'%cid)
    #fig.frameon(False)
    #fig.patch.set_visible(False)
    ax=fig.axes[0]
    ax.spines['left'].set_edgecolor((1,1,1,1))
    format_axes(ax)
    #embed()
    fig.savefig('/tmp/fd_%s_%s.png'%(cid,endf[-4:]),bbox_inches='tight',pad_inches=0)

def format_axes(ax,fontsize=50,ticksize=50):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    things=[ax.xaxis.label, ax.yaxis.label, ax.title]
    ticks=ax.get_xticklabels()+ax.get_yticklabels()
    [t.set_fontsize(fontsize) for t in things]
    [t.set_fontsize(ticksize) for t in ticks]

def do_files():
    abfpath=get_abf_path()
    cell_ids=36,37,41,43 #39, 40 no data
    end=[#filename, go back, std_thrs, std_max
        ('2013_12_10_0060', 58, 2.5, 5), #36 missing file 11 from the list due to weird bug #space=5
        ('2013_12_10_0118', 58, 2.5, 5), #37 4V #space =3
        ('2013_12_10_0176', 58, 2.5, 5), #37 4.1V #health failed
        ('2013_12_11_0000', 58, 3.0, 5), #41 3V
        ('2013_12_11_0058', 58, 3.0, 5), #41 0V
        ('2013_12_11_0127', 58, 3.3, 5), #43 3V
        ('2013_12_11_0208', 58, 2.5, 3.8), #43 0V, could go farther back and review the files around crash
    ]
    for cid in cell_ids:
        all_files,dists=get_cell_traces(cid,abfpath)
        cell=s.query(Cell).get(cid)
        files=cell.datafiles
        for endf,counts,std_thrs,std_max in end:
            try:
                indexes=get_n_before(counts,all_files,abfpath+endf+'.abf')
            except ValueError as e:
                continue
            fileset=np.array(all_files)[indexes]
            filenames=[f.split('/')[-1] for f in fileset]
            distset=np.array(dists)[indexes]
            #files_by_dist(fileset,distset,cid,endf)
            fig=plt.figure(figsize=(20,20))
            pos=np.array([ f.position for f in files if f.filename in filenames])
            slice_=cell.parent
            s_pos=np.array([d.value for d in get_metadata_query(Slice,slice_.id,'getPos').all()[:3]])
            print(s_pos)
            plt.plot(-pos[:,0]*1000,pos[:,1]*1000,'bo',color=(.8,.8,1),markersize=10)
            plt.plot(-s_pos[:,0]*1000,s_pos[:,1]*1000,'go',markersize=20)
            plt.plot(-cell.position[0]*1000,cell.position[1]*1000,'ro',markersize=20)
            plt.axis('equal')
            plt.xlabel('$\mu$m')
            plt.ylabel('$\mu$m')
            plt.title('Simulus positions and cortex surface for cell %s'%(cid))
            format_axes(fig.axes[0])
            plt.savefig('/tmp/positions_%s_%s'%(cid,endf[-4:]),bbox_inches='tight',pad_inches=0)




def main():
    #do_files()
    #return None
    import pickle
    try:
        spike_fn_dict=pickle.load(open('/tmp/led_spikes.p','rb'))
        stats_dict=pickle.load(open('/tmp/led_stats.p','rb'))
    except FileNotFoundError:
        abfpath=get_abf_path()
        cell_ids=36,37,41,43 #39, 40 no data
        end=[#filename, go back, std_thrs, std_max
            ('2013_12_10_0060', 58, 2.5, 5), #36 missing file 11 from the list due to weird bug #space=5
            ('2013_12_10_0118', 58, 2.5, 5), #37 4V #space =3
            ('2013_12_10_0176', 58, 2.5, 5), #37 4.1V #health failed
            ('2013_12_11_0000', 58, 3.0, 5), #41 3V
            ('2013_12_11_0058', 58, 3.0, 5), #41 0V
            ('2013_12_11_0127', 58, 3.3, 5), #43 3V
            ('2013_12_11_0208', 58, 2.5, 3.8), #43 0V, could go farther back and review the files around crash
        ]
        spike_fn_dict={}
        stats_dict={}
        for cid in cell_ids:
            all_files,dists=get_cell_traces(cid,abfpath)
            for endf,counts,std_thrs,std_max in end:
                try:
                    indexes=get_n_before(counts,all_files,abfpath+endf+'.abf')
                except ValueError as e:
                    continue
                fileset=np.array(all_files)[indexes]
                distset=np.array(dists)[indexes]
                #files_by_dist(fileset,distset,cid,endf)

                stats,sfnd=plot_abf_traces(fileset,distset,std_thrs=std_thrs,std_max=std_max,threshold_func=threshold_maker(abfpath,THRS_DICT),spikes=True,spike_func=make_spike_count_dict(abfpath,COUNT_DICT),cell_id=cid,do_plot=False)
                stats_dict['%s_%s'%(cid,endf[-4:])]=stats
                spike_fn_dict.update(sfnd)
        pickle.dump(spike_fn_dict, open('/tmp/led_spikes.p','wb'))
        pickle.dump(stats_dict, open('/tmp/led_stats.p','wb'))

    
    cid=37

    #cid=41
    abfpath=get_abf_path()
    all_files,dists=get_cell_traces(cid,abfpath)
    endf='2013_12_10_0118'
    std_thrs=2.5
    std_max=5
    indexes=get_n_before(58,all_files,abfpath+endf+'.abf')
    fileset=np.array(all_files)[indexes]
    distset=np.array(dists)[indexes]
    stats,sfnd=plot_abf_traces(fileset,distset,std_thrs=std_thrs,std_max=std_max,threshold_func=threshold_maker(abfpath,THRS_DICT),spikes=True,spike_func=make_spike_count_dict(abfpath,COUNT_DICT),cell_id=cid,do_plot=True)

    #cell_ids=16,26 #based on num files
    #cell_ids=32,34
    #cell_ids=37,#41,43
    #cell_ids=36,
    #cell_ids=41,

            #plot_abf_traces([abfpath+'2013_12_10_0188.abf',abfpath+'2013_12_10_0189.abf'],[0,0],std_thrs=std_thrs,std_max=std_max,threshold_func=threshold_maker(abfpath,THRS_DICT),spikes=True,cell_id=cid)
            #plot_abf_traces([abfpath+'2013_12_10_0216.abf',abfpath+'2013_12_10_0217.abf'],[0,0],std_thrs=std_thrs,std_max=std_max,threshold_func=threshold_maker(abfpath,THRS_DICT),spikes=True,cell_id=cid)

    def compile_all(stats_dict):
        all_base=[]
        all_spike=[]
        all_norm=[]
        for key,cont in stats_dict.items():
            all_base.extend(cont['base_dist_stats'])
            all_spike.extend(cont['spike_dist_stats'])
            all_norm.extend(cont['norm_dist_stats'])
        return all_base,all_spike,all_norm


    b,s,n=compile_all(stats_dict)
    b=np.array(b)
    s=np.array(s)
    n=np.array(n)
    ndists=n[:,0]
    nmeans=n[:,1]
    nstds=n[:,2]
    sdists=s[:,0]
    smeans=s[:,1]
    sstds=s[:,2]
    bdists=b[:,0]
    bmeans=b[:,1]
    bstds=b[:,2]

    fig=plt.figure(figsize=(20,20))
    nbins=bin_dists(ndists*1000,nmeans,nstds,25)
    plt.xlim(xmin=-2)
    plt.xticks(np.arange(0,225,25))
    #plt.ylim(ymax=2)
    plt.yticks(np.arange(0,1.25,.25))
    plt.title('Normalized spike count vs distance')#' (binned). Error is SEM.')
    plt.xlabel(r'Distance in $\mu$m')
    plt.ylabel('Normalized spike counts')
    format_axes(fig.axes[0],50,50)
    fig.savefig('/tmp/norm_dist_all.png',bbox_inches='tight',pad_inches=0)
    plt.clf()

    #fig=plt.figure(figsize=(20,20))
    plt.plot(ndists*1000,nmeans,'ko',markersize=20)
    plt.title('All spike counts vs distance')#' (binned). Error is SEM.')
    plt.xlabel(r'Distance in $\mu$m')
    plt.ylabel('Normalized spike counts')
    format_axes(fig.axes[0],50,50)
    fig.savefig('/tmp/population_normalized_counts.png',bbox_inches='tight',pad_inches=0)
    plt.clf()

    #fig=plt.figure(figsize=(20,20))
    sbins=bin_dists(sdists*1000,smeans,sstds,25)
    plt.xlim(xmin=-2)
    plt.xticks(np.arange(0,225,25))
    plt.yticks(np.arange(0,8,1))
    plt.title('Average spike count vs distance')#' (binned). Error is SEM.')
    plt.xlabel(r'Distance in $\mu$m')
    plt.ylabel('Average spike count')
    format_axes(fig.axes[0],50,50)
    fig.savefig('/tmp/spike_dist_all.png',bbox_inches='tight',pad_inches=0)
    plt.clf()

    bbins=bin_dists(bdists,bmeans,bstds)
    #embed()

    def get_lmes(bins):
        lefts=[]
        means=[]
        stds=[]
        sems=[]
        for left,means in bins.items():
            lefts.append(left)
            new_mean=np.mean(means)
            new_std=np.std(means)
            new_sem=new_std/len(means)
            means.append(new_mean)
            stds.append(new_std)
            sems.append(new_sem)
        return np.array(lefts),np.array(means),np.array(stds),np.array(sems)

    lefts,means,stds,sems=get_lmes(nbins)
    #plt.figure(figsize=(10,10))
    #plt.errorbar(lefts+12.5,means,sems,fmt='ko',ecolor=(.2,.2,.2))
    #plt.savefig('/tmp/test3.png')
    #useful="plt.figure();[ plt.errorbar(left+.0125,np.mean(lst[0]),np.std(lst[0])/np.sqrt(len(lst[0])) ) for left,lst in bins.items()];plt.xlim(-.1,.250);plt.savefig('/tmp/test2.png')"

    #embed()
        #data=get_cell_data(cid)
        #plot_cell_data(*data[:-1])
            #plt.show()



if __name__=='__main__':
    main()
