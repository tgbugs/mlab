#!/usr/bin/env python3.3
"""Main file for database stuff
Usage:
    main.py [(-e | --echo) (-p | --pgsql) (-w | --wipe) (-s | --setup) (-t | --test) (-i | --ipython)]
    main.py (-h | --help )

Options:
    -h --help       show this
    -e --echo       enable echo
    -p --pgsql      use postgres
    -w --wipe       wipe the database
    -s --setup      setupDB
    -t --test       run tests
    -i --ipython    drop into ipython after everything else is done
"""
from docopt import docopt

from datetime import datetime

from sqlalchemy                 import create_engine
from sqlalchemy.orm             import Session
from sqlalchemy.orm             import aliased
from sqlalchemy.engine          import Engine

from database.models            import *
from database.models.base       import initDBScience
from database.engines           import sqliteMem, pgTest
from database.setupDB           import populateConstraints, populateTables
from database.TESTS             import run_tests
from database.table_logic       import logic_StepEdge

try:
    import rpdb2
except:
    pass

from debug                      import TDB,ploc

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdboff=tdb.tdbOff

###-------------
###  print stuff
###-------------
def printStuff(cons=True,mice=True,data=True,notes=True):
    if cons:
        print('\n###***constraints***')
        [printD(c,'\n') for c in session.query(SI_PREFIX)]
        [printD(c,'\n') for c in session.query(SI_UNIT)]
        [printD(c,'\n') for c in session.query(SEX)]
        [printD(c,'\n') for c in session.query(HardwareType)]

    if mice:
        print('\n###***mice***')
        for mouse in session.query(Mouse):
            print('\n',mouse)
        print('\n###***sires***')
        for s in session.query(Sire):
            print('\n',s)
        print('\n###***dams***')
        for d in session.query(Dam):
            print('\n',d)
        print('\n###***MatingRecords***')
        for mate in session.query(MatingRecord):
            print('\n',mate)
        print('\n###***Litters***')
        for lit in session.query(Litter):
            print('\n',lit)
    if data:
        for d in session.query(DataFile):
            #print('\n',[t for t in d.__dict__.values()])
            print('\n',[t for t in d.experiment.person.__dict__.values()])

    if notes:
        for note in session.query(Note):
            print('\n',note)


###----------
###  Test it!
###----------

def main(echo=False,postgres=False,wipe_db=False,setupDB=False,test=False):
    #create engine
    if postgres: #FIXME THIS HURTS ME OW OW OW
        engine=pgTest(echo=echo,wipe_db=wipe_db)
        if setupDB:
            session=initDBScience(engine) #imported from base.py via *
            #add table logic
            logic_StepEdge(session)
            #populate constraint tables
            populateConstraints(session)
            populateTables(session)
        else:
            session=Session(engine) #imported from base.py via *
            #add table logic
            logic_StepEdge(session)
    else:
        engine=sqliteMem(echo=echo) #XXX sqlite wont autoincrement compositie primary keys >_< DERP
        session=initDBScience(engine) #imported from base.py via *
        #add table logic
        logic_StepEdge(session)
        #populate constraint tables
        populateConstraints(session)
        populateTables(session)

    #do some tests!
    if test:
        try:
            run_tests(session)
            pass
        except:
            raise
            print('tests failed')

    #print stuff!
    printStuff(cons=0,mice=0,data=0,notes=0)

    #query stuff
    #queryAll(session)
    #session.query(Cell).all()
    return session

    
if __name__=='__main__':
    args=docopt(__doc__, version='Main .0002')
    #global ipython #FIXME LOL MASSIVE HACK
    session=main(args['--echo'],args['--pgsql'],args['--wipe'],args['--setup'],args['--test']) #THAT WAS EASY
    if args['--ipython']:
        from rig.ipython import embed
        embed()
