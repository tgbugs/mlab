#!/usr/bin/env python3.3
""" For Dante
Usage:
    inferno.py <HS1_id> <HS2_id> <HS3_id> <HS4_id> [ --filepath=<path> ]
    inferno.py -h | --help
Options:
    -h --help                   print this
    -f --filepath=<path>        set which csv file to write to, IF NONE IT WILL USE HARDCODED FILE
"""


#may not even need rigioman if we can just load in clx and mcc dll handlers from a script, all we need is the filename and the cell ids

from docopt import docopt
args=docopt(__doc__) #do this early to prevent all the lags
print(args)

import numpy as np
from rig.clx import clxControl
from rig.mcc import mccControl
from rig.functions import clxFuncs,mccFuncs

#todo all multiclamps

class danteFuncs(clxFuncs,mccFuncs):
    def __init__(self,clx,mcc,csvFile,hsToCellDict):
        """ Some voodoo to get everything up and running without fixing other code """
        class modestate:
            """ hack to make kCtrlObj not a kCtrlObj """
            charBuffer=None
            setMode=lambda:None
            keyThread=None
            releaseKeyRequest=lambda:None

        super().__init__(modestate,clx=clx,mcc=mcc)
        self.csvFile=csvFile
        self.hsToCellDict=hsToCellDict

    ###
    ### Put your functions below! see rig/functions.py for reference specifically mccFuncs and clxFuncs
    ###

    def writeFile(stuff):
        ''' This is the function that writes the data we got to file '''
        #TODO format for this

        #write to binary file, full mcc states, functions to get that back out to a csv

        return None

    def click_protocol_button(self,button=None):
        #window name is 'Clampex - some shit'
        #gonna have to enum windows
        for i,n in get_windows():
            if n.count('Clampex'):
                name=n
                break
        #get the window position

        #604,8
        #y position of the row 148
        #x width of buttons 656-683
        #8 buttons starting at 670
        #3 at 910
        #3 at 1005
        #3 at 1100


        pass

    def click_record(self):

        #604,8 -> 953,76
        #left and top
        pass




    def DOALLTHETHINGS(hsToCellDict,csvPath): #FIXME eh, given the structure of this program, just stuff these in at init
        stuff=None
        writeFile(csvPath)
        print(csvPath,hsToCellDict)
        #FIXME may need a way to stop execution in the middle???


        #set the mode for each headstage NOTHING ELSE
        #load protocol <- use the mouse click
        #wait for key input or cancel
        #record mcc state, protocol, and cell asociations
        #run protocol <- use the mouse click
        #get the new filename
        #print text to terminal

        hsdict={
            'labels'=['gen from output format?']
            1={'cell id':'aa',}
        }
        return None

#output format

#filename format YYYY_MM_DD_nnnn
#protocol p1 p2 p3 p4 corrisponding to the buttons

#nnnn   p1
#headstage  1   2   3   4
#cell id    a   b   c   d 
#mode       vc  ic  vc  ic #map between mcc + channel and the digitizer input channel
#holding    -70 OFF OFF -70 #OFF for holding disabled
#bridge balance

#structure for associating protocols to mcc settings

def main():
    #define our constants
    clxDllPath=''
    mccDllPath=''

    #set variables from the command line
    csvPath=args['--filepath']
    hsToCellDict={ #FIXME somehow this seems redundant...
        1:args['<HS1_id>'],
        2:args['<HS2_id>'],
        3:args['<HS3_id>'],
        4:args['<HS4_id>'],
    }

    #make sure headstage numbers line up correctly!

    #initialize the controllers and the 
    clx=clxControl(clxDllPath)
    mcc=mccControl(mccDllPath)

    #create an instance of danteFuncs using the controllers, csvFile, and 
    fucntions=danteFuncs(clx,mcc,csvFile,hsToCellDict)

    #run the protocol
    functions.DOALLTHETHIGNS()




if __name__ == '__main__':
    main()

