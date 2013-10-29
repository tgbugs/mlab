from database.imports import *
from database.base import Base


class StepNode(Base): #steps are verbs, what we want here are actually their outcomes being true... eg that there is actually a batch of ACSF that exists
    id=

class InstalledNode(Base): #we have this so we can check it once on startup? but there are functions for each bloody step that are conditional... but in database that would mean buttload of check constraints on foriegn keys...
#unfortunately each 'node' is being treated as its own class :/.... but many steps actually have the same code and all that changes are the readers and the writers... can't sort those by name :/ and that makes the tree non-static
    id=Column(Integer,primary_key=True)
    dependencies=None #m-m on self... check mixins risk of circularity w/ this...
    #dictionary with key=name and values = names of dependencies...
    #transformed into functions...
    #but then also need to tie in subjects, which is really hard using a dict :/
    #damn it each step needs to be a class :( :( :( unless we can build them on the fly
    #{'key':(['list of deps'],StepFactory)} #seems like a bad idea?? hard for people to use
    
    #steps exist to facilitate the reuse of datasources...



