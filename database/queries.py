from database.models import *

def q(session):
    s=session
    #really bad way to find datafiles for experiment n
    n=1
    s.query(DataFile).filter(Datafile.subjects.any(id=s.query(Experiment).filter_by(id=n)[0].subjects[1].id))

