import numpy as np
import serial as ser
#import pydaqmx as da

#data structure, needs to be able to handle the states of the following


"""
A simpler version:

Don't bother with data acquasition for the time being
use any one of the python modules that can read abf/atf files
if I know how many indiviudal recordings I'm going to make for
and experiment then I can just see where the directory is now
and add pointers to those abf files that I can then read in as
numpy arrays when I need to do data analysis (also pyphys)

as far as data structure, in theory I have everything I need
unfortunately I do not currently have the ability to control the
LED with analog output

but I can record all the calibration and all the cell locations
and all the abf files and that is really all I need to produce
my histograms

can use neo py or something else to read the abf files
stimfit also might be of use, though we do have igor
"""



#should I have an experiment reference file or something?
#I could make this so it can handle arbitrary data and pair it with the conditions for the experiment, adf (arbirary data framework)
#my data will almost always be some number of channles captured at some frequency, for ephys it is 1-4, for imaging it is pix x pix
#but in that case the data is stored in a different format because of how ccds work and the best way to efficienty write/save it
#ephys data is small enough that I can look at a whole time serries at once
#need to keep the conditions so that I can discard bad data post hoc w/o worrying about it

"""
to/from the nidaq
4 analog inputs from the two axon boxes
6 analog outputs 4 to the two axon boxes, 2 to two potential leds
voltage range
encoding depth (nubumber of bits used to represent range)
capture frequency
possibly other stuff

to/from the 700b
ideally would like to read certain things from mcc for the 700b
and set them without having to fucking click shit
gain
capacetance
etc

from the newport
get positions of things
move to positions

from computer
date
time

manual input
slice number (make it easy to increment)
cell number (make it easy to increment) #this is complicated...
success?
internal
bath
drugs?

automated
experiment number for this cell
total experiments



"""


#dictionary? yeah, seems right; NO you DONT need to name EVERYTHING!!!! (in theory) but it is a good way to start thinking
#need to be able to have arbitary number of channles, and deal with concurrent patches, tie cells to channels
#hierarchical seems like it might be eaiser to manage since less asumptions at each level
#experiment dict {date:time.date(),time:time.time(),slice:int,numCells:int,numAI:int,numAO:int,data:dict} #this can lead to a whole lot of data duplication that may not be necessary...
#data dict {ai1:np.array int16,ai2
