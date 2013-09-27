from database.main import *
#from database.models import *
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import object_session

def q(session):
    s=session
    #really bad way to find datafiles for experiment n
    n=1
    s.query(DataFile).filter(DataFile.subjects.any(id=s.query(Experiment).filter_by(id=n)[0].subjects[1].id))
    #FIXME this does not hit the whole experiment

    #FUKKEN MAGIC BABY gets all datafiles in an experiment
    s.query(DataFile).join((Subject, DataFile.subjects)).join((Experiment, Subject.experiments)).filter(Experiment.id==1).all()

def getDataFiles(experiment):
    return object_session(experiment).query(DataFile).join((Subject, DataFile.subjects)).join((Experiment, Subject.experiments)).filter(Experiment.id==experiment.id)

def qTree(session):
    #fucking mess in here
    #session=object_session(hardware)

    sub_hardware=session.query(Hardware.sub_components,Hardware.id).filter(Hardware.id==1).cte(name='sub_hardware',recursive=True)
    #sub_hardware=session.query(Hardware.id).filter(Hardware.id==1).cte(name='sub_hardware',recursive=True)

    sub_a=aliased(sub_hardware, name='sh')
    hw_a=aliased(Hardware, name='h')
        
    sub_hardware=sub_hardware.union_all(session.query(hw_a.id,hw_a.sub_components).filter(hw_a.id==sub_a.c.sub_components))


    q=session.query(sub_hardware.c.sub_components)
    return q
