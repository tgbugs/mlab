from database.models import MetaDataSource, Experiment, Subject
#TODO what I need is a link between datasources and the Controller classes, that should probably be defined... here? or somewhere? or fuck what damn it one class per metadata source???!

def mdsAll(channels=4):
    """used to populate from an existing ExperimentType"""
    glob=globals()
    clsDict={}
    [clsDict.update({name:cls}) for name,cls in glob.items() if name[4:7]=='esp']
    [clsDict.update({name:cls}) for name,cls in glob.items() if name[4:7]=='trm']
    for channel in range(channels):
        mccs=[mccBindChan(glob[name],channel) for name in glob.keys() if name[5:8]=='mcc']
        for cls in mccs:
            clsDict[cls.__name__]=cls
    return clsDict


class _MDSource:
    @property
    def name(self):
        return self.__class__.__name__[4:]
    prefix=None
    unit=None
    mantissa=None #FIXME mantissa should be rounded not truncated, make sure this is implemented

    def __init__(self,Controller,session):
        if Controller.__class__.__name__==self.ctrl_name:
            self.ctrl=Controller
        else:
            raise TypeError('Wrong controller for this metadata source!')
        
        self.session=session #FIXME is it better to create a new session every time or better to just leave one open? read up

        try:
            self.MetaDataSource=self.session.query(MetaDataSource).filter_by(name=self.name)[0]
        except IndexError:
            self.Persist()

    def Persist(self):
        self.MetaDataSource=MetaDataSource(name=self.name,prefix=self.prefix,unit=self.unit,mantissa=self.mantissa)
        self.session.add(self.MetaDataSource)
        self.session.commit()

    def record(self,Parent):
        value=self.getCurrentValue()
        abs_error=self.getAbsError()
        #Parent.metadata_.append(Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error)) #alternate form
        self.currentRecord=Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error)
        #FIXME is currentRecord a sufficient safety net?? could aways just get the data again...
        #probably shouldn't worry TOO much about all these crazy failure cases
        self.session.add(self.currentRecord)
        #commit at the end?
        #FIXME should this be forced to commit previous values before adding a new one? well the session has it now...

    def getCurrentValue(self):
        #FIXME somehow I think I need a way to hold this until everything is collect before I commit? or should I just commit?
        return None

    def getAbsError(self):
        #TODO this is where online analysis based on calibration should go??? well we also need that somewhere else too...
        return None

###-----------------------------------------------------------------------------------
###  trm metadata sources BEWARE!! ALL trm inputs at the moment are MASSIVELY blocking
###-----------------------------------------------------------------------------------

class MDS_trmZ(_MDSource):
    """objective height reading for an object""" #TODO figur out how to record surface Z...
    prefix='u'
    unit='m'
    ctrl_name='trmControl' #this is the equivalent of key.py keyControl, but obviously is just return input()
    #ofc with special checks to make sure the datatype is correct ie float
    def getCurrentValue(self):
        return self.ctrl.getFloatInput()


class MDS_trmSlicesOut(_MDSource): #FIXME this feels like a hack :/
    """objective height reading for an object""" #TODO figur out how to record surface Z...
    prefix=''
    unit='time'
    ctrl_name='trmControl' #this is the equivalent of key.py keyControl, but obviously is just return input()
    #ofc with special checks to make sure the datatype is correct ie float
    def getCurrentValue(self):
        return None

###----------------------
###  esp metadata sources
###----------------------

def espAll():
    """returns a dict of all esp metadata source classes"""
    glob=globals()
    espDict={}
    [espDict.update({name:cls}) for name,cls in glob.items() if name[4:7]=='esp'] #TODO profile this
    #for cls in classes:
        #espDict[cls.__name__]=cls
    return espDict


class MDS_espX(_MDSource):
    prefix='m'
    unit='m'
    mantissa=5
    ctrl_name='espControl'
    def getCurrentValue(self):
        return self.ctrl.getX()


class MDS_espY(_MDSource):
    prefix='m'
    unit='m'
    mantissa=5
    ctrl_name='espControl'
    def getCurrentValue(self):
        return self.ctrl.getY()

###----------------------
###  mcc metadata sources
###----------------------

def mccBindChan(MDS_mcc,channel): #FIXME this does not work becasue it modifies the base class instead of adding a new one...
    #FIXME these names are really freeking hard to identify/remember which is why we do it by source instead of all the individual names
    #this it might be better to have full names based on which function they implement from mcc?
    out=type(MDS_mcc.__name__[1:]+str(channel),
             (MDS_mcc,),
             {'channel':channel}
            )
    return out

def mccBindAll(channel):
    """method for binding all mcc state mdses to the same channel at once"""
    glob=globals()
    classes=[mccBindChan(glob[name],channel) for name in glob.keys() if name[5:8]=='mcc']
    mccDict={}
    for cls in classes:
        mccDict[cls.__name__]=cls
    return mccDict



