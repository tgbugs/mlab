#!/usr/bin/env python3.3
"""Streamlined file for testing postgres stuff in ipython
Usage:
    main.py [(-e | --echo) (-i | --ipython)]
    main.py (-h | --help )
Options:
    -e --echo       enable echo
    -i --ipython    embed
"""
#-t --test       run tests and exit
from docopt import docopt
from IPython import embed
from database.TESTS import *
from database.steps import *
from database.dataio import Get,Set,Bind,Read,Write,Analysis,Check
from database.models import *
from database.engines import *
from database.queries import *
from database.table_logic import *
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

#give me some ipython!
if args['--ipython']:
    embed()

#tests
else:# args['--test']:
    dirAll(s) #FIXME NOTE: __dir__ does not work in 3.2 for some reason >_<
    #t_steps(s,100)
    #s.commit()
    #print(session.query(Step).all())
    #t_edges(s)

