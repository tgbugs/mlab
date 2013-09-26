class ExperimentRunner:
    def __init__(self,mcc,clx,esp,dat):
        self.clx=clx
        self.CLX=clx.controller
        self.dat=dat
        self.DAT=dat.controller
        self.esp=esp
        self.ESP=esp.controller
        self.mcc=mcc
        self.MCC=mcc.controller
        

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

