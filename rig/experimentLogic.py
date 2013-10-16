#from database.models import Experiment # Subject #, Mouse, Slice, Cell
from database.models import ExperimentType
from database import interface #FIXME
from debug import TDB

tdb=TDB()
printFD=tdb.printFuncDict

class ExperimentRunner:
    #FIXME use input() to get terminal input for stuff like depth?

    #this is preferable to having each thing be assigned individually to self, in fact we could even pass something like this in
            #NOTE somehow cells and slices go here for patch
                               #slices need to be added to mouse @ sliceprep? 

    def newExpFromLast(self):
        pass
    def newSubFromLast(self):
        #TODO this needs to handle subject hierarchies transparently
        #fortunately the orm should handle this without too much effort?
        pass
    def newExpFromTemp(self):
        pass
    def newSubFromTemp(self):
        pass


class ExperimentState:
    #TODO I need prototypes for experiments... also, need a way to get the current rig stats and link against it
    #basically tom's rig.children or something get them all in a list and stick them in the hardware list
    #reagents might be eaiser to propagate by date from their protype instead of by batch... or use a join?
    #TODO add a table for 'last used' things... eg person project, to make it easy to pick up where left off
    def __init__(self,session,expType):
        self.session=session #FIXME think about whether this is the best way to access the database (ie by passing around a session)
        self.expType=expType #FIXME check that it is a valid type
        state=self.getStateFromLastExperiment() #from experiment I can get basically retrieve everything I need to propagate

        
        #Hardware get current hardware
        #Reagents get current reagents
    def getStateFromLastExperiment(self): #FIXME this should *probably* go elsewhere but we'll work on that
        LastExp=self.session.query(Experiment).filter_by(type=self.expType).order_by(-Experiment.id)[0]
        self.person_id=LastExp.person_id
        self.project_id=LastExp.project_id #FIXME missing backref?

    def getCurrentHardware(self,root='Tom\'s Rig'):
        self.session.query(Hardware).filter_by()
        
    def newExperiment(self):
        hardware=getCurrentHardware(root)
        experiment=Experiment(project_id=self.project_id,person_id=self.person_id)
        self.session.add
    #termIO.session.Experiment
    #Mouse
    #Slice
    #Cells


class SomChr(ExperimentRunner):
    def newSlice(self):
        Slice()




