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
    #defintion of mdsDict should go up here

    def __init__(self,rigIO,Experiment=None):
        #check for things we're supposed to have
        try: self.name
        except: raise AttributeError('experiment definitions require a name')
        try: self.abbrev
        except: self.abbrev=None
        try: self.repository_url
        except: self.repository_url=None

        self.session=rigIO.Session() #a single experiment (even if long) seems like a natural scope for a session
        try:
            self.ExperimentType=self.session.query(ExperimentType).filter_by(id=self.name)[0]
        except:
            self.Persist()

        if Experiment: #resume experiment and override the default defined in child classes but check type
            if Experiment.type==self.ExperimentType.id:
                self.experiment=Experiment
            else:
                self.ExpFromType()
        #self.current_subjects=[] #TODO

        self.imdsDict={}
        for MDS in self.mdsDict.values():
            self.imdsDict[MDS.__name__[4:]]=MDS(rigIO.ctrlDict[MDS.ctrl_name],self.session)

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
        self.ExperimentType=ExperimentType(id=self.name,repository_url=self.repository_url)
        self.session.add(self.ExperimentType)
        self.session.commit() #FIXME/TODO as opposed to flush??!
        return self

    def getSubjects(self):
        #TODO
        return self
    
    def ExpFromType(self):
        #TODO
        return self



class PatchExp(BaseExp):
    name='in vitro patch' #FIXME this should probably match the class name???
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

