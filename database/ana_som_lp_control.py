from rig.ipython import embed
import socket
import numpy as np
#import scipy as sci
import pylab as plt
from neo import AxonIO, AnalogSignal

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

def load_abf(filepath):
    raw=AxonIO(filename=filepath)
    block=raw.read_block(lazy=False,cascade=True)
    segments=block.segments
    header=raw.read_header()
    return raw,block,segments,header

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


def detect_spikes(array,thresh=3,max_thresh=5,threshold=None): #FIXME need an actual threshold?
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
        threshold=avg+max_thresh

    space=5
    first=array[:-space] #5 to hopefully prevent the weirdness with tiny fluctuations
    second=array[space:]
    base=len(first)-space
    #s_list=[ i for i in range(base) if first[i]<=threshold and second[i]>threshold ]
    s_list=[ i for i in range(base-1) if first[i]<=threshold and second[i]>threshold and first[i+1]<=threshold and second[i+1]>threshold ]
    s_index=s_list[0::space] #take only the first spike
    return s_index

def detect_led(led_array):
    maxV=max(led_array.base)
    minV=min(led_array.base)
    if maxV-minV < .095:
        return [],base,maxV,minV
    half=maxV-(maxV-minV)/2
    led_on_index=np.where(led_array.base < half)[0]
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
]
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

def bin_dists(dist,mean,var,bin_width=.01): #FIXME return dont plot?
    bin_lefts=np.arange(0,.2,bin_width)
    bin_dict={}
    for v in bin_lefts:
        bin_dict[v]=[[],[]]
    for d,m,v in zip(dist,mean,var):
        left=bin_lefts[bin_lefts<=d][-1] #left inclusive
        right=left+bin_width
        bin_dict[left][0].append(m)
        bin_dict[left][1].append(v)
    for left_bin,lst in bin_dict.items():
        new_mean=np.mean(lst[0])
        new_std=np.std(lst[0]) #FIXME ignores the individual vars
        plt.bar(left_bin,new_mean,bin_width,color=(.8,.8,1),yerr=new_std)

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
            continue
        filepath=abfpath+filename #FIXME
        size=os.path.getsize(filepath)
        if size != 10009088 and size != 2009088: #FIXME another way to detect filetype really just need a way to get the protocol
            continue
        filepaths.append(abfpath+filename)
        dists.append(distance)
    return filepaths,dists

def plot_abf_traces(filepaths,dists,spikes=False): #FIXME this is for 58 alternating
    for filepath,distance in zip(filepaths,dists):
        raw,block,segments,header=load_abf(filepath)
        if list(raw.read_header()['nADCSamplingSeq'][:2]) != [1,2]: #FIXME
            print('Not a ledstim file')
            return None,None
        gains=header['fTelegraphAdditGain'] #TODO
        #TODO cell.headstage number?!
        headstage_number=1
        zero=transform_maker(0,20*gains[headstage_number]) #cell
        #one=transform_maker(0,5) #led
        one=transform_maker(0,10) #led no idea why the gain is different for these
        nseg=len(segments)
        if nseg!=1:
            plt.figure()
        for seg,n in zip(segments,range(nseg)):
            if nseg == 1:
                plt.subplot(6,1,6)
            else:
                plt.subplot(6,1,n+1)
            signal=zero(seg.analogsignals[0])
            led=one(seg.analogsignals[1])
            #signal=seg.analogsignals[0]
            #led=seg.analogsignals[1]
            led_on_index,base,maxV,minV=detect_led(led) #FIXME move this to count_spikes
            if not len(led_on_index):
                print('No led detected maxV: %s minV: %s'%(maxV,minV))
                continue
            sig_on=signal.base[led_on_index]
            sig_on_times=signal.times.base[led_on_index] #FIXME may not be synch?
            sig_mean=np.mean(sig_on)
            sig_std=np.std(sig_on)
            #plt.plot(sig_std+sig_mean)
            sm_arr=base*sig_mean
            sm_arr_times=signal.times.base[led_on_index]
            std_arr=base*sig_std
            
            #do spike detection
            if spikes:
                spike_indexes=detect_spikes(sig_on)
                spike_times=signal.times.base[led_on_index][spike_indexes]
                sc=len(spike_indexes)
                plt.plot(spike_times,sig_on[spike_indexes],'ro')
                plt.title('%s spikes %s um from cell %s'%(sc,int(distance*1000),block.file_origin))
            else:
                plt.title('%s um from cell %s'%(distance*1000,block.file_origin))

            plt.xlabel(signal.times.units)
            plt.ylabel(signal.units)

            #plt.xlabel(led.times.units)
            #plt.ylabel(led.units)
            #plt.plot(led.times.base[led_on_index],led.base[led_on_index])

            plt.plot(sig_on_times,sig_on,'k-')
            plt.plot(sm_arr_times,sm_arr,'b-')
            plt.fill_between(np.arange(len(sm_arr)),sm_arr-std_arr,sm_arr+std_arr,color=(.8,.8,1))
            plt.xlim((sig_on_times[0],sig_on_times[-1]))

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
    return np.arange(index-(n-2),index+1)

def get_abf_path():
    """ return the abf path for a given computer """
    if os.name=='posix':
        abfpath='/mnt/tgdata/clampex/'
    elif socket.gethostname()=='andromeda':
        abfpath='D:/clampex/'
    else:
        abfpath='D:/tom_data/clampex/'
    return abfpath

def notes():
    #_cell_endfile=review;threshold,max_above
    _36_0060=1,8,19,39,55;3,5

def main():
    abfpath=get_abf_path()
    #cell_ids=16,26 #based on num files
    #cell_ids=32,34
    #cell_ids=36,37,41,43 #39, 40 no data
    cell_ids=36,37,41,43
    end=[
        #'2013_12_10_0060', #36
        '2013_12_10_0118', #37 4V
        '2013_12_10_0176', #37 4.1V #health failed
        '2013_12_11_0000', #41 3V
        '2013_12_11_0058', #41 0V
        '2013_12_11_0127', #43 3V
        '2013_12_11_0208', #43 0V, could go farther back and review the files around crash
    ]
    for cid in cell_ids:
        all_files,dists=get_cell_traces(cid,abfpath)
        for endf in end:
            try:
                indexes=get_n_before(58,all_files,abfpath+endf+'.abf')
            except ValueError:
                continue
            print(indexes)
            plot_abf_traces(np.array(all_files)[indexes],np.array(dists)[indexes],spikes=True)
        #data=get_cell_data(cid)
        #plot_cell_data(*data[:-1])
            plt.show()



if __name__=='__main__':
    main()