class BaseExp:
    def __init__(self,rigIO,experiment=None,experimenttype=None): #FIXME should be arbitrary IO
        if not checkExpType(experimenttype):
            #check for things we're supposed to have
            try: self.name
            except: raise AttributeError('experiment definitions require a name')
            try: self.person_id
            except: raise AttributeError('experiment definitions require a person_id')
            try: self.project_id
            except: raise AttributeError('experiment definitions require a project_id')
            try: self.mdsDict
            except: raise AttributeError('the whole point of these is to have mdsDicts...')
            try: self.abbrev
            except: self.abbrev=None
            try: self.repository_url
            except: self.repository_url=None

            self.session=rigIO.Session() #a single experiment (even if long) seems like a natural scope for a session
            try:
                self.ExperimentType=self.session.query(experimenttype).\
                        filter_by(name=self.name).\
                        order_by('-id').first() #get the latest version of the experiment type w/ this name
            except:
                self.Persist()

        if Experiment: #resume experiment and override the default defined in child classes but check type
            if Experiment.type_id==self.ExperimentType.id:
                self.experiment=Experiment
            else:
                raise TypeError('Experiment.type does not match ExperimentType for this class')
        else:
            self.ExpFromType()

        #self.current_subjects=[] #TODO

        #create metadata sources
        self.imdsDict={}
        for MDS in self.mdsDict.values():
            self.imdsDict[MDS.__name__[4:]]=MDS(rigIO.ctrlDict[MDS.ctrl_name],self.session)

        #BIND ALL THE THINGS
        bind MDS to experiment
        bind MDS to subject TYPE #FUCK

    def checkExpType(self,experimenttype)
        if experimenttype: #implies that there is a session elsewhere...
            if experimenttype.id:
                try:
                    if self.name!=experimenttype.name:
                        raise AttributeError('Defined name does not match that of ExperimentType!')
                except:
                    pass
                names=[mds.name for mds in experimenttype.metadatasources]
                from rig.metadatasources import mdsAll
                self.mdsDict={}
                [self.mdsDict.update({name:cls}) for name,cls in mdsAll().items() if names.count(name[4:])]
                self.experimenttype=experimenttype
                #TODO get session from experimenttype?
                return 1
            else:
                raise AttributeError('no id')
        else:
            return None

    def record(self,Parent,keys): #keys to update from self.mdsDict #extremely granular record method
        #def record(self,mdsParentDict): << not many use cases
        #FIXME this is another option for starting a session
        [self.imdsDict[key].record(Parent) for key in keys]
        self.session.commit()
        return self

    def record_subset(self,Parent,threeString): #could use .count(threeString) but is slower and I control names
        return self.record( Parent, [key for self.imdsDict.keys() if key[:3]==threeString] )

    def record_all(self,Parent)
        [mds.record(Parent) for mds in self.imdsDict.values()]
        self.session.commit()
        return self

    def add_datafile(self):
        filename=None #TODO self.getNewDataFile()
        datafile=DataFile(self.experiment.repository,filename)
        self.experiment.datafiles.append(datafile)

        for subject in self.current_subjects:
            pass

    def add_subjects_by_id(self,ids): #FIXME subjects could come from elsewhere? where does the id come from
        #think big and automated, where does the id come from
        subjects=self.session.query(Subject).filter(Subject.id.in_(ids)).all()
        self.experiment.subjects.extend(subjects)
        return self

    def Persist(self):
        #TODO damn this is such a better idea...
        mds=[m.MetaDataSource for m in self.imdsDict.values()] #FIXME check for changes and update w/ version
        self.ExperimentType=ExperimentType(name=self.name,repository_url=self.repository_url,MetaDataSources=mds)
        self.session.add(self.ExperimentType)
        self.session.commit()
        return self

    def ExpFromType(self,startDateTime=None):
        #TODO
        #MDS_RecordCurrentHardware
        Experiment(self.ExperimentType,person_id=,project_id=,startDateTime=startDateTime) #reagents? subjects? TODO
        self.experiment=None
        return self

    def run(self):
        #loop make/get root subject
            #get subject metadata
            #record subject datafiles
                #get datafile metadata
            #recursive make/get nth child subject

 
    @class_method
    def getPreData(subject): #FIXME this way is really convoluted and will require good doccumentation
        if subject.preMDS is not None:
            [self.imdsDict[name].record(subject) for name in subject.preMDS]
        if subject.preProts is not None:
            [prot.record(subject) for prot in subject.preProts]
        #FIXME TODO add the equivalent for datafiles... or collapse all the data into one thing
    @class_method
    def getInterData(subject):
        [self.imdsDict[name].record(subject) for name in subject.interMDS]
    @class_method
    def getPostData(subject):
        [self.imdsDict[name].record(subject) for name in subject.postMDS]
        [prot.record(subject) for prot in subject.postProts] #XXX this is where the cell pair data goes

    def subjectLogic(self,subject): #TODO this one
        self.getParams(subject) #urg, not sure this is the best/most logical pattern... the calling object is the experiment but the thing that will hold the data is the subject :/ ie: confusing that I need to put something on the subject type to tell the experiment what to do when it encounters this type
        #subject.fillInParams() #FIXME I think the best pattern will be to have pre,post,inter, be from metadatasources and BaseExp should have the getPreData functions to keep things simple

        #it reduces flexibility a bit but it will preserve the order of the data we collect
        #and make everything standard since these are monkey patches, yes it breaks stuff up

        #subject.getPreData()
        self.getPreData(subject) #these functions basically call MDS_.record(subject) for MDS_ in subject.PreData
        for child in subject.children:
            self.subjectLogic(child)
            #subject.getInterData()
            if is last child:
                subject.makeMoreChilds() #FIXME can't iterate over children over and over...
                #TODO when making subjects from the EXPERMETNALLY defined one it can take Subjects as parents OR groups that have the same parent_id, CHECK TO VERIFY and there are some other problems that need to be solved
            #FIXME what if there are no actual children only the monkey patched?
        #subject.getPostData(subject)
        #subject.IfLastSubjectAddNewToParent_questionmark()
        self.getPostData(subject)

    def subjectSetLogic(self,subjects): #FIXME binding must occur before init otherwise the declarative style pattern will break also branching from a root that has more than one subject... :/ simultaneous recursion...
        """depth first traversal of subjects with the ability to add subjects at the deepest level first and then add on the way back up and go back down opperates on sets of subjects as if they are a single subject"""
        #FIXME there MUST be an exemplar set from which to opperate, but this fails as soon as an intermediate subject is added w/ no children???? SOLUTION: define a child type
        if not subjects.any():
            return 'DONE' #FIXME

        getObjectMetaData(subjects,wait=True)
        self.session.commit()
        getObjectDataFiles(subjects)

        if not_done: #FIXME this logic does not handle depth first, for example slices that have multiple cells because recursion doesn't quite work right still need a for loop
            all_childs=[]
            [all_childs.extend(subject.children) for subject in subjects]
            subjectSetLogic(all_childs)
        number=int(input('enter number of subjects to add')) #FIXME there is one more loop which is [[,,],[,,],[,,]] nexted lists of subjects
        return subjectSetLogic(makeNewSubjects(subjects[0],number=number)) #TODO
        #TODO the way to 'loop' over multiple subjects at the same level AFTER going to a deeper level is to just have a branched return scenario
        #argh! still not quite right

    def getObjectMetadata(self,objects,wait=False):
        def getMD(obj,wait):
            if wait:
                input('press any key to start collecting metadata for %s'%obj.__class__.__name__)
            for key in objects.metadatasource_names: #advantage here is that the list can be ordered in the order you want to collect the metadata
                self.mdsDict[key].record(obj)
        try:
            for obj in objects:
                getMD(obj)
        except AttributeError:
            getMD(obj)

    def getObjectDataFiles(self,objects,wait=False):
        """Assumes that all objects passed in are associated with the datafiles that will be generated and of the same type/have the same protocols"""
        try: objects.__iter__
        except: objects=(objects,)
        obj=objects[0]
        if wait:
            input('press any key to start collecting datafiles for %s'%obj.__class__.__name__)
        for protocol in obj.protocols:
            datafile=obj.protocol_runner(protocol) #TODO this should commit the datafile to the database or raise an error
            datafile.subjects.extend(objects) #TODO look up whether this actually commits...
            self.getObjectMetaData(datafile)
            self.session.commit()

    
