#events/triggers go here
#TODO personally I reccomend a strongy worded warning against creating sessions
    #to access the database directly via sqlalchemy, I need my own that hav
    #the event listeners added automatically to the session
from numpy import array
from sqlalchemy import event
from sqlalchemy.orm import object_session
from database.models import Experiment, StepEdge, StepEdgeVersion

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

def logic_StepEdge(session): #FIXME this does not seem to be working properly...
    """ Enforce DAG for step dependency tree"""
    @event.listens_for(session,'before_flush') #FIXME why does this trigger on session.add??!
    def history_table_delete(session,flush_context,instances):
        #print(session.new,session.deleted) #FIXME this reveals a number of problems in __repr__s around the db
        for obj in session.deleted:
            if type(obj) is StepEdge:#isinstance preferred IF I subclass StepEdge (very unlikely)
                session.add(StepEdgeVersion(step_id=obj.step_id,dependency_id=obj.dependency_id,added=False))
                #hrm the above could create a list of cycle enducing edges... given all else constant...
            elif type(obj) is StepEdgeVersion:
                session.expunge(obj) #this should prevent the delete
                raise AttributeError('StepEdgeVersion is write only!')
        for obj in session.new:
            if type(obj) is StepEdge:
                #print('wtf m8!') #FIXME this is being called waaay too much
                session.add(StepEdgeVersion(step_id=obj.step_id,dependency_id=obj.dependency_id,added=True))


    @event.listens_for(session,'before_attach')
    def check_for_cycles(session,instance): #FIXME monumentally slow for repeated adds and high edge counts
        if type(instance) is StepEdge:
            #FIXME since this is now called at before_attach the edge cannot find itself!
            edges=session.query(StepEdge.step_id,StepEdge.dependency_id).all() #ICK horrible for repeatedly adding edges :/
            edge_tuple=(instance.step_id,instance.dependency_id)
            if edge_tuple in edges:
                raise ValueError('Edge already exists!') #FIXME
            edges.append(edge_tuple)
            def makeDepDict(edges):
                #edges=array(edges)
                depDict={}
                #revDepDict={}
                for step,dep in edges:
                    depDict[step]=set((dep,))
                    #revDepDict[dep]=set((step,))
                for step,dep in edges:
                    depDict[step].add(dep)
                    #revDepDict[dep].add(step) #this is fucking stupid
                return depDict#,revDepDict

            def topoSort(depDict,revDepDict):
                #edges=array(edges)
                #starts=[node for node in edges[:,0] if edge not in edges[:,1]]
                starts=[node for node in depDict.keys() if node not in revDepDict.keys()]
                #print(starts)
                L=[] #our sorted list
                while starts:
                    node=starts.pop()
                    L.append(node)
                    discards=set()
                    #print(depDict.keys(),node)
                    try:
                        for m in depDict[node]:
                            revDepDict[m].discard(node)
                            discards.add(m)
                            if not revDepDict[m]:
                                starts.append(m)
                        depDict[node].difference_update(discards)
                    except KeyError:
                        pass #the node is a leaf and thus not in depDict
                check=set()
                (check.update(v) for v in depDict.values())
                (check.update(v) for v in revDepDict.values())
                if check:
                    raise TypeError('NOT ACYCLIC!!')
                else:
                    return L

            depDict=makeDepDict(edges)
            if not len(edges): #in the one time event that there are no edges
                return False
            def cycle(start,node):
                if node==start:
                    return True
                #TODO this *might* be faster with a transitive closure query, but srsly?
                #deps=edges[:,1][edges[:,0]==node] #FIXME this seems to be the culpret for the slow down
                #TODO better to see if start is in the TC of start aka if step_id in TC of dep_id
                    #don't need this right now since most scientific protocols dont have massive x-deps
                #print('node %s dependencies'%node,deps)
                try:
                    if start in depDict[node]:
                        return True
                    else:
                        for n in depDict[node]: #TODO make this threaded? OR use lists sorted by connectivity
                            if cycle(start,n): #nasty stack overflow here
                                return True
                        return False
                except KeyError:
                    return False
            #if session.query(StepEdge).get(instance.step_id,instance.dependency_id):
                #session.delete(instance)
                #session.flush()
                #raise BaseException('Edge already exists, saving you a nasty backtrace!')
            print('Checking if edge %s -> %s would add cycle!'%(instance.step_id,instance.dependency_id))
            #try:
                #print(topoSort(*makeDepDict(edges))) #slow as balls
            #except:
                #raise
                #raise ValueError('[!] Edge %s -> %s would add cycle! Not adding!'%(instance.step_id,instance.dependency_id))

            if cycle(instance.step_id,instance.dependency_id):
                #FIXME I don't want to roll back the whole session here do it?!
                #session.delete(instance) #XXX apparently delete autoflushes!??!
                #print('deleted?')
                #session.flush() #FIXME this will trigger history_table_delete
                raise ValueError('[!] Edge %s -> %s would add cycle! Not adding!'%(instance.step_id,instance.dependency_id))
                #FIXME HORRENDOUSLY SLOW as edge count grows

#TODO add the history part too!
