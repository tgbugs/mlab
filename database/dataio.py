#pulled this out of api.py
class BaseDataIO:
    """ 
        Base class for all experiment steps
        This should be extended for each type of step
        Step types should then be extended once more
        To define individual records/steps

        :attr::class:`.MappedClass` should appear in local namespace via
            `from database.models import ModelName as MappedClass`. These
            classes are things that ususally will not need to be queried
            within the scope of datacollection.
        :attr::string:`.ctrl_name`
        :attr::list:`.prereqList`

        :param: Controller, a class instance w/ function that can return floats,
            Controller.__class__.__name__ must match ctrl_name
        :param: session, a sqlalchemy database session that
            (hopefully) has tables matching your mapped classes

        :meth:`.Persist`
        :meth:`.do` retunrs self.value
    """

    #FIXME could make a factory function that takes the class variables and returns the class...
    #the only issue is writeTarget can't be checked before hand :/
    MappedClass=None #from database.models import thing as MappedClass
    mappedClassPropertiesDict={} #things required by the database, eg datasource units
    ctrl_name=None

    @property
    def name(self):
        #FIXME add a way to explicity name classes if you want?
        return self.__class__.__name__[4:]

    def __init__(self,Controller,session): #FIXME controller could also be a MappedInstance?
        if Controller.__class__.__name__==self.ctrl_name:
            self.controller_version=Controller.version #FIXME hash the file or something for external stuff
            #BIGGER FIXME doccumenting which version of the controller was used is now VITAL
            if not self.controller_version:
                raise AttributeError('What are you doing not keeping track of'
                                     ' what software you used! BAD SCIENTIST')
            self.ctrl=Controller
        else:
            raise TypeError('Wrong controller for this step!')
        self.session=session
        try:
            self.MappedInstance=self.session.query(MappedClass).filter_by(name=self.name).one()
        except NoResultFound:
            self.Persist()
    def checkVersion(self,thing,strict=False): #validate that the code has not changed
        #TODO this should be handled at the level of the experiment
        #hash the code of the thing #FIXME should this all be here or should it be tracked globally on startup?
        if strict:
            #hash the file that it came from and compare it to the previous hash
        pass

    def Persist(self):
        """
        Returns None
        Creates an instance of :class:`.MappedClass` according to other defined
        params, assigns it to :instance:`.MappedInstance` and commits it to the database.
            
        """
        raise NotImplementedError('You MUST implement this at the subclass level')

    def do(self):
        raise NotImplementedError('You MUST implement this at the subclass level')

class DataIO(BaseDataIO): #IXCK ugly ugly might be nice for a factory :/ but is poorly constrained @do, so slow
    #NOTE TO SELF: this interface needs to be here unless we go with STI for dataio objects in order to implement persistence, and EVEN THAT misses the point which is that there are live functions that we want to run and have doccumented, I supposed using only names it would be possible to init everything and save it BUT we would still need something to deal with actually tying it all together at run time which is what THIS is supposed to do
        #doing it this way we keep the all the relevant information in one place that can all be seen at the same time and debugged more easily
        #the alternative is generating DataIO objects directly from database entries but that still leaves tying them to actual live code objects which seems like it could go very wrong and would still require an input interface and we would essentially be persisting a class that looks like this anyway
        #probably do want a way to recreate classes straight from the database though... but that is alot of work and we will have to do it in the future NOT RIGHT NOW
    MappedClass=None #from database.models import thing as MappedClass
    mcKwargs={} # MappedClass(**kwargs) things for the database, eg datasource units
    ctrl_name=None #FIXME why do we need this again??? ANSWER: because we need live functions and I'm not sure the best way to unambigiously name a 'dead' function of a class and make it live (the way in rigcont is iffy)
    getter_name=None #name of the function used to get stuff
    writer_name=None #eg getattr(writeTarget,self.writer_name)
    collection_name=None #eg metadata_ or something mapped collection name
    setter_name=None #FIXME the name of the setting function
    check_function=None #FIXME checks are ONLY going to be written to experiments, so we can pull them out to steps? or even make them their own step akin to analysis? yeah, because checks often need to occur across multiple steps and longer stretches of time
    analysis_function=None #FIXME probably should be a from xyz import thing as function
    def __init__(self,Controller,session):
        super().__init__(Controller,session)
        if getter_name:
            self.getter=getattr(self.ctrl,self.getter_name) #FIXME allow override
        if setter_name:
            self.setter=getattr(self.ctrl,self.setter_name)
        #TODO version checks

    def Persist(self):
        #self.MappedInstance=MappedClass(name=self.name,prefix=self.prefix,unit=self.unit,mantissa=self.mantissa,hardware_id=hardware_id)
        self.MappedInstance=MappedClass(**self.mcKwargs)
        self.session.add(self.MappedInstance)
        self.session.commit()

    def setValue(self,set_value,error=0): #both value and expected value will be recoreded somehow...
        self.expected_value=set_value
        self.ev_error=error #allowed error
        self.setter(self.expected_value)
    def getValue(self,analysis_value=None):
        self.value=analysis_value #FIXME how do we link this to the output...
        if not self.value:
            self.value=self.getter()
    def checkValue(self): #FIXME making check steps similar to analysis simplifies saving results
        self.check_function()
    def analysis(self):
        #FIXME need version control here... :/ so it is possible to track down errors
        self.value=self.analysis_function(self.value)
    def writeValue(self,writeTarget,autocommit=False):
        collection=getattr(writeTarget,self.collection_name)
        writer=getattr(writeTarget,self.writer_name)
        collection.append(writer(MappedInstance,self.value)) #FIXME this gives some insight into array formats
        if autocommit:
            self.session.commit()
    def do(self,writeTarget=None,set_value=None,set_error=0,analysis_value=None,autocommit=False):
        if set_value: #FIXME handle lack of setter_name?
            self.setValue(set_value,set_error) #TODO make sure that this will block properly
        if analysis_value:
            self.getValue(analysis_value)
        else:
            self.getValue()
        if self.analysis_function:
            self.analysis() #FIXME how to check these...
        if writeTarget:
            self.writeValue(writeTarget,autocommit)
        if self.check_function:
            self.checkValue() #check post write and THEN raise so that the bad value is recorded
        return self.value


#pairings:
#MetaDataSource - clx,mcc,esp,key

#need failover if a function is not found?

