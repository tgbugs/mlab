#TODO FIXME there are three things that are trying to go on here
#1) easy way to create the steps of an experiment
#2) easy way to create the datasources for an experiment
#3) bind the result to an object
#compatability between the three breaks down when:
#the datasource specified by 2 is not 1:1 with the result generated by the step 1
#put another way: if the object generated by 1 is not what we want to bind in 3
#because we want to bind a sub component of 3
#eg multiple df placeholders, the datafile and record datafile

#FIXME fuck, it is rather obvious that steps have substeps... but this could be hard to persist?
#FIXME also, datasources really do need to be reused...

#TODO the step object in the database... should link... datasources, analysis, etc to the object... but that is already done...
#it is hard to understand the logic of a list of measurements and analysis especially if something like a sanity check is not annotated as such
#it would depend on the name given to the object...

#FIXME ALL STEPS, EVEN THE MOST BASIC, ARE DATASORUCES, booleans saying 'this step is done!' based on the class name of the step

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

class Get(BaseDataIO):
    MappedClass=None #from database.models import thing as MappedClass
    ctrl_name=None
    getter_name=None #name of the function used to get stuff
    def __init__(self,Controller,session):
        super().__init__(Controller,session)
        if getter_name:
            self.getter=getattr(self.ctrl,self.getter_name) #FIXME allow override
    def getValue(self):
        self.value=self.getter()
    def do(self):
        self.getValue()
        return self.value

class GetWrite(Get):
    MappedClass=None #from database.models import thing as MappedClass
    ctrl_name=None
    getter_name=None #name of the function used to get stuff
    writer_name=None #eg getattr(writeTarget,self.writer_name)
    collection_name=None #eg metadata_ or something
    def writeValue(self,writeTarget,autocommit=False):
        collection=getattr(writeTarget,self.collection_name)
        writer=getattr(writeTarget,self.writer_name)
        collection.append(writer(MappedInstance,self.value)) #FIXME this gives some insight into array formats
        if autocommit:
            self.session.commit()
    def do(self,writeTarget):
        self.getValue()
        self.writeValue(writeTarget)
        return self.value

class SetGetWriteCheck(GetWrite): #this is the basis for following protocols... eg print and input
    MappedClass=None #from database.models import thing as MappedClass
    ctrl_name=None
    getter_name=None #name of the function used to get stuff
    writer_name=None #eg getattr(writeTarget,self.writer_name)
    collection_name=None #eg metadata_ or something
    setter_name=None #FIXME the name of the setting function
    def __init__(self,Controller,session):
        super().__init__(Controller,session)
        if setter_name:
            self.setter=getattr(self.ctrl,self.setter_name)
    def setValue(self,set_value,error=0): #both value and expected value will be recoreded somehow...
        self.expected_value=set_value
        self.ev_error=error #allowed error
        self.setter(self.expected_value)
    def checkValue(self):
        raise NotImplementedError('You MUST implement this at the subclass level')
    def do(self,writeTarget,set_value):
        self.setValue(set_value) #TODO make sure that this will block properly
        super().do(writeTarget) #FIXME this needs to write value AND expected_value
        self.checkValue() #check post write and THEN raise so that the bad value is recorded
        return self.value

class Analysis(Get): #mostly for online stuff that won't be persisted which is really very few things
    MappedClass=None #from database.models import thing as MappedClass
    ctrl_name=None
    getter_name=None #name of the function used to get stuff
    analysis_function=None #FIXME probably should be a from xyz import thing as function
    def getValue(self,analysis_value=None):
        self.value=analysis_value #FIXME how do we link this to the output...
        if not self.value:
            super().getValue() #FIXME make sure this sets self.value correctly
    def analysis(self):
        self.value=self.analysis_function(self.value)
    def do(self,analysis_value=None):
        self.getValue(analysis_value)
        self.analysis() #FIXME how to check these...
        return self.value

class AnalysisWrite(Analysis,GetWrite): #datafiles should be opened via GetWrite or simply via Get
    MappedClass=None #from database.models import thing as MappedClass
    ctrl_name=None
    getter_name=None #name of the function used to get stuff
    writer_name=None #eg getattr(writeTarget,self.writer_name)
    collection_name=None #eg metadata_ or something
    function=None #FIXME probably should be a from xyz import thing as function
    def do(self,writeTarget,analysis_value=None):
        self.getValue(analysis_value)
        self.analysis() #FIXME how to check these...
        self.writeValue(writeTarget)
        return self.value

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
    collection_name=None #eg metadata_ or something
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





def doStep(self,Parent=None,autocommit=False): #the assertion that this data is about this object happens here... it is doccumented via the data not via the subject... TODO need to doccument MDSes...
    try:
        log that the step happened successfully!
    except:
        log that the step failed hardcore!
        raise FailError('oops that step failed! now you cannot continue because the coder is an idiot')
    #TODO by default this sould log the event to something... but because these don't have experiments as default parents... waaiitttt...
    raise NotImplementedError('You MUST implement this at the subclass level')
    #FIXME ideally this step should raise an error if a variable being assigned will not persist



class SetupStep(ExpStep):
    #step used as an interactive checklist
    #should be possible to display the whole list
    #and then go through them all...
    pass