class _mccBase(_MDSource):
    ctrl_name='mccControl'
    def __init__(self,Controller,session):
        try:
            self.channel
            super().__init__(Controller,session)
        except:
            raise #AttributeError('%s requires a channel, use mccBindChan'%self.__class__.__name__)
    def record(self,Parent):
        self.ctrl.selectMC(self.channel) #FIXME make sure this mapping is static plox, if I have two mccs...
        super().record(Parent)


class _MDS_mccHE(_mccBase):
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetHoldingEnable()


class _MDS_mccH(_mccBase):
    prefix=''
    unit='V'
    mantissa=3
    def getCurrentValue(self):
        return self.ctrl.GetHolding()


class _MDS_mccPS(_mccBase):
    """primary signal numerical identifier"""
    prefix=''
    unit='num' #FIXME storing these codes is going to be really really confusing
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignal()


class _MDS_mccPSG(_mccBase):
    """Gain for primary signal"""
    prefix=''
    unit='num'
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignalGain()


class _MDS_mccPSLPF(_mccBase):
    """Low pass filter for primary signal"""
    prefix=''
    unit='Hz'
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignalLPF()


class _MDS_mccPO(_mccBase):
    """Pipette offset"""
    prefix=''
    unit='V'
    mantissa=5
    def getCurrentValue(self):
        return self.ctrl.GetPipetteOffset()


class _MDS_mccFCC(_mccBase):
    """Fast Comp Cap"""
    prefix=''
    unit='F'
    #no mantissa here since not sure if mcc uses the full float in amplifier
    def getCurrentValue(self):
        return self.ctrl.GetFastCompCap()


class _MDS_mccSCC(_mccBase):
    """Slow Comp Cap"""
    prefix=''
    unit='F'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompCap()


class _MDS_mccFCT(_mccBase):
    """Fast Comp Tau"""
    prefix=''
    unit='s'
    def getCurrentValue(self):
        return self.ctrl.GetFastCompCap()


class _MDS_mccSCT(_mccBase):
    """Slow Comp Tau"""
    prefix=''
    unit='s'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompTau()


class _MDS_mccSCTE(_mccBase):
    """Slow Comp Tau X20 enable"""
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompTauX20Enable()


class _MDS_mccBBE(_mccBase):
    """Bridge balance enable"""
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetBridgeBalEnable()


class _MDS_mccBBR(_mccBase):
    """Bridge balance resistance"""
    prefix=''
    unit='R'
    def getCurrentValue(self):
        return self.ctrl.GetBridgeBalResist()



def _main():
    from rig.esp import espControl
    from rig.mcc import mccControl
    from database.main import sqliteEng,initDBScience,populateConstraints,Experiment
    from database.TESTS import t_experiment
    engine=sqliteEng(False)
    session=initDBScience(engine)
    populateConstraints(session)
    e=t_experiment(session,2,2)
    exp=e.records[0]

    esp=espControl()
    mcc=mccControl()

    ex=MDS_espX(esp,session)
    mccHE_0=mccBindChan(_MDS_mccHE,0)
    mccHE_1=mccBindChan(_MDS_mccHE,1)
    print(mccHE_0.channel)
    print(mccHE_1.channel)
    mccHEz=mccHE_0(mcc,session)
    mccHEo=mccHE_1(mcc,session)
    print(ex.name)
    ex.record(exp)
    print(mccHEz.name)
    print(mccHEo.name)
    mccHEz.record(exp)
    [mccHEo.record(exp) for i in range(100)]
    [mccHEo.record(e.records[1]) for i in range(100)]
    session.commit()
    emd=session.query(Experiment.MetaData)
    #print(emd.all())
    print(e.records[0].metadata_)
    print(e.records[1].metadata_)

    return ex

def main():
    from rig.esp import espControl
    from rig.mcc import mccControl
    from database.main import sqliteEng,initDBScience,populateConstraints,Experiment
    from database.TESTS import t_experiment
    engine=sqliteEng(False)
    session=initDBScience(engine)
    populateConstraints(session)
    e=t_experiment(session,5,5)
    exp0=e.records[0]
    exp1=e.records[1]

    ctrlDict={
        espControl.__name__:espControl(),
        mccControl.__name__:mccControl()
    }

    mc0=mccBindAll(0)
    mc1=mccBindAll(1)

    imc0=[c(ctrlDict[c.ctrl_name],session) for c in mc0.values()]
    imc1=[c(ctrlDict[c.ctrl_name],session) for c in mc1.values()]

    [c.record(exp0) for c in imc0]
    [c.record(exp0) for c in imc1]
    [c.record(exp1) for c in imc0]
    [c.record(exp1) for c in imc1]

    session.commit()

    print(exp0.metadata_)
    print(exp1.metadata_)

if __name__=='__main__':
    main()

