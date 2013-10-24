#from database.main import *
import inspect as ins
from database.models import *
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


#queries to sort subjects by whether they have a certain property
def hasProperty(session,Object,key):
    return session.query(Object).join((Object.Properties,Object.properties.local_attr)).filter_by(key=key)

def hasKVPair(session,Object,key,value):
    return session.query(Object).join((Object.Properties,Object.properties.local_attr)).filter(Object.Properties.key==key,Object.Properties.value==value)

def queryAll(session):
    from database import models
    s=session
    #[s.query(models.__dict__[a]).all() for a in models.__all__] #AWEYISS 
    for a in models.__all__:
        print(s.query(models.__dict__[a]).all())
        try:
            print(s.query(models.__dict__[a].MetaData).all())
        except AttributeError:
            pass

def dirAll(session):
    from database import models
    s=session
    #[s.query(models.__dict__[a]).all() for a in models.__all__] #AWEYISS 
    things=models.__all__
    things=[thing for thing in things]# if thing is not 'Sire' and thing is not 'Dam' and thing is not 'Mouse']
    print(things)
    for a in things:
        try:
            thing=s.query(models.__dict__[a]).all()
            if thing:
                print('---------------------%s---------------------\n\n'%thing[0])
                dir_=[t for t in thing[0].__dir__() if t[0]!='_']
                for attr in dir_:
                    iat=getattr(thing[0],attr)
                    if ins.isclass(iat):
                        try:
                            more_thing=session.query(iat).all()
                        except:
                            print(attr,'=',iat)
                            continue
                        if more_thing:
                            mtdir=[t for t in more_thing[0].__dir__() if t[0]!='_']
                            print('\t-----meta------------%s---------------------\n\n'%(more_thing[0]))
                            for attr_ in mtdir:
                                miat=getattr(more_thing[0],attr_)
                                if ins.ismethod(miat):
                                    print('\t',attr_,'=',miat())
                                else:
                                    print('\t',attr_,'=',miat)
                            print('\t-----meta------------END---------------------\n\n')

                    elif ins.ismethod(iat):
                        print(attr,'=',iat())
                    else:
                        print(attr,'=',iat)
        except: raise
        #try:
            #thing=s.query(models.__dict__[a].MetaData).all()
            #if thing:
                #dir_=[t for t in thing[0].__dir__() if t[0]!='_']
                #[print(attr,'=',getattr(thing[0],attr)) for attr in dir_]
        #except AttributeError: pass


