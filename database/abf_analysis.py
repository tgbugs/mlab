#!/usr/bin/env python3.3
import os
import numpy as np
from scipy import integrate #for quad or whatever
import pylab as plt
from neo import AxonIO

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

def find_rs_test(trace):
    baseline=np.mean(trace[0:n])
    start=0
    end=1000
    volts=5
    return start,end,volts

def compute_rs(trace,start,end,volts):
    Tau=R*C
    R=Tau/C
    C=Q/volts
    Q=integrate.quad(trace[start:end])
    return rs


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

def get_protocol_offsets(filepath):
    """ analyize a protocol file, or better yet get it from the abf? """
    pass

import struct
def struct_read(binary,format,offset=None):
    if offset is not None:
        binary.seek(offset)
    return struct.unpack(format, binary.read(struct.calcsize(format)))


def main():
    from sqlalchemy.orm import Session
    from database.table_logic import logic_StepEdge
    from database.engines import engine
    from database.models import Cell, DataFile
    from rig.ipython import embed
    session=Session(engine)
    logic_StepEdge(session)

    path=get_abf_path()
    #filenames=[f.filename for f in session.query(DataFile).all()]
    #filenames=[f.filename for f in session.query(Cell).get(66).datafiles]
    filenames= ['2013_12_13_0038.abf']
    filepaths = [path+filename for filename in filenames]

    for fp in filepaths:
        binary=open(fp,'rb')
        lines=binary.readlines()
        #l1=binary.readline() #399
        #print(len(l1))
        #l2=binary.readline() #4499?? yes
        #print(len(l2)) #5132
        #print(l2[4499:])

        try:
            raw,block,segments,header=load_abf(fp)
        except FileNotFoundError as e:
            print(e)
        print(header['sProtocolPath'])
        #plot_raw_aligned(block)
    embed()
    #plt.show()

    #TODO 2013_12_13_0038.abf for testing




if __name__ == '__main__':
    main()


