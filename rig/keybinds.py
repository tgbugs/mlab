#Key bindings for rigcontroy.py
#to use this file simply import keyDicts
#or manually import only what you want even though
#makeModeDict is smart enough to discard anything that isn't installed

def rigDict():
    rigDict= {
        'mode':'rig',
        'keyFuncs':{
                    'esc':'esc',
                    'h':'help',
                    'q': #FIXME depricated???
                        {
                         'mccFuncs':{0:'cleanup'},
                         'clxFuncs':{1:'cleanup'},
                         'espFuncs':{2:'cleanup'},
                         'keyfuncs':{3:'esc'},
                        },

                    ':':'cmd',
                   },

        'clxFuncs':{
                    'r':('setMode','clx'),
                    'l':'load',
                   },

        'mccFuncs':{
                    '1':'allIeZ',
                    '2':'allVCnoHold',
                    '3':'allVChold_60',
                    '4':'allICnoHold',
                    '5':'testZtO_75',
                    '6':'testOtZ_75',
                    '7':'zeroVChold_60',
                    '8':'oneVChold_60',
                    #'a':'printMCCstate',
                    'c':('setMode','mcc'),
                    'y':'getState',
                   },

        'espFuncs':{
                    #'o':'readProgram',
                    'w':'move',
                    'a':'move',
                    's':'move',
                    'd':'move',
                    'p':'printMarks',
                    'e':'printError',
                    #'w':'printPosDict',
                    #'e':('setMode','esp'),
                    't':'getDisp', #FIXME Mod, Ctrl etc... :/
                    #'s':'setSpeedDef',
                    'g':'getPos',
                    'f':'gotoMark',
                    #'r':'read',
                    'z':'fakeMove',
                    'm':'mark',
                    '\'':'gotoMark',
                   },

        'datFuncs':{
                    'n':('setMode','new'),
                    #'o':'test',
                    #'d':('setMode','dat'),
                   },

        'trmFuncs':{
            'k':('setMode','trm'),
            #'i':'ipython',
            #':':'test' #this works, so not sure why command doesnt
            ':':'command',
            },
    }
    return rigDict


##Method to convert the static dicts into their equivalent functions at runtime

def clxDict():
    protPath='C:/tom_axon/' #FIXME this is hidden this needs to go somewhere else or be removed period
    programDict={
                 '1':protPath+'2ch_scope'+'.pro',
                 '2':protPath+'current_step_-100-1000'+'.pro',
                 '3':protPath+'pair_test_0-1'+'.pro',
                 '4':protPath+'pair_test_1-0'+'.pro',
                 '5':protPath+'protname'+'.pro',
                 '6':protPath+'protname'+'.pro',
                 '7':protPath+'protname'+'.pro',
                 '8':protPath+'protname'+'.pro',
                 '9':protPath+'led_test'+'.pro',
                 '0':protPath+'nidaq_sync_test'+'.pro',
                }
                 
    # the #! opperator works by calling the the 'funcName' of the outer key name
    clxDict={
             'mode':'clx',
             'clxFuncs':{
                         '#!':('readProgDict',(programDict,)),
                         'l':'load',
                         'g':'getStatus',
                         's':'startMembTest',
                        },
            }
    
    for key in programDict.keys():
        clxDict['clxFuncs'][key]=('load',key)

    return clxDict

def mccDict():
    mccDict={
        'mode':'mcc',
        'mccFuncs':{
                    'r':'reloadControl',
                    '1':'allIeZ',
                    '2':'allVCnoHold',
                    '3':'allVChold_60',
                    '4':'allICnoHold',
                    '5':'testZtO_75',
                    '6':'testOtZ_75',
                    '7':'zeroVChold_60',
                    '8':'oneVChold_60',
                    '0':['allIeZ','allVCnoHold','allVChold_60'],
                    '9':{'mccFuncs':{ #FIXME this is bloodly useless >_< replace w/ actual programatic control
                                     0:'allIeZ',
                                     2:'allICnoHold',
                                     4:'inpWait',
                                    },
                         'clxFuncs':{
                                     1:('load','0'),
                                     3:('load','1'),
                                    },
                        },
                    'y':'getState',
                   },
    }

    return mccDict

def datDict():
    datDict={
        'mode':'new',
        'datFuncs':
            {
                's':'newSlice',
                'c':'newCell',
                'e':'newExperiment',
            }
    }
    return datDict

def trmDict():
    trmDict={
        'mode':'trm',
        'trmFuncs':
            {
                'i':'openIPython',
                '1':'getString',
                '2':'getFloat',
                '3':'getInt',
                '4':'getBool',
                '5':'getKbdHit',
            },
    }
    return trmDict

def getDicts(locs): #in theory we would like to generate this automatically...
    from inspect import isfunction
    dictDict={}
    for name,locvar in locs.items():
        if isfunction(locvar):
            if name != 'getDicts':
                dict=locvar()
                dictDict[dict['mode']]=dict

    return dictDict

keyDicts=getDicts(locals()) #This mirrors modeDict

def checkDups(keyDicts):
    for mode,DICT in keyDicts.items():
        keys=[]
        [keys.extend(d.keys()) for d in DICT.values() if type(d) is dict]
        dups=[k for k in keys if keys.count(k) > 1]
        if dups:
            print(mode,'has duplicate key entries!',dups)

def main():
    checkDups(keyDicts)
    
if __name__ == '__main__':
    main()

all__=[
    'rigDict',
    'clxDict',
    'mccDict',
    'datDict'
]
