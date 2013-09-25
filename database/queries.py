from database.models import *

def q(session):
    s=session
    #really bad way to find datafiles for experiment n
    n=1
    s.query(DataFile).filter(DataFile.subjects.any(id=s.query(Experiment).filter_by(id=n)[0].subjects[1].id))
    #FIXME this does not hit the whole experiment

    #FUKKEN MAGIC BABY gets all datafiles in an experiment
    s.query(DataFile).join((Subject, DataFile.subjects)).join((Experiment, Subject.experiments)).filter(Experiment.id==1).all()
