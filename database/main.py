"""Main file for database stuff
Usage:
    main.py [-e -p -w -s -t -i]
    main.py (-h | --help )

Options:
    -h --help   show this
    -e          enable echo
    -p          use postgres
    -w          wipe the database
    -s          setupDB
    -t          run tests
    -i          open ipython and run everything in it
"""
#FIXME many of the options only apply if postgres is used...
#TODO ipython

#Base file for creating the tables that I will use to store all my (meta)data

#TODO use postgres search_path to control the user so that we can share basic things such as constants and strain information, definately need to audit some of those changes... audit table...

#FIXME holy shit problems with using datetime.now as the default for DateTime!

#TODO when thinking about staging this stuff I need a safe way to hold data incase my access to the db goes down, like pickling something or the like? ideally this shouldn't happen but better safe than sorry

#TODO conform to MINI, NIF ontologies?, or odML terminiologies?

#TODO
### Create an IsLoggable class or the like to manage logging changes to fields
#see: http://stackoverflow.com/questions/141612/database-structure-to-track-change-history
#TODO transaction log will have a first entry for...
#internal doccumentation of the creation date may not be needed if I have refs to transactions

#TODO transfer logs for mice can now be done and incorporated directly with the system for weening etc

#TODO reimplement notes so that they can apply to multiple things like I do with classDOB, but check the overhead, join inheritance might work
#make sure to set the 'existing table' option or something?

#TODO neo io for dealing with abf files, but that comes later
#OBJECTIVE raw data format agnostic, this database does not house the raw data, it houses the assumptions and the results and POINTS to the analysis code and the raw data
#if needs be the code used to analyize the data can be stored and any updates/diffs can be added to track how numbers were produced
#this means that this database stays flexible in terms of what kinds of experiments it can handle
#it also maximizes poratbility between different backend databases
from docopt import docopt

from datetime import datetime

from sqlalchemy                 import create_engine
from sqlalchemy.orm             import Session
from sqlalchemy.orm             import aliased
from sqlalchemy.engine          import Engine

from database.models            import *
from database.models.base       import Base, initDBScience
from database.engines           import sqliteMem, pgTest
from database.setupDB           import populateConstraints, populateTables
from database.TESTS             import run_tests

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

def queryAll(session):
    from database import models
    s=session
    #[s.query(models.__dict__[a]).all() for a in models.__all__] #AWEYISS 
    for a in models.__all__:
        print(s.query(models.__dict__[a]).all())
        try:
            print(s.query(models.__dict__[a].MetaData).all())
        except:
            pass

def dirAll(session):
    from database import models
    s=session
    #[s.query(models.__dict__[a]).all() for a in models.__all__] #AWEYISS 
    things=models.__all__
    things=[thing for thing in things if thing is not 'Sire' and thing is not 'Dam' and thing is not 'Mouse']
    printD(things)
    for a in things:
        try:
            thing=s.query(models.__dict__[a])[-1]
            print('---------------------%s---------------------\n\n'%thing)
            dir=[t for t in thing.__dir__() if t[0]!='_']
            print([getattr(thing,attr) for attr in dir])
        except: pass
        try:
            thing=s.query(models.__dict__[a].MetaData)[-1]
            print('-----meta------------%s---------------------\n\n'%thing)
            dir=[t for t in thing.__dir__() if t[0]!='_']
            print([getattr(thing,attr) for attr in dir])
        except: pass

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

def connect(echo=False):
    return Session(pgTest(echo=echo))

def main(echo=False,postgres=False,wipe_db=False,setupDB=False,test=False):
    #create engine
    if postgres:
        engine=pgTest(echo=echo,wipe_db=wipe_db)
        if setupDB:
            session=initDBScience(engine) #imported from base.py via *
            populateConstraints(session)
            populateTables(session)
        else:
            session=Session(engine) #imported from base.py via *
    else:
        engine=sqliteMem(echo=echo) #XXX sqlite wont autoincrement compositie primary keys >_< DERP
        session=initDBScience(engine) #imported from base.py via *
        populateConstraints(session)
        populateTables(session)

    #create metadata on the engine
    #Base.metadata.drop_all(engine,checkfirst=True)

    #create session
    #session = Session(engine)

    #populate constraint tables

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
    args=docopt(__doc__, version='Main .0001')
    printD(args)
    main(args['-e'],args['-p'],args['-w'],args['-s'],args['-t']) #WOW THAT WAS EASY
