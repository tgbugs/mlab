from database import interface #FIXME

class ExperimentRunner:
    def __init__(self,termIO,clxCtrl,espCtrl,mccCtrl,termIO):
        self.clx=clxCtrl
        self.esp=espCtrl
        self.mcc=mccCtrl
        #FIXME use input() to get terminal input for stuff like depth?

        self.currentStateDict={ #this is preferable to having each thing be assigned individually to self, in fact we could even pass something like this in
            'Experiment':None,
            'Subjects':[], #NOTE somehow cells and slices go here for patch
                               #slices need to be added to mouse @ sliceprep? 


        }
    def newExpFromLast(self):
        pass
    def newSubFromLast(self):
        #TODO this needs to handle subject hierarchies transparently
        #fortunately the orm should handle this without too much effort?
        pass

    def newExpFromTemp(self):
        pass
    def newSubFromTemp(self):


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

    def getCurrentHardware(self,root='Tom\'s Rig')):
        self.session.query(Hardware).filter_by()
        
    def newExperiment(self):
        hardware=getCurrentHardware(root)
        experiment=Experiment(project_id=self.project_id,person_id=self.person_id)
        self.session.add
    session.Experiment
    Mouse
    Slice
    Cells


class SomChr(ExperimentRunner):
    def newSlice(self):
        Slice()



class BaseExp:
    #defintion of mdsDict should go up here
    def __init__(self,termIO):
        mdsDict={}
        for MDS in self.mdsDict:
            mdsDict[MDS.__name__[4:]]=MDS(termIO.ctrlDict[MDS.ctrl_name],session)
        self.mdsDict=mdsDict

class SliceExp(BaseExp):
    self.mdsDict={}
