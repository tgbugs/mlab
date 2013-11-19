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
    setter_name=None #FIXME the name of the setting function
    getter_name=None #name of the function used to get stuff
    writer_name=None #eg getattr(writeTarget,self.writer_name)
    collection_name=None #eg metadata_ or something mapped collection name
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

class baseio:
    #TODO inspect.getsourcelines for versioning? or... what? doesn't work for wrapped classes
    @property
    def name(self):
        return self.__class__.__name__#[4:]

    def __init__(self,session):
        self.validate()
        try:
            self.MappedInstance=session.query(MappedClass).filter_by(name=self.name).one()
        except:
            self.persist(session)
        self.session=session

    def validate(self):
        raise NotImplementedError('You MUST implement this at the subclass level')

    def persist(self,session):
        session.add(self.MappedInstance)
        session.commit()
        

class ctrlio(baseio):
    function_name=''
    kwargs={}
    ctrl_name=''

    def __init__(self,session,controller_class):
        self.ctrl=controller_class
        super().__init__(session)

    def validate(self):
        if self.ctrl_name == self.ctrl.__class__.__name__:
            #TODO check the version!
            pass
        else:
            raise TypeError('Wrong controller for this step!')
            
    def persist(self,session):
        self.MappedInstance=MappedClass(ctrl_name=self.ctrl_name,function_name=
                                self.function_name,kwargs=self.kwargs)
        super().persist(session)


class Get(ctrlio): #FIXME now that this is separate from Writer... wat do?
    #TODO i think this somehow needs to interface with subjects, or do I need another step type? Set has it too
    MappedClass=None #Getter
    function_name=''
    kwargs={}
    ctrl_name=''

    def get(self,**kwargs):
        self.kwargs.update(kwargs)
        out=getattr(self.ctrl,function_name)(**self.kwargs)
        return {'value':out}

    def do(self,**kwargs):
        return self.get(**kwargs)


class Set(ctrlio): #FIXME must always have an input value
    #TODO set COULD be used to change the subject/set of subjects? YES
    MappedClass=None #Setter
    function_name=''
    kwargs={}
    ctrl_name=''

    def set(self,**kwargs):
        self.kwargs.update(kwargs)
        try:
            setter=getattr(self.ctrl,function_name)
            setter(**self.kwargs)
            return {'success':True} #FIXME *args will almost never be in order...
        except:
            raise #error or true false??

    def do(self,**kwargs):
        return self.set(**kwargs)

class Read(baseio): #FIXME technically anything read from the database should already be annotated
    #AND the link between what is read MUST be maintained... which is quite hard w/ this setup...?
    MappedClass=None #DataBaseSource BAD BAD BAD BAD practice
    class_kwargs={}
    MappedReader=None #literally any mapped class, depending on the query strategy
    filter_string='' #FIXME these do no allow sufficient query power
    order_by=''
    def validate(self):
        #check to make sure stuff here has not changed? ie versioning?
        pass
    def persist(self,session):
        mrn=self.MappedReader.__name__
        self.MappedInstance=MappedClass(name=self.name,reader_name=mrn,filter_string=self.filter_string,order_by=self.order_by)
        super().persist(session)
    def read(self,readTarget=None,**kwargs): #this seems to be needed for analysis... but how to we tie it in 
        raise NotImplementedError('You MUST implement this at the subclass level')
        query=self.session.query(self.MappedReader).filter(self.filter_string).order_by(self.order_by)
        #we explicitly do NOT want to allow subcolumns so that analysis can be properly linked to the
            #generating data objects??
        reclist=query.all()
        return {'value':reclist}
    def do(self,**kwargs):
        if 'writeTarget' in kwargs.keys():
            kwargs['readTarget':kwargs['writeTarget']] #stupid hack
        return self.read(**kwargs)


class Write(baseio):
    MappedClass=None #MetaDataSource
    class_kwargs={}
    MappedWriter=None #MetaData
    writer_kwargs={}
    def validate(self):
        #check to make sure stuff here has not changed? ie versioning?
        pass
    def persist(self,session):
        mwn=self.MappedWriter.__name__
        self.MappedInstance=MappedClass(name=self.name,writer_name=mwn,kwargs=self.kwargs)
        super().persist(session)
    def write(self,writeTarget=None,autocommit=False,**kwargs): #not handling errors here
        self.writer_kwargs.update(kwargs) #XXX kwargs should include the value
        self.session.add(self.MappedWriter(writeTarget=writeTarget,**self.kwargs)) #TODO parent shall be speced in kwargs???
        if autocommit:
            self.session.commit()
        return {'success':True}
    def do(self,**kwargs):
        return self.write(**kwargs)


class Analysis:
    MappedClass=None
    analysis_function=lambda **kwargs: 2+2
    def validate(self):
        pass
    def persist(self):
        pass
    def analyze(self,**kwargs): #TODO make sure to unpack everything when calling analyze
        out=self.analysis_function(*args,**kwargs)
        return {'result':out}
    def do(self,**kwargs):
        return self.analyze(**kwargs)


class Check:
    MappedClass=None
    check_function=lambda **kwargs:True #return type: Boolean please
    def validate(self):
        #make sure the code for the check function hasn't change, if it has, increment version
        pass
    def persist(self):
        pass
    def check(self,**kwargs):
        out=self.check_function(**kwargs)
        return {'success':out}
    def do(self,**kwargs):
        return self.check(**kwargs)
