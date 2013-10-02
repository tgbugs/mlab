from database.models import MetaDataSource, Experiment, Subject
#TODO what I need is a link between datasources and the Controller classes, that should probably be defined... here? or somewhere? or fuck what damn it one class per metadata source???!

class MDSource:
    @property
    def name(self):
        return self.name=self.__class__.__name__[4:]
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


class MDS_mccState(MDSource):
    ctrl_name='mccControl'
    def __init__(self,Controller,session,channel)
        self.channel=channel
        self.name=self.name+str(self.channel)
        super().__init__(Controller,session)
    def record(self,Parent):
        self.ctrl.selectMC(self.channel) #FIXME make sure this mapping is static plox, it wont be if I have two mccs...
        super().record(Parent)


class MDS_mccHE(MDS_mccState):
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetHoldingEnable()


class MDS_mccH(MDS_mccState):
    prefix=''
    unit='V'
    mantissa=3
    def getCurrentValue(self):
        return self.ctrl.GetHolding()


class MDS_mccPS(MDS_mccState):
    prefix=''
    unit='number' #FIXME storing these codes is going to be really really confusing
    mantissa=3
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignal()


class MDS_mccPSG(MDS_mccState):
    """Gain for primary signal"""
    prefix=''
    unit='number'
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignalGain()


class MDS_mccPSLPF(MDS_mccState):
    """Low pass filter for primary signal"""
    prefix=''
    unit='Hz'
    def getCurrentValue(self):
        return self.ctrl.GetPrimarySignalLPF()


class MDS_mccPO(MDS_mccState):
    """Pipette offset"""
    prefix=''
    unit='V'
    mantissa=5
    def getCurrentValue(self):
        return self.ctrl.GetPipetteOffset()


class MDS_mccFCC(MDS_mccState):
    """Fast Comp Cap"""
    prefix=''
    unit='F'
    #no mantissa here since not sure if mcc uses the full float in amplifier
    def getCurrentValue(self):
        return self.ctrl.GetFastCompCap()


class MDS_mccSCC(MDS_mccState):
    """Slow Comp Cap"""
    prefix=''
    unit='F'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompCap()


class MDS_mccFCT(MDS_mccState):
    """Fast Comp Tau"""
    prefix=''
    unit='s'
    def getCurrentValue(self):
        return self.ctrl.GetFastCompCap()


class MDS_mccSCT(MDS_mccState):
    """Slow Comp Tau"""
    prefix=''
    unit='s'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompTau()


class MDS_mccSCTE(MDS_mccState):
    """Slow Comp Tau X20 enable"""
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetSlowCompTauX20Enable()


class MDS_mccBBE(MDS_mccState):
    """Bridge balance enable"""
    prefix=''
    unit='bool'
    def getCurrentValue(self):
        return self.ctrl.GetBridgeBalEnable()


class MDS_mccBBR(MDS_mccState):
    """Bridge balance resistance"""
    prefix=''
    unit='R'
    def getCurrentValue(self):
        return self.ctrl.GetBridgeBalResist()


def main():
    from rig.esp import espControl
    from database.main import sqliteEng,initDBScience,populateConstraints
    engine=sqliteEng()
    session=initDBScience(engine)
    populateConstraints(session)

    esp=espControl()

    ex=MDS_espX(esp,session)
    print(ex.name)

    return ex

if __name__=='__main__':
    main()