class ExampleExp(BaseExp):
    #FIXME this pattern may not work if other parts of the program also need to use the database.models... but as long as we aren't running the same experiments then it *should* be ok to monkey patch those? it's dirty... but...
    from database.models import Experiment
    from database.models import Subject
    from database.models import Subject as SubjectChild
    from database.models import DataFile
    from rig.metadatasources import mdsAll()

    mdsDict=mdsAll(2)

    Experiemnt.metadatasource_names=['ALL THE KEYS']

    #metadata should only be collected once per subject for this kind of experiment another pattern with repeated collection would use different run logic
    Subject.metadatasource_names=['ALL THE KEYS']  #FIXME this wont work the way I want it to? or will it? well... maybe it will!??!
    SubjectChild.metadatasource_names=['ALL THE KEYS'] #FIXME make sure that this works, I think it will

    SubjectChild.protocol_runner=None
    SubjectChild.protocols=['ALL THE FILENAMES OR WHATEVER THE RUNNER TAKES eg voltage time serries like I have for the LED']

    DataFile.metadatasource_names=['ALL THE KEYS'] #FIXME this can't handle different data files per subject type... with different metadata
    SubjectChild.DataFile=DataFile #FIXME need to do something about datafile types... or something still...

    Subject.child_type=SubjectChild

    #declare relationships here
    #binding happens at init