class SanityCheckStep(ExpStep): #FIXME should steps be allow to call other steps??!??! organizing by datasource makes sense but multiple different steps might use the same datasource!!!
    #make sure all the things are consistent, eg does this headstage ACTUALLY corrispond to IN 0??
    expected_value=None
    allowed_error=None
    def doStep(self,Parent,autocommit=False):
        measured_value=self.getValue()
        if allowed_error:
            minimum = self.expected_value - self.allowed_error
            maximum = self.expected_value + self.allowed_error
            if minimum <= self.measured_value and self.measured_value <= maximum:
                print('Sanity check passed!')
                #TODO do something with DataContainer?
            else:
                raise ValueError('Sanity check failed!')
        elif self.measured_value is not self.expected_value:
            raise ValueError('Sanity check failed!')
        else:
            print('Sanity check passed!')
            #TODO Parent.data.add(measured 
    def getValue(self):
        raise NotImplementedError('You MUST implement this at the subclass level')



class AnalysisStep(ExpStep):
    #used for online analysis (and doccumenting it)
    #could also be used for offline analysis probably a good idea for doccumenting the version of the code and stuff
    #TODO set up a check at creation time that verifies that the analysis step has the data it will need
    from database.models import Analysis as MappedClass
    def doStep(self,Parent,autocommit=False):
        result=self.getResult()
        #TODO Parent??? Parent.Results?!?!
    def getResult(self):
        #self.session.query(GetTheDataNeeded)
        #FIXME TODO AnalysisType should link against specific fields it is expecting?? need to work out the issue with tensor/timeserries data first
        #basically should we go through the datainterface to get to analysis?
        pass


class ChangeVariableStep(ExpStep):
    #move the microscope stage
    #set the mcc state
    #load a clx protocl #FIXME this may not go here, but we will see about that
    def doStep(self,Parent,autocommit=False):
        self.ctrl.doSomeShit()
        Parent.metadata_.add(well shit, this could be a boolean, but actually we probably want to record the old and new value...)


class GetDataStep(ExpStep):
    def doStep(self,ParentorParents,autocommit=False): #FIXME collections of thigns??
        pass


class GetDataFileStep(ExpStep):
    #should be preceeded by a ChangeVariableStep... TODO add a check for this
    protocol_filename=None #FIXME may not need this
    def doStep(self,SubjectCollection,autocommit=False): #FIXME problem with Parent not being in tree? or no?
        datafile=self.runProtocol()
        datafile.subjects.extend(SubjectCollection)
        #[subject.datafiles.extend(datafile) for subject in SubjectGroup.members] #FIXME? right way to do?
        #is subject group redundant here with DataFile itself the only issue being priority in time???
    def runProtocol(self):
        """Return a DataFile instance"""
        raise NotImplementedError('Each datafile type you are going to collect needs to implement this')


class GetSoftwareChanStep(ExpStep):
    #I SHOULD BE ABLE TO MAKE THIS WORK OFF OF HASHARDWARE???
    #I suppose it *could* just go in metadata, but I want it to be relational
    #FIXME is this a getParams-like step???
    #the problem is that the equivalent is 'HasMetaDataSources'
    #these are all things that we must know aprior, which is simply not possible for certain things...
    hardware_id=None #TODO do I DEMAND that a certain headstage be used, or to I allow assignment?
    def doStep(self,Parent,autocommit=False):
        #unfortunately the way this is set up this class is 1:1 WITH the channel itself...
        pass
    def getAssociatedSoftwareChannel(self): #FIXME Subject should somehow inherit df_type from group ?
        

class BackupStep(ExpStep):
    """ Step to initiate backup of datafiles or anything else. Probably best
        used between subjects when drives are not being hit with writes. """
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
            if self.MappedInstance.hardware_id != self.hardware_id:
                self.MappedInstance.hardware_id=self.hardware_id
                self.session.commit() #FIXME make sure this works right
        except:
            raise AttributeError('wtf has you done!?')

    def Persist(self):
        self.MappedInstance=MappedClass(name=self.name,prefix=self.prefix,unit=self.unit,mantissa=self.mantissa,hardware_id=hardware_id)
        self.session.add(self.MappedInstance)
        self.session.commit()

    def doStep(self,Parent,autocommit=False):
        """ adds the product of getCurrentValue and getAbsError to the session but does NOT commit by default"""
        value=self.getCurrentValue()
        abs_error=self.getAbsError()
        self.session.add(Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error)) #FIXME do we actually need parent here?
        Parent.metadata_.add(Parent.MetaData(value,Parent,self.MetaDataSource,abs_error=abs_error))
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
            if self.MappedInstance.hardware_id != self.hardware_id:
                self.MappedInstance.hardware_id=self.hardware_id
                self.session.commit() #FIXME make sure this works right
        except:
            raise AttributeError('wtf has you done!?')

    def Persist(self):
        self.MappedInstance=MappedClass(name=self.name,hardware_id=hardware_id)
        self.session.add(self.DataFileSource)
        self.session.commit()
    #yay! this is the base class to define datasources for where datafiles come from
    #because in theory it is possible to have more than one DSource for an experiment
    #FIXME and suddently we discover that DataFileSource and DataSource should be distinct since DSource should be reserved for structured data that will be passed in
    #FIXME actually ideally we should just be able to define the DF source TYPE and be done with it but that leads to either lots of rows or lots of columns :/
