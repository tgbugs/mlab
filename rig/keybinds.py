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
                   },

        'clxFuncs':{
                    'r':('setMode','clx'),
                    #'l':'load',
                   },

        'mccFuncs':{
                    #'1':'allIeZ',
                    #'2':'allVCnoHold',
                    #'3':'allVChold_60',
                    #'4':'allICnoHold',
                    #'5':'testZtO_75',
                    #'6':'testOtZ_75',
                    #'7':'zeroVChold_60',
                    #'8':'oneVChold_60',
                    #'a':'printMCCstate',
                    'c':('setMode','mcc'),
                    'y':'getState',
                   },

        'espFuncs':{
                    #'o':'readProgram',
                    'o':'motorToggle',
                    'w':'move',
                    'a':'move',
                    's':'move',
                    'd':'move',
                    'W':'move',
                    'A':'move',
                    'S':'move',
                    'D':'move',
                    'v':'moveNext',
                    'M':'printMarks',
                    'p':'getPos___',
                    'x':'printError',
                    #'w':'printPosDict',
                    #'e':('setMode','esp'),
                    'I':'showDisp', #FIXME Mod, Ctrl etc... :/
                    #'s':'setSpeedDef',
                    'g':'getPos',
                    'G':'getWT_getPos', #FIXME some subjects dont move?
                    'f':'gotoMark',
                    '\'':'gotoMark',
                    #'r':'read',
                    'z':'fakeMove',
                    'm':'mark',
                    'l':'mark_to_movelist',
                   },

        'datFuncs':{
                    't':'print_write_target',
                    'T':'setWriteTargets',
                    'P':'printAll',
                    'n':('setMode','new'),
                    'e':('setMode','end'),
                    #'o':'test',
                    #'d':('setMode','dat'),
                   },

        'trmFuncs':{
            'k':('setMode','trm'),
            'U':'getWT_getDistance_um',
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
                 #'1':protPath+'2ch_scope'+'.pro',
                 '1':protPath+'1_led_loose_patch'+'.pro',
                 '2':protPath+'1_scope'+'.pro',
                 '3':protPath+'current_step_-100-1000'+'.pro',
                 '4':protPath+'pair_test_0-1'+'.pro',
                 '5':protPath+'pair_test_1-0'+'.pro',
                 '6':protPath+'protname'+'.pro',
                 '7':protPath+'protname'+'.pro',
                 '8':protPath+'protname'+'.pro',
                 '9':protPath+'led_test'+'.pro',
                 #'0':protPath+'nidaq_sync_test'+'.pro',
                }
                 
    # the #! opperator works by calling the the 'funcName' of the outer key name
    clxDict={
             'mode':'clx',
             'clxFuncs':{
                         '#!':('readProgDict',(programDict,)),
                         #'l':'load',
                         #'r':'record',
                         #'r':'getSub_record',
                         'v':'view',
                         'g':'getStatus',
                         's':'stop_rec',
                         'm':'startMembTest',
                         ' ':{'clxFuncs':{0:'getSub_record'},
                              'espFuncs':{1:'getWT_getPos'},
                         }
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
                    '1':'set_hs0',
                    '2':'set_hs1',
                    #'3':'set_hsAll',
                    '0':'allIeZ',
                    #'2':'allVCnoHold',
                    #'3':'allVChold_60',
                    '4':'allICnoHold',
                    '5':'testZtO_75',
                    '6':'testOtZ_75',
                    '7':'zeroVChold_60',
                    '8':'oneVChold_60',
                    #'0':['allIeZ','allVCnoHold','allVChold_60'],

                    'g':{ #get cell steps #FIXME need a check to prevent running when cells are already gotten, but that requires the steps to work, cant do it with this setup :/
                         #FIXME also need a way to auto switch to next headstage if one is already occupied otherwise we will cook shit :(
                         'mccFuncs':{
                             0:('setVChold',-.06), 
                             1:'setVCholdOFF',
                             2:'autoOffset',
                             3:'autoCap',
                             5:'setVCholdON',
                         },
                         'trmFuncs':{
                             4:('getKbdHit','hit a key when you bump a cell'), #FIXME move to datFuncs? well it is trying to be a step but >_<
                         },
                         'datFuncs':{
                             6:'getBrokenIn', #TODO FIXME getDoneFailNB?
                         },
                    },

                    'c':{ #current steps
                         'mccFuncs':{0:'allICnoHold',3:'allIeZ'},
                         'clxFuncs':{
                            1:('load','3'), #FIXME naming
                            2:'getSub_record',
                         },
                         'trmFuncs':{3:''},
                    },

                    'p':{ #check connected pairs
                         'mccFuncs':{
                             0:('testZtO',-.075),
                             5:('testZtO',-.06),
                             8:('testOtZ',-.075),
                             13:('testOtZ',-.06),
                             16:'allIeZ',
                         },
                         'clxFuncs':{
                             1:('load','4'), #FIXME zero-to-one
                             3:'getSub_record',
                             4:'wait_till_done',
                             6:'getSub_record',
                             7:'wait_till_done',
                             9:('load','5'), #FIXME one-to-zero
                             11:'getSub_record',
                             12:'wait_till_done',
                             14:'getSub_record',
                             15:'wait_till_done',
                         },
                         'trmFuncs':{
                             2:('getKbdHit','Hit a key after adjusting the program so that the cell will spike'),
                             10:('getKbdHit','Hit a key after adjusting the program so that the cell will spike'),
                         },
                    },

                    '9':{'mccFuncs':{ #FIXME this is bloodly useless >_< replace w/ actual programatic control
                                     0:'allIeZ',
                                     3:'allICnoHold',
                                    },
                         'clxFuncs':{
                                     1:('load','1'),
                                     2:'record',
                                     4:('load','2'),
                                     5:'record',
                                    10:'stop_rec',
                                    },
                         'trmFuncs':{
                                     9:'getKbdHit',
                                    }
                        },
                    'y':'getState',
                   },
    }

    return mccDict

def newDict():
    datDict={
        'mode':'new',
        'datFuncs':
            {
                'n':'newNote',
                's':'newSlice',
                'c':'newCell',
                'e':'newExperiment',
                'p':'printAll',
            },
    }
    return datDict

def endDict():
    datDict={
        'mode':'end',
        'datFuncs':
        {
            's':'endSlice',
            'c':'endCells',
            'e':'endExperiment',
            'p':'printAll',
            'd':'endDataFile',
            'n':('setMode','new'),
        },
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
                'u':'getWT_getDistance_um',
            },
    }
    return trmDict

def checkDups(keyDicts):
    for mode,DICT in keyDicts.items():
        keys=[]
        [keys.extend(d.keys()) for d in DICT.values() if type(d) is dict]
        dups=[k for k in keys if keys.count(k) > 1]
        if dups:
            print('[!]',mode,'has duplicate key entries!',dups)

def getDicts(locs): #in theory we would like to generate this automatically...
    from inspect import isfunction
    dictDict={}
    for name,locvar in locs.items():
        if isfunction(locvar):
            if name not in {'getDicts','checkDups'}:
                dict=locvar()
                dictDict[dict['mode']]=dict

    checkDups(dictDict)
    return dictDict

keyDicts=getDicts(locals()) #This mirrors modeDict

def main():
    pass
    
if __name__ == '__main__':
    main()

all__=[
    'rigDict',
    'clxDict',
    'mccDict',
    'datDict'
]
