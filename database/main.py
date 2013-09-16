#Base file for creating the tables that I will use to store all my (meta)data

#__table_args__ = {'extend_existing':True} #XXX useful!
#FIXME somehow still circular deps here...
#from database.constraints import *
#from database.notes import *
#from database.experiments import *
#from database.inventory import *
#from database.people import *
#from database.mice import *

#TODO therefore we need a 'convert local to utc for storage'
#TODO start moving stuff out of here that we don't use to define the tables
#TODO watch out for sqlite_autoincriment=True needed when using composite keys!
#TODO going to need the 'PRAGMA foreign_keys=ON' ???
#TODO I can just store the bloody python code used to calculate the values in another column... >_<, that will allow for consistnecy check even if code changes
#TODO install git you asshole
#TODO aleks says overnormalization is just stuipd for this?

#TODO conform to MINI, NIF ontologies?, or odML terminiologies?

#TODO autogenerate ALL THE DATES based on startDateTime
#table of projected dates which has: estimated and actual pairs for each one
#but we don't really need that information stored because we can just generate it

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

from datetime import datetime

from sqlalchemy                 import event
from sqlalchemy                 import MetaData
from sqlalchemy                 import create_engine
from sqlalchemy.orm             import Session #scoped_session, sessionmaker
from sqlalchemy.engine          import Engine

from database.constraints       import *
from database.experiments       import *
from database.inventory         import *
from database.people            import *
#from database.notes             import * #FIXME exceptionally broken at the moment #FIXME why does this still import when commented out! maybe an artifact of having it linked to Base in base.py?!?!?
from database.mice              import *
from database.data              import *

from database.TESTS             import run_tests
from database.base              import Base #FIXME this has to go last!???! so that all the rest are attached?

try:
    import rpdb2
except:
    pass

from debug                      import TDB,ploc

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdboff=tdb.tdbOff

###----------
###  Test it!
###----------

def main():
    #test globals
    #ploc(globals())

    #setup the engine
    echo=True
    #echo=False

    #engine = create_engine('postgresql://sqla:asdf@localhost:54321/postgres',echo=echo)
    #con=engine.connect()
    #con.execute('commit')
    #con.execute('drop database if exists db_test')
    #con.execute('commit')
    #con.execute('create database db_test')
    #con.execute('commit')
    #con.close()
    #del(engine)

    engine = create_engine('postgresql://sqla:asdf@localhost:54321/db_test',echo=echo)
    #event.listen(engine,'connect',set_sqlite_pragma)

    #create metadata and session

    Base.metadata.drop_all(engine,checkfirst=True)
    #return None
    #TODO schema option
    
    Base.metadata.create_all(engine,checkfirst=True)

    session = Session(engine)

    #populate constraint tables
    populateConstraints(session)

    #do some tests!
    run_tests(session)


    if 0:
        print('\n###***constraints***')
        [printD(c,'\n') for c in session.query(SI_PREFIX)]
        [printD(c,'\n') for c in session.query(SI_UNIT)]
        [printD(c,'\n') for c in session.query(SEX)]

    if 0:
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
    if 0:
        for d in session.query(DataFile):
            #print('\n',[t for t in d.__dict__.values()])
            print('\n',[t for t in d.experiment.person.__dict__.values()])

        #for note in session.query(Note):
            #print('\n',note)

    #input('hit something to exit')
    
if __name__=='__main__':
    main()
