#from database.main import *
import inspect as ins
from database.models import *
from sqlalchemy import or_, and_
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
    """DUMP ALL THE THINGS"""
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
                for subthing in thing[:2]:
                    dir_=[t for t in subthing.__dir__() if t[0]!='_']
                    for attr in dir_:
                        iat=getattr(subthing,attr)
                        if ins.isclass(iat):
                            try:
                                more_thing=session.query(iat).all()
                            except:
                                print(attr,'=',iat)
                                continue
                            if more_thing:
                                for submore in more_thing[:2]:
                                    mtdir=[t for t in submore.__dir__() if t[0]!='_']
                                    print('\t-----meta------------%s---------------------\n\n'%(submore))
                                    for attr_ in mtdir:
                                        miat=getattr(submore,attr_)
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

def getSusTru(stepedge,session): #XXX used in table_logic
    #FIXME the proper way to do this is by alisasing StepTC
    start=stepedge.step_id
    end=stepedge.dependency_id

    sus_1=session.query(StepTC.step_id,StepTC.tc_id).filter(
            or_( StepTC.step_id==end, #edges starting at deleted edge
            StepTC.tc_id==start )) #edges ending at deleted edge
    sus_2=session.query(StepTC.step_id, StepEdge.dependency_id).filter(
            and_( StepTC.tc_id==start, StepEdge.dependency_id==end ))
    sus_3=session.query(StepEdge.step_id, StepTC.tc_id).filter(
            and_( StepTC.step_id==end, StepEdge.step_id==start ))
    sus_4=session.query(StepTC.step_id,StepTC.tc_id).filter(
            StepTC.step_id==start,
            StepTC.tc_id==end )

    suspects=sus_1.union(sus_2,sus_3,sus_4)

    deleted=session.query(StepEdge.step_id,StepEdge.dependency_id).filter(
            StepEdge.step_id == start,
            StepEdge.dependency_id == end )
    all_but_del=session.query(StepEdge.step_id,StepEdge.dependency_id).except_(deleted)
    trusty=session.query(StepTC.step_id,StepTC.tc_id).except_(suspects).union(all_but_del)
    t1=aliased(StepTC,trusty.subquery())
    t2=aliased(StepTC,trusty.subquery())
    t3=aliased(StepTC,trusty.subquery())
    trusty_obj=aliased(StepTC,trusty.subquery()) #tru_a will now behave as a table
    t1t2=session.query(t1.step_id,t2.tc_id).filter(t1.tc_id == t2.step_id) #join paths
    t2t3=session.query(t1.step_id,t3.tc_id).filter(and_(t1.tc_id == t2.step_id,
                                                        t2.tc_id == t3.step_id )) #join paths
    new_tc=t1t2.union(t2t3)

    to_delete=session.query(StepTC).except_(new_tc)

    return suspects,trusty,new_tc,to_delete

    #suspects=sus_1.union(sus_2).union(sus_3).union(sus_4) #indistinguishable from the above

    #s1=set(sus_1.all())
    #print('s1')
    #s2=set(sus_2.all())
    #print('s2')
    #s3=set(sus_3.all())
    #print('s3')
    #s4=set(sus_4.all())
    #print('s4')
    #out=s1.union(s2).union(s3).union(s4)
    #return out

def getSuspects(session):
    edges=session.query(StepEdge).all()
    for edge in edges:
        sus,tru,ntc,tod=getSusTru(edge,session)
        s=sus.order_by(StepTC.step_id).all()
        t=tru.order_by(StepTC.step_id).all()
        n=ntc.order_by(StepTC.step_id).all()
        d=tod.order_by(StepTC.step_id).all()
        print('edge:',repr(edge))
        print('sus :',s)
        print('trus:',t)
        print('new :',n)
        print('del :',d)



