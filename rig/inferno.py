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

        return None


    def DOALLTHETHINGS(hsToCellDict,csvPath): #FIXME eh, given the structure of this program, just stuff these in at init
        stuff=None
        writeFile(csvPath)
        print(csvPath,hsToCellDict)
        #FIXME may need a way to stop execution in the middle???
        return None

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

