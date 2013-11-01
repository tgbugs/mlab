#events/triggers go here
from numpy import array
from sqlalchemy import event
from sqlalchemy.orm import object_session
from database.models import Experiment, StepEdge

def listenForThings(session): #FIXME very broken
    """this should be 1:1 with every session where things are automated?? is it better to do this or to do it by hand, I think this is better because I can't miss with it"""
    class Holder:
        def store(self,thing):
            self.thing=thing
        def dump(self):
            return self.thing

    hld=Holder()

    def remover():
        event.remove(Experiment,'init',mds_hw_listen)
        event.remove(session,'after_flush',hld.dump()) #FIXME?

    @event.listens_for(Experiment,'init')#,propagate=True) #no idea what prop does
    def mds_hw_listen(instance,args,kwargs):
        print(args,kwargs)
        session.add(instance)
        def got_id(session,flush_context):
            print(instance)
            try:
                for mds in instance.type.metadatasources: #FIXME test to see if we can get stuff from args/kwargs
                    session.add(instance.id,mds.id,mds.hardware_id)
                    session.flush()
            except:
                print('it would seem your exp doesnt have a type or the type has not mdses, what kind of experiment is this!?')
                #raise
            finally:
                pass
                #rem_got_id() #FIXME why does this... fail on Project...?
        hld.store(got_id)
        event.listen(object_session(instance),'after_flush',got_id,instance)

    return remover

def checkEdges(session): #FIXME this does not seem to be working properly...
    """ Enforce DAG for step dependency tree"""
    @event.listens_for(session,'after_attach')
    def check_for_cycles(session,instance): #FIXME monumentally slow for repeated adds and high edge counts
        if type(instance) is StepEdge:
            edges=array(session.query(StepEdge.step_id,StepEdge.dependency_id).all()) #ICK horrible for repeatedly adding edges :/
            if not len(edges): #in the one time event that there are no edges
                return False
            def cycle(start,node):
                if node==start:
                    return True
                #TODO this *might* be faster with a transitive closure query, but srsly?
                deps=edges[:,1][edges[:,0]==node] #FIXME this seems to be the culpret
                #print('node %s dependencies'%node,deps)
                if start in deps:
                    return True
                else:
                    for n in deps:
                        if cycle(start,n):
                            return True
                    return False
            #if session.query(StepEdge).get(instance.step_id,instance.dependency_id):
                #session.delete(instance)
                #session.flush()
                #raise BaseException('Edge already exists, saving you a nasty backtrace!')
            if cycle(instance.step_id,instance.dependency_id):
                session.delete(instance)
                session.flush()
                raise ValueError('[!] Edge %s -> %s would add cycle! Deleting!'%(instance.step_id,instance.dependency_id))
                #FIXME HORRENDOUSLY SLOW as edge count grows

#TODO add the history part too!
