""" This is the config file for the rig, it contains functions that set
    sane defaults for different bits of the rig, at some point this may be
    converted so that those defaults can be saved in the database, but that
    may not really matter since these measures will be taken elsewhere too

    This file will be used by rigIO during init so it is fine to call stuff directly
"""

clx_defaults={
                'protocolPath':{
                    'HILL_RIG':'C:/tom_axon',
                               },
             }


mcc_defaults={ 
                'VC_Holding':-.06,
                'VC_HoldingEnable':0,
                'VC_PrimarySignal':0,
                'VC_PrimarySignalGain':1,
                'VC_PrimarySignalLPF':2000,

                'IC_Holding':0,
                'IC_HoldingEnable':0,
                'IC_PrimarySignal':7,
                'IC_PrimarySignalGain':1,
                'IC_PrimarySignalLPF':2000,
             }
    

esp_defaults={
                'Speed':(1,.1),
                'FeLim':8,
                #TODO 'kp kd, or ki needed to fix felim nonsense'
                'MotorOn':0,
             }

#TODO move the functions themselves into their own file?

def mcc(ctrl):
    mcc_mode_dict={'VC':0,'IC':2}
    for channel in range(ctrl.mcNum):
        ctrl.selectMC(channel)
        for key,value in mcc_defaults.items():
            ctrl.SetMode(mcc_mode_dict[key[:2]])
            getattr(ctrl,'Set'+key[3:])(value)


def esp(ctrl):
    for key,value in esp_defaults.items(): #FIXME some of these things do need state tracking...
        if hasattr(value,'__iter__'):
            getattr(ctrl,'set'+key)(*value)
        else:
            getattr(ctrl,'set'+key)(value)


def set_all_defaults(rigio):
    #mcc(rigio.ctrlDict['mccControl']) #FIXME WARNING DANGEROUS!!! on a crash this could fry cells!
    esp(rigio.ctrlDict['espControl'])
