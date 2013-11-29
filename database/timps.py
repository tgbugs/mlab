#!/usr/bin/env python3.3
"""Streamlined file for testing postgres stuff in ipython
Usage:
    main.py [(-e | --echo) (-i | --ipython) (-s | --steps) (-r | --rio-start)]
    main.py (-h | --help )
Options:
    -e --echo       enable echo
    -i --ipython    embed
    -s --steps      test all steps 
    -r --rio-start  start the rig io manager (capture key input)
"""
#-t --test       run tests and exit
from docopt import docopt
#from IPython import embed
from database.TESTS import *
#from database.steps import *
#from database.dataio import Get,Set,Bind,Read,Write,Analysis,Check
#from rig.ipython import embed
from rig.rigcontrol import rigIOMan, keyDicts
from database.real_steps import *
from database.steps import StepRunner, StepCompiler
from database.models import *
from database.engines import *
from database.queries import *
from database.table_logic import *
from database.main import printFD
from sqlalchemy.orm import Session
args=docopt(__doc__)
engine=pgTest(args['--echo'])
session=Session(engine)
s=session


#session type
dbtype=session.connection().engine.name #dialect.name??
#FIXME use this to change how models import??

#table logic
logic_StepEdge(session)

#load up the stuff we need to test dataios and steps
rio=rigIOMan(keyDicts, session)#, globals())
if args['--rio-start']:
    rio.start()

#deal with steps
iStepDict={}
printFD(stepDict)
for name,step in stepDict.items():
    #printD(name,step.__name__)
    iStepDict[name.lower()]=step(session,ctrlDict=rio.ctrlDict)
locals().update(iStepDict)
#iStepDict=stepDict

#sc=StepCompiler(bind_pia_xys,stepDict)
#FIXME use ExperimentType???
#sr=StepRunner(session,bind_pia_xys,stepDict,rio.ctrlDict, session.query(Experiment).all()[10])
#sr.do() #DUN DUN DUN!
#rio.pass_locals(locals()) #FIXME some stuff seems to be missing...

if args['--steps']:
    for step in iStepDict.values():
        try:
            sr=StepRunner(session,step,stepDict,rio.ctrlDict, session.query(Experiment).all()[10])
            sr.do()
        except (NotImplementedError,KeyError) as e: #XXX this masks many diverse errors... given how much I use dicts...
            #raise
            pass
        rio.pass_locals(locals()) #FIXME some stuff seems to be missing...

#get_at_desired_xy.do()

#give me some ipython!
if args['--ipython'] and not args['--rio-start']:
    embed() #just hit i if you want it

#tests
else:# args['--test']:
    dirAll(s) #FIXME NOTE: __dir__ does not work in 3.2 for some reason >_<
    #t_steps(s,100)
    #s.commit()
    #print(session.query(Step).all())
    #t_edges(s)

#cleanup! #just it @ and it will close properly
#rio.cleanup() #FIXME this should be handled internally in rio probs w/ a wrapper for with as:
