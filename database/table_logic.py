#events/triggers go here
from sqlalchemy import event
from sqlalchemy.orm import object_session
from database.models import Experiment

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
