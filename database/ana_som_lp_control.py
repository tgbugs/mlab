from rig.ipython import embed
import numpy as np
import scipy as sci
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
    return raw,block,segments

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

image_path='D:/tom_data/macroscope/'
path='D:/tom_data/clampex/'
filenames=[
    #'2013_12_04_0024.abf',
    '2013_12_04_0025.abf',
    #'2013_12_04_0026.abf',
]

sig_map={0:set_gain_and_time_func(20,True),1:set_gain_and_time_func(1,True)}
sig_map_nt={0:set_gain_and_time_func(20,False),1:set_gain_and_time_func(1,False)} #FIXME why is the time doubled?

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


#zero=transform_maker(fADC_DO_0,fADC_DA_0,fDAC_scale_0)
#zero=transform_maker(4.2741,24.7521*20)
#one=transform_maker(2.1144,4.2731)#9.5017)
#one=transform_maker(fADC_DO_1,fADC_DA_1)#,fDAC_scale_1)
#one=transform_maker(-16.9,1)

zero=transform_maker(0,400)
one=transform_maker(0,5) #FIXME why do I need this!?
test_map={0:zero,1:one}

#[plot_abf(path+fn,sig_map_nt) for fn in filenames]
[plot_abf(path+fn,test_map) for fn in filenames]

raw,block,segments=load_abf(path+filenames[0])

#plt.show()
#embed()

def count_spikes(filepath,signal_map): #TODO
    raw,block,segments=load_abf(filepath)
    nseg=len(segments)
    zero=transform_maker(0,400) #cell
    one=transform_maker(0,5) #led
    for seg,n in zip(segments,range(nseg)):
        plt.figure()
        plt.title(block.file_origin)
        #plt.title('%s Segment %s'%(block.file_origin,n))
        nas=seg.size()['analogsignals']
        signal=zero(seg.analogsignals[0])
        led=one(seg.analogsignals[1])
        led_on_index=np.where(led.base < led.base[0]-.05)[0]
        base=np.ones_like(led_on_index)
        sig_on=signal.base[led_on_index]
        sig_mean=np.mean(sig_on)
        sig_std=np.std(sig_on)
        plt.plot(sig_on)
        #plt.plot(sig_std+sig_mean)
        sm_arr=base*sig_mean
        plt.plot(sm_arr)
        plt.fill_between(sm_arr,sm_arr-(base*sig_std),sm_arr+(base*sig_std))

count_spikes(path+filenames[0],None)
plt.show()

def get_disp(origin,target):
    a2=(origin[0]-target[0])**2
    b2=(origin[1]-target[1])**2
    return (a2+b2)**.5

sqrt2=get_disp([0,0],[1,1])
print('This should be square root of 2',sqrt2)
sqrt2=get_disp([0,0],[-1,-1])
print('And so should this!',sqrt2)


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

def run_stuff():
    cell_ids=16,26 #based on num files
    DFMD=DataFile.MetaData
    for cid in cell_ids:
        cell=s.query(Cell).get(cid)
        cell_pos=s.query(Cell.MetaData).filter_by(parent_id=cid).\
            join(MetaDataSource,Cell.MetaData.metadatasource).\
            filter_by(name='getPos').order_by(Cell.MetaData.id).first().value
        #print(cell_pos)
        #TODO get slice points
        slice_=cell.parent
        s_pos=get_metadata_query(Slice,slice_.id,'getPos').all()[:3]
        #print(s_pos)
        files=s.query(DataFile).join(Cell,DataFile.subjects).filter(Cell.id==cid).order_by(DataFile.creationDateTime).all()
        positions=[]
        for file in files:
            filepath=file.full_url[8:]
            try:
                file_pos=s.query(DFMD).filter(DFMD.url==file.url,DFMD.filename==file.filename).\
                    join(MetaDataSource,Cell.MetaData.metadatasource).\
                    filter_by(name='getPos').order_by(Cell.MetaData.dateTime).first().value
                print(filepath)
            except:
                print('%s does not have a position! Assuming the previous file position'%filepath)
            print(file_pos)
            positions.append(file_pos)
            print(get_disp(cell_pos,file_pos))
            size=os.path.getsize(filepath)
            print(size)
            #spike_count=count_spikes(filepath,None) #TODO OH NOSE MEMORY USAGE
        pos=np.array(positions)
        plt.figure()
        plt.title('Cell %s'%cid)
        plt.plot(esp_fix_x(pos[:,0]),pos[:,1],'bo') #TODO these are flipped from reality!
        plt.plot(esp_fix_x(cell_pos[0]),cell_pos[1],'ro')
        [plt.plot(esp_fix_x(p.value[0]),p.value[1],'go') for p in s_pos] #plot the slice positions

#run_stuff()


plt.show()






