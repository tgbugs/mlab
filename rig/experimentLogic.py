from database.models import Experiment, Subject, Mouse, Slice, Cell
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
    def __init__(self,rigIO,Experiment=None,ExperimentType=None):
        if not checkExpType(ExperimentType):
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
                self.ExperimentType=self.session.query(ExperimentType).\
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

        self.imdsDict={}
        for MDS in self.mdsDict.values():
            self.imdsDict[MDS.__name__[4:]]=MDS(rigIO.ctrlDict[MDS.ctrl_name],self.session)

    def checkExpType(self,ExperimentType)
        if ExperimentType: #implies that there is a session elsewhere...
            if ExperimentType.id:
                names=[mds.name for mds in ExperimentType.metadatasources]
                try:
                    if self.name!=ExperimentType.name:
                        raise AttributeError('Defined name does not match that of ExperimentType!')
                    elif list(self.mdsDict.keys()).sort()!=names.sort():
                        raise AttributeError('Defined metadatasources do not match those in ExperimentType. Create a new experiment so the updated metadatasources can be persisted in a new ExperimentType.')
                except:
                    from rig.metadatasources import mdsAll
                    self.mdsDict={}
                    [self.mdsDict.update({name:cls}) for name,cls in mdsAll().item() if names.count(name[4:])]
                self.ExperimentType=ExperimentType
                #TODO get session from ExperimentType
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

    def Persist(self):
        #TODO damn this is such a better idea...
        mds=[m.MetaDataSource for m in self.imdsDict.values()] #FIXME check for changes and update w/ version
        self.ExperimentType=ExperimentType(name=self.name,repository_url=self.repository_url,MetaDataSources=mds)
        self.session.add(self.ExperimentType)
        self.session.commit() #FIXME/TODO as opposed to flush??!
        return self

    def getSubjects(self):
        #TODO
        return self
    
    def ExpFromType(self):
        #TODO
        Experiment(self.ExperimentType,person_id=,project_id=) #reagents? subjects? TODO
        self.experiment=None
        return self



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



    #experiment=Experiment() #FIXME or should this be ExperimentType... somehow I think it should...
    #experimentType=ExperimentType() #TODO make sure that we can easily construct new experiments from exptype

def main():
    from rig.rigcontrol import rigIOMan
    from rig.keybinds import keyDicts
    rigIO=rigIOMan(keyDicts)
    pe=PatchExp(rigIO) #FIXME somehow this is ass backward at the moment...
    printFD(se.mdsDict)

if __name__=='__main__':
    main()