class AlternateExampleExp(BaseExp):
    #FIXME this pattern may not work if other parts of the program also need to use the database.models... but as long as we aren't running the same experiments then it *should* be ok to monkey patch those? it's dirty... but...
    from database.models import Experiment
    from database.models import Subject
    from database.models import Subject as SubjectChild
    from database.models import DataFile
    from rig.metadatasources import mdsAll()

    mdsDict=mdsAll(2)

    Experiemnt.metadatasource_names=['ALL THE KEYS']
    Experiment.protocol_names=['keys of external datafiles to run or something']
    Experiment.getPreData=lambda: None
    Experiment.getInterData=lambda: None
    Experiment.getPostData=lambda: None

    #metadata should only be collected once per subject for this kind of experiment another pattern with repeated collection would use different run logic
    Subject.metadatasource_names=['ALL THE KEYS']  #FIXME this wont work the way I want it to? or will it? well... maybe it will!??!
    Experiment.protocol_names=['keys of external datafiles to run or something']
    Subject.getPreData=lambda: None
    Subject.getInterData=lambda: None
    Subject.getPostData=lambda: None

    #FIXME this works if I keep inheritance, what happens if that changes becasue of a proliferation of subjects?
    SubjectChild.metadatasource_names=['ALL THE KEYS'] #FIXME make sure that this works, I think it will
    SubjectChild.protocol_names=['keys of external datafiles to run or something']
    SubjectChild.getPreData=lambda: None
    SubjectChild.getInterData=lambda: None
    SubjectChild.getPostData=lambda: None

    #FIXME FIXME the protocol is what needs to have this I think, not the DataFile? because it will vary per datafile...

    Subject.child_type=SubjectChild

    #declare relationships here
    #binding happens at init


class MatingRecord(BaseExp):
    from database.models import Experiment
    from database.models import Mouse
    name = 'mating record'
    abbrev = 'mr'

    #FIXME it might be nice to have an option to add a new experiment to a subject...
    #since it might have already been found

    def add_subjects_by_id(self,ids): #FIXME an extensible way to validate that the set of root subjects is valid for a given experiment TODO
        if len(ids) != 2:
            raise AttributeError('mrs require a male and a female subject')
        subjects=self.session.query(Subject).filter(Subject.id.in_(ids)).all()
        sexes=[subject.sex_id for subject in subjects]
        if not sexes.count('m')==sexes.count('f'):
            raise AttributeError('mrs require a male and a female subject')


class ESPCalibration(BaseExp):
    """Oh look! calibrations are just experiments on hardware! subject type! hardware! lol"""
    pass


class PatchExp(BaseExp):
    #FIXME rigIO should be contain these? or be contained? how do we want to launch these?
    #by giving rigIO and experiment dict with keys bound? probably not? but then we need a way to seemelessly spawn new experiments from the keyboard and recover them...
    #there is better encapsulation if we just use an existing rigIO, but somehow that suggests that rigIO itself should be calling experiments... I think rigIO needs to be the base and these need to be added
    #which means I need to formalize the interfaces between them
    #RESPONSE: actually it is sort of nice to have it work both ways incase something goes wrong and I need to start where I left off I can just load up an experiment and give it an existing rigIO...
    name='in vitro patch'
    abbrev='patch'
    repository_url='file:///C:/asdf/test' #FIXME there is no verification here... and need a way to update
    #hardware etc can be connected up elsewhere once the basics are created here to keep things simple

    from rig.metadatasources import mccBindAll,espAll
    mdsDict={}
    mdsDict.update(mccBindAll(0)) #FIXME this mdsDict is nice, and we might/probably want to use it along with some of the keybinds stuff in some cases??
    mdsDict.update(mccBindAll(1))
    mdsDict.update(espAll())
    #printFD(mdsDict)

    def run(self):
        self.ExpFromType()
        #get mouse
        #get slice loop
            #get slice metadata
                #get appos
            #get cells loops
                #cell n 
                    #get cell metadata
                        #espX
                        #espY
                        #trmZ
                        #trmRFP
                        #trmGFP
                    #someday take a picture
                #make recordings
                    #set mcc state
                    #set pro file
                    #record file
                    #get filename
                    #make datafile
                    #get datafilemetadata


#Slice Prep
#Patch
#IUEP
#ChrSom
#Histology
#WaterRecords


def main():
    from rig.rigcontrol import rigIOMan
    from rig.keybinds import keyDicts
    rigIO=rigIOMan(keyDicts)
    pe=PatchExp(rigIO) #FIXME somehow this is ass backward at the moment...
    printFD(se.mdsDict)

if __name__=='__main__':
    main()

