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


#XXX NOTE: readTarget and WriteTarget are really the only INPUT that is dynamic for dataios

class baseio:
    #TODO inspect.getsourcelines for versioning? or... what? doesn't work for wrapped classes
    dependencies=[] #these propagate up to iodeps, we want to use the same dataios for many steps
        #so we can't use dataio names for step names DUH that was why we split stuff up in the first place!
        #and they should be the expected keywords for anything downstream
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
    kwargs={} #FIXME because Getters are now divorced from Writers, need to validate that units match?
    ctrl_name=''
    dependencies=[] #TODO these will be in the expected kwarg list
    #FIXME time serries acquisition are all within their own get so no worries
        #about key collisions with multiple reads from the same Getter
    #FIXME PROBLEM: dep names here are different than the dep names for steps...
        #gotta figure out how to integrate the two... :/
    #atm dep_names in here just mean that the inner function is going to expect those keywords to be present
    #TODO: could auto-generate steps based on the dep names found here... probably wouldnt be quite so reusable

    def do(self,**kwargs):
        out=self.get(**kwargs)
        return {'%s'%self.name:out}#XXX NOTE: this makes it super easy to chain things by dependency name
            #might not even need the whole step framework to keep track of deps if the dataios keep the
            #names of the upstream dataios that they need... or really just automatically add certain deps

    def get(self,**kwargs):
        """Modify as needed"""
        self.kwargs.update(kwargs)
        return getattr(self.ctrl,function_name)(**self.kwargs)

class Set(ctrlio): #FIXME must always have an input value
    #TODO set COULD be used to change the subject/set of subjects? YES/NO???
    #TODO probably also to be used for resetting the experimental state? NO??
        #both of the above suggestions seem like too much overloading of this
        #this is about io not about tracking the internal state of the program
        #even if we are persisiting that too
    #TODO setter's should really be reading their values from a protocol of some sort...
        #which ideally would be stored in the database and thus accessed via a read
    MappedClass=None #Setter
    function_name=''
    kwargs={}
    ctrl_name=''
    dependencies=[] #TODO virtually all setters should have a read dep or define the set value in kwargs

    def do(self,**kwargs):
        out=self.set(**kwargs)
        return {'%s'%self.name:out}

    def set(self,**kwargs):
        """Modify as needed"""
        self.kwargs.update(kwargs)
        try:
            setter=getattr(self.ctrl,function_name)
            setter(**self.kwargs)
            return True
        except:
            raise #error or true false??


class Bind(baseio): #this is not quite analysis, it is just a data organizing step
    MappedClass=None #TODO yay! finally a simple way to collect datasources into vectors!
        #obviously if I have 100 independent sensors this things is getting refactored
    dependencies=[] #eg: esp_x esp_y, or channel_1, channel_2, etc
    out_format=[] #take the dep_names from above and put them in the structure you want, need not be a list
        #rewrite self.bind as need for more complex data structures

    def do(self,**kwargs):
        out=self.bind(**kwargs)
        return {'%s'%self.name:out}

    def bind(self,**kwargs):
        """Modify as needed"""
        out=[]
        for kw in out_format:
            out.append(kwargs[kw])
        return {'%s'%self.name:out}


class Read(baseio): #FIXME technically anything read from the database should already be annotated
    #AND the link between what is read MUST be maintained... which is quite hard w/ this setup...?
    MappedClass=None #DataBaseSource BAD BAD BAD BAD practice
    class_kwargs={}
    MappedReader=None #literally any mapped class, depending on the query strategy

    def validate(self):
        #check to make sure stuff here has not changed? ie versioning?
        pass

    def persist(self,session):
        mrn=self.MappedReader.__name__
        self.MappedInstance=MappedClass(name=self.name,reader_name=mrn,filter_string=self.filter_string,order_by=self.order_by)
        super().persist(session)

    def do(self,**kwargs):
        if 'writeTarget' in kwargs.keys(): #FIXME very dangerous!
            kwargs['readTarget':kwargs['writeTarget']] #stupid hack
        out=self.read(**kwargs)
        return {'%s'%self.name:out}

    def read(self,readTarget=None,**kwargs): #this seems to be needed for analysis... but how to we tie it in 
        """Modify as needed"""
        raise NotImplementedError('You MUST implement this at the subclass level')
        query=self.session.query(self.MappedReader).filter(self.filter_string).order_by(self.order_by)
        #we explicitly do NOT want to allow subcolumns so that analysis can be properly linked to the
            #generating data objects??
        return query.all()


class Write(baseio): #wow, this massively simplifies this class since the values is passed in as a kwarg
    #TODO validate incoming units :/
    MappedClass=None #MetaDataSource
    class_kwargs={} #things like units etc,
        #XXX BEWARE need to validate these against inputs AT START TIME NOT RUN TIME
    MappedWriter=None #MetaData, we're not even messing with adding to collections right now
    writer_kwargs={}
    dependencies=[] #pretty much every writer should have get or an analysis or something

    def validate(self):
        #check to make sure stuff here has not changed? ie versioning?
        #check units XXX this may have to be done at the level of steps
            #OR we can just feed it forward from the Getter/Analysis
            #and throw an error if it is not defined, but then we can't persist Writer's properly...
            #maybe we don't NEED to persist writers properly, INFACT I'm faily ertain we don't
            #because they aren't what has the properties, they just need to persist them
            #we can probably document the 'datasource' properties via the getter
            #even through tht writer is what actually 'writes' the data
            #think about how to make this sensible and don't forget that kwargs would be
            #overwritten if we use {'mantissa':5} for multiple things, BUT
            #it should be ok as long as it gets fed DIRECTLY in to the writer, which really
            #should happen...
        pass

    def persist(self,session):
        mwn=self.MappedWriter.__name__
        self.MappedInstance=MappedClass(name=self.name,writer_name=mwn,writer_kwargs=self.writer_kwargs)
        super().persist(session)

    def do(self,**kwargs):
        out=self.write(**kwargs)
        return {'%s'%self.name:out}

    def write(self,writeTarget=None,autocommit=False,**kwargs): #not handling errors here
        """Modify as needed"""
        self.writer_kwargs.update(kwargs) #XXX kwargs should include the value
        self.session.add(self.MappedWriter(writeTarget=writeTarget,**self.writer_kwargs)) #TODO parent shall be speced in kwargs???
        if autocommit:
            self.session.commit()
        return True


class Analysis(baseio):
    MappedClass=None
    analysis_function=lambda **kwargs: 2+2
    dependencies=[]

    def validate(self):
        pass

    def persist(self):
        pass

    def do(self,**kwargs):
        out=self.analyze(**kwargs)
        return {'%s'%self.name:out}

    def analyze(self,**kwargs):
        """Modify as needed"""
        return self.analysis_function(**kwargs)


class Check(baseio):
    MappedClass=None
    check_function=lambda **kwargs:True #return type: Boolean please
    dependencies=[]

    def validate(self):
        #make sure the code for the check function hasn't change, if it has, increment version
        pass

    def persist(self):
        pass

    def do(self,**kwargs):
        out=self.check(**kwargs)
        return {'%s'%self.name:out}

    def check(self,**kwargs):
        """Modify as needed"""
        return self.check_function(**kwargs)
