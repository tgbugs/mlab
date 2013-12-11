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
    protoPath='C:/tom_axon/' #FIXME this is hidden this needs to go somewhere else or be removed period
    programDict={
                 #'1':protPath+'2ch_scope'+'.pro',
                 '1':'1_led_loose_patch'+'.pro',
                 '2':'1_scope'+'.pro',
                 '3':'current_step_-100-1000'+'.pro',
                 '4':'pair_test_0-1'+'.pro',
                 '5':'pair_test_1-0'+'.pro',
                 '6':'protname'+'.pro',
                 '7':'protname'+'.pro',
                 '8':'protname'+'.pro',
                 '9':'led_test'+'.pro',
                 #'0':protPath+'nidaq_sync_test'+'.pro',
                }
                 
    # the #! opperator works by calling the the 'funcName' of the outer key name
    clxDict={
             'mode':'clx',
             'clxFuncs':{
                         '#!1':('setProtocolPath',(protoPath,)), #FIXME massive hack as usual
                         '#!2':('readProgDict',(programDict,)),
                         #'l':'load',
                         #'r':'record',
                         #'r':'getSub_record',
                         #'v':'view', #FIXME try not to have things overlap >_<
                         'g':'getStatus',
                         's':'stop_rec',
                         #'m':'startMembTest',
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
                    '0':'allIeZ', #FIXME make this generalize by allow a list of the headstages!
                    'n':'allVCnoHold',
                    #'3':'allVChold_60',
                    #'4':'allICnoHold',
                    #'5':'testZtO_75',
                    #'6':'testOtZ_75',
                    #'7':'zeroVChold_60',
                    #'8':'oneVChold_60',
                    #'0':['allIeZ','allVCnoHold','allVChold_60'],
#get WHOLE cell steps 
                    'a':'autoOffset',
                    'g':{#FIXME need a check to prevent running when cells are already gotten, but that requires the steps to work, cant do it with this setup :/
                         #FIXME also need a way to auto switch to next headstage if one is already occupied otherwise we will cook shit :(
                         'mccFuncs':{
                             #-1:'new', #TODO checkpoints so that we dont go when when have a cell #TODO headstage <-> cell linkage can happen here naturally
                             0:'setVCholdOFF',
                             1:('setVChold',-.06),  #FIXME HUGE PROBLEM the 2nd headstage to be set somehow goes to -1000mV this happens because the program hits the end of the pipette offset and so it wraps around
                             2:'autoOffset',
                             3:'autoCap',
                             5:'setVCholdON',
                         },
                         'trmFuncs':{
                             -1:'getDistance_um',
                             4:('getKbdHit','hit a key when you bump a cell'), #FIXME move to datFuncs? well it is trying to be a step but >_<
                         },
                         'espFuncs':{-2:'getWT_getPos'},
                         'datFuncs':{
                             -3:'newCell',
                             6:'getBrokenIn', #TODO FIXME getDoneFailNB?
                         },
                    },
#current steps
                    'c':{ 
                         'mccFuncs':{0:'allICnoHold',4:'allIeZ'}, #FIXME need a check that we arent running
                         'clxFuncs':{
                            1:('loadfile','current_step_-100-1000'+'.pro'),
                            2:'getSub_record',
                            3:'wait_till_done',
                         },
                         #'trmFuncs':{3:''},
                    },
#check connected pairs
                    'p':{
                         'mccFuncs':{
                             0:('testZtO',-.075), #excitation
                             5:('testZtO',-.05), #inhibition
                             8:('testOtZ',-.075), #excitation
                             13:('testOtZ',-.05), #inhibition
                             16:'allIeZ',
                         },
                         'clxFuncs':{
                             1:('loadfile','pair_test_0-1'+'.pro'), #FIXME zero-to-one
                             3:'getSub_record',
                             4:'wait_till_done',
                             6:'getSub_record',
                             7:'wait_till_done',
                             9:('loadfile','pair_test_1-0'+'.pro'), #FIXME one-to-zero
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
#run the optogenetic stimulation!
                    #'s':{},

                    'asdf':{'mccFuncs':{ #FIXME this is bloodly useless >_< replace w/ actual programatic control
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
    #mccDict['mccFuncs']['l']=None
    def make_led_dict(step_um,number): #FIXME it is monumentally stupid to have to compile this only at startup >_<
        led_dict={}
        led_dict['espFuncs']={}
        led_dict['mccFuncs']={1:('setGain',10),0:'allIeZ'}
        led_dict['clxFuncs']={}
        base_steps={
            'clxFuncs':{
                1:('loadfile','1_led_loose_patch'+'.pro'),
                6:('loadfile','1_led_loose_cell'+'.pro'),
                2:'getSub_record',
                3:'wait_till_done',
                7:'getSub_record',
                8:'wait_till_done',
                       },
            'espFuncs':{
                0:'moveNext',
                4:'getWT_getPos',
                5:'moveNext',
                9:'getWT_getPos',
            },
        }
        start=2 #FIXME generalize it instead of hardcoding
        nsteps=10 # zero to nine
        check={}
        for i in range(number*4-3): #the -3 accounts for the fact that 3 of the 4 origins are are left out
            loop_start=i*nsteps+start
            for func_name,dodict in base_steps.items():
                #print(func_name)
                for step_number,thing in dodict.items():
                    #print('\t',thing)
                    led_dict[func_name][step_number+loop_start]=thing
                    check[step_number+loop_start]=thing
        #print(check)
        #print(led_dict)
        return led_dict
    step_um=25
    number=8 #XXX note that you need step_um * dist-1 to get to max dist here because zero counts as a stop
    mccDict['espFuncs']={'m':('mark_to_cardinal',step_um,number)} #this means we need to multipy by number by 4 each position-origin pair should be accounted for
    mccDict['mccFuncs']['l']=make_led_dict(step_um,number)

    def make_som_dict(step_um,number): #TODO
        return {}
    step_um=100
    number=10
    mccDict['mccFuncs']['d']=make_som_dict(step_um,number)
    mccDict['espFuncs'].update({'s':('mark_to_spline',step_um,number)}) #*2 for left and right traversal


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
            'c':'endCell', 
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
