"""Streamlined file for testing postgres stuff in ipython
Usage:
    main.py [(-e | --echo) (-t | --test)]
    main.py (-h | --help )
Options:
    -e --echo       enable echo
    -t --test       run tests and exit
"""
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

#tests
if args['--test']:
    dirAll(s)
    #t_steps(s,100)
    #s.commit()
    #print(session.query(Step).all())
    #t_edges(s)

#give me some ipython!
else:
    embed()
