class ExpStep:
    """ Base class for all experiment steps
        This should be extended for each type of step
        Step types should then be subclassed once more
        To define individual records
        :param: Controller, a class that has a function that will return floats,
                __class__.__name__ must match ctrl_name
        :param: session, a sqlalchemy database session that hopefully has tables matching your mapped classes
    """

    MappedClass=None
    ctrl_name=None

    @property
    def name(self):
        #FIXME add a way to explicity name classes if you want?
        return self.__class__.__name__[4:] #FIXME? enforcing a sensible naming scheme might make sense, but that is a really pointless abuse that is hard to doccument and communicate, use the need for unique naming within the 'step' namespace to map on to the demand for unique step names

    def __init__(self,Controller,session):
        #TODO using these steps it SHOULD be possible to reconstruct a timeline for each experiment
        #and look at the temporal variance, good way to track experimenter performance
        if Controller.__class__.__name__==self.ctrl_name:
            self.controller_version=Controller.version #FIXME run a hash against the file find another way for external datafile soruces
            #BIGGER FIXME doccumenting which version of the controller was used is now VITAL
            if not self.controller_version:
                raise BaseException('What are you doing not keeping track of what software you used! BAD SCIENTIST')
            self.ctrl=Controller
        else:
            raise TypeError('Wrong controller for this step!')
        self.session=session
        try:
            self.MappedObject=self.session.query(MappedClass).filter_by(name=self.name).one()
        except NoResultFound:
            self.Persist()

    def Persist(self):
        raise AttributeError('You MUST implement this at the subclass level')

    def doStep(self):
        raise AttributeError('You MUST implement this at the subclass level')

class SanityCheckStep(ExpStep):
    #make sure all the things are consistent, eg does this headstage ACTUALLY corrispond to IN 0??
    pass

class AnalysisStep(ExpStep):
    #used for online analysis (and doccumenting it)
    #could also be used for offline analysis probably a good idea for doccumenting the version of the code and stuff
    from database.models import Analysis as MappedClass
    pass

class ChangeVariableStep(ExpStep):
    #move the microscope stage
    #set the mcc state
    #load a clx protocl #FIXME this may not go here, but we will see about that
    pass

class MDSource:
    from database.models import MetaDataSource as MappedClass
    prefix=None #FIXME need some way to convey that prefix and unit cannot be changed w/o changing name
    unit=None #FIXME need some way to convey that prefix and unit cannot be changed w/o changing name
    mantissa=None #FIXME mantissa should be rounded not truncated, make sure this is implemented
    hardware_id=None #this will be mutable so just chagne it here

    def __init__(self,Controller,session):
        super().__init__(Controller,session)
        try:
            if self.MappedObject.hardware_id != self.hardware_id:
                self.MappedObject.hardware_id=self.hardware_id
                self.session.commit() #FIXME make sure this works right
        except:
            raise AttributeError('wtf has you done!?')

    def Persist(self):
        self.MappedObject=MappedClass(name=self.name,prefix=self.prefix,unit=self.unit,mantissa=self.mantissa,hardware_id=hardware_id)
        self.session.add(self.MappedObject)
        self.session.commit()

    def doStep(self,Parent,autocommit=False):
        """ adds the product of getCurrentValue and getAbsError to the session but does NOT commit by default"""
        value=self.getCurrentValue()
        abs_error=self.getAbsError()
        self.session.add(Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error))
        #Parent.metadata_.append(Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error)) #alt
        if autocommit:
            self.session.commit()

        #self.currentRecord=Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error)
        #FIXME is currentRecord a sufficient safety net?? could aways just get the data again...
        #probably shouldn't worry TOO much about all these crazy failure cases
        #self.session.add(self.currentRecord)

    def getCurrentValue(self):
        return None

    def getAbsError(self):
        return None

class DFSource: #TODO
    from database.models import DataFileSource as MappedClass #FIXME check to see if already imported?
    hardware_id=None #this will be mutable so just chagne it here
    def __init__(self,Controller,session):
        super().__init__(Controller,session)
        try:
            if self.MappedObject.hardware_id != self.hardware_id:
                self.MappedObject.hardware_id=self.hardware_id
                self.session.commit() #FIXME make sure this works right
        except:
            raise AttributeError('wtf has you done!?')
    def Persist(self):
        self.MappedObject=MappedClass(name=self.name,hardware_id=hardware_id)
        self.session.add(self.DataFileSource)
        self.session.commit()
    #yay! this is the base class to define datasources for where datafiles come from
    #because in theory it is possible to have more than one DSource for an experiment
    #FIXME and suddently we discover that DataFileSource and DataSource should be distinct since DSource should be reserved for structured data that will be passed in
    #FIXME actually ideally we should just be able to define the DF source TYPE and be done with it but that leads to either lots of rows or lots of columns :/
