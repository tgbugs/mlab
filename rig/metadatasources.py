from database.models import MetaDataSource, Experiment, Subject
#TODO what I need is a link between datasources and the Controller classes, that should probably be defined... here? or somewhere? or fuck what damn it one class per metadata source???!

class MDSource:
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
        self.currentRecord=Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error)
        self.session.add(self.currentRecord)
        #TODO how to commit??!

    def getCurrentValue(self):
        #FIXME somehow I think I need a way to hold this until everything is collect before I commit? or should I just commit?
        return None

    def getAbsError(self):
        #TODO this is where online analysis based on calibration should go??? well we also need that somewhere else too...
        return None


class MDS_espX(MDSource):
    prefix='m'
    unit='m'
    mantissa=5
    ctrl_name='espControl'
    def getCurrentValue(self):
        return self.ctrl.getX()


class MDS_espY(MDSource):
    prefix='m'
    unit='m'
    mantissa=5
    ctrl_name='espControl'
    def getCurrentValue(self):
        return self.ctrl.getY()


class mccBase(MDSource):
    ctrl_name='mccControl'
    def __init__(self,Controller,session):
        try:
            self.channel
            super().__init__(Controller,session)
        except:
            raise AttributeError('%s requires a channel, use mccBindChan'%self.__class__.__name__)
    def record(self,Parent):
        self.ctrl.selectMC(self.channel) #FIXME make sure this mapping is static plox, if I have two mccs...
        super().record(Parent)


def mccBindChan(MDS_mcc,channel): #FIXME this does not work becasue it modifies the base class instead of adding a new one...
    out=MDS_mcc
    out.__name__=out.__name__+str(channel)
    out.channel=channel
    return out
def mccBindAll(channel):
    pass


class MDS_mccHE(mccBase):
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetHoldingEnable()


class MDS_mccH(mccBase):
    prefix=''
    unit='V'
    mantissa=3
    def getCurrentValue(self):
        return self.ctrl.GetHolding()


class MDS_mccPS(mccBase):
    prefix=''
    unit='number' #FIXME storing these codes is going to be really really confusing
    mantissa=3
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignal()


class MDS_mccPSG(mccBase):
    """Gain for primary signal"""
    prefix=''
    unit='number'
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignalGain()


class MDS_mccPSLPF(mccBase):
    """Low pass filter for primary signal"""
    prefix=''
    unit='Hz'
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignalLPF()


class MDS_mccPO(mccBase):
    """Pipette offset"""
    prefix=''
    unit='V'
    mantissa=5
    def getCurrentValue(self):
        return self.ctrl.GetPipetteOffset()


class MDS_mccFCC(mccBase):
    """Fast Comp Cap"""
    prefix=''
    unit='F'
    #no mantissa here since not sure if mcc uses the full float in amplifier
    def getCurrentValue(self):
        return self.ctrl.GetFastCompCap()


class MDS_mccSCC(mccBase):
    """Slow Comp Cap"""
    prefix=''
    unit='F'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompCap()


class MDS_mccFCT(mccBase):
    """Fast Comp Tau"""
    prefix=''
    unit='s'
    def getCurrentValue(self):
        return self.ctrl.GetFastCompCap()


class MDS_mccSCT(mccBase):
    """Slow Comp Tau"""
    prefix=''
    unit='s'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompTau()


class MDS_mccSCTE(mccBase):
    """Slow Comp Tau X20 enable"""
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompTauX20Enable()


class MDS_mccBBE(mccBase):
    """Bridge balance enable"""
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetBridgeBalEnable()


class MDS_mccBBR(mccBase):
    """Bridge balance resistance"""
    prefix=''
    unit='R'
    def getCurrentValue(self):
        return self.ctrl.GetBridgeBalResist()


def main():
    print(globals())
    from rig.esp import espControl
    from rig.mcc import mccControl
    from database.main import sqliteEng,initDBScience,populateConstraints,Experiment
    engine=sqliteEng(False)
    session=initDBScience(engine)
    populateConstraints(session)

    esp=espControl()
    mcc=mccControl()

    ex=MDS_espX(esp,session)
    mccHE=mccBindChan(MDS_mccHE,0)(mcc,session)
    print(ex.name)
    ex.record(Experiment)
    print(mccHE.name)
    mccHE.record(Experiment)
    session.commit()
    print(session.query(Experiment.MetaData).all())

    return ex

if __name__=='__main__':
    main()

