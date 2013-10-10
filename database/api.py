class MDSource: #FIXME move this to an actual API file in the database!??!
    """ Base class for all metadata sources
        :param: Controller, a class that has a function that will return floats,
                __class__.__name__ must match ctrl_name
        :param: session, a sqlalchemy database session that hopefully has tables matching your mapped classes
    """
    @property
    def name(self):
        return self.__class__.__name__[4:]
    prefix=None
    unit=None
    mantissa=None #FIXME mantissa should be rounded not truncated, make sure this is implemented
    ctrl_name=None

    def __init__(self,Controller,session):
        if Controller.__class__.__name__==self.ctrl_name:
            self.ctrl=Controller
        else:
            raise TypeError('Wrong controller for this metadata source!')
        
        self.session=session #FIXME is it better to create a new session every time or better to just leave one open? read up

        try:
            self.MetaDataSource=self.session.query(MetaDataSource).filter_by(name=self.name).one()
        except NoResultFound: #FIXME probably going to need to import this
            self.Persist()

    def Persist(self):
        self.MetaDataSource=MetaDataSource(name=self.name,prefix=self.prefix,unit=self.unit,mantissa=self.mantissa)
        self.session.add(self.MetaDataSource)
        self.session.commit()

    def record(self,Parent,autocommit=False):
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

class DSource: #TODO
    #yay! this is the base class to define datasources for where datafiles come from
    #because in theory it is possible to have more than one DSource for an experiment
    #FIXME and suddently we discover that DataFileSource and DataSource should be distinct since DSource should be reserved for structured data that will be passed in
    #FIXME actually ideally we should just be able to define the DF source TYPE and be done with it but that leads to either lots of rows or lots of columns :/
    pass
