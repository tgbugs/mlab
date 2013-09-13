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
from sqlalchemy                 import create_engine
from sqlalchemy.orm             import Session #scoped_session, sessionmaker
from sqlalchemy.engine          import Engine

from database.base              import init_db
from database.constraints       import *
from database.experiments       import *
from database.inventory         import *
from database.people            import *
from database.notes             import * #FIXME exceptionally broken at the moment
from database.mice              import *
from database.data              import *

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

###----------
###  Test it!
###----------

def makeObjects(session): #OLD AND UNUSED
    import numpy as np
    sex_seed=np.random.choice(2,100,.52)
    sex_arr=np.array(list('m'*100))
    sex_arr[sex_seed==0]='f' #FIXME not used and IN PLACE YOU TARD
    
    #make some notes
    notes=map(str,range(50))

    urdob=DOB(datetime.strptime('0001-1-1 00:00:00','%Y-%m-%d %H:%M:%S'))
    session.add(urdob)
    session.commit()

    #make mice to be sires and dams
    session.add_all([Mouse(eartag=i+300,sex='f',DOB=urdob) for i in range(2)])
    session.add_all([Mouse(eartag=i+200,sex='m',DOB=urdob) for i in range(2)])
    session.commit()

    #session.add_all([[m.notes.append(note) for m in session.query(Mouse)] for note in notes]) #notes.append call should return m? fingers crossed FIXME

    session.add_all([Sire(Mouse=m) for m in session.query(Mouse).filter(200 <= Mouse.eartag, Mouse.eartag < 300)])
    session.add_all([Dam(Mouse=m) for m in session.query(Mouse).filter(300 <= Mouse.eartag, Mouse.eartag < 400)])
    session.commit()

    #make mating records and litters
    mrs=[]
    lits=[]
    n=10
    #make random pairings
    sires=[s for s in session.query(Sire)]
    dams=[d for d in session.query(Dam)]
    sire_arr=np.random.choice(len(sires),n)
    dam_arr=np.random.choice(len(sires),n)
    litter_sizes=np.random.randint(0,20,n) #randomize litter size
    for i in range (n):
        #pick sire and dam at random
        now=datetime.utcnow()
        mr=MatingRecord(Sire=sires[sire_arr[i]],Dam=dams[dam_arr[i]], startDateTime=now+timedelta(hours=i),stopTime=now+timedelta(hours=i+12))
        session.add(mr)
        session.commit() #FIXME problem here

        dob1=DOB(mr.est_e0+timedelta(days=19))
        session.add(dob1)
        session.commit()

        mr.dob_id=dob1.id
        session.add(mr)
        session.commit()

        lit=Litter(MatingRecord=mr,DOB=dob1) #FIXME there is a problem comparing datetimes because they are strings on they way back out >_<
        session.add(lit)
        session.commit()

        session.add_all(lit.make_members(litter_sizes[i]))
        session.commit()


def main():
    #SQLite does not check foreign key constraints by default so we have to turn it on every time we connect to the database
    #the way I have things written at the moment this is ok, but it is why inserting an id=0 has been working
     
    @event.listens_for(Engine, 'connect') #FIXME NOT WORKING!
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    #setup the engine
    #echo=True
    echo=False
    dbPath=':memory:'
    #dbPath='test2' #holy crap that is alow slower on the writes!
    #dbPath='C:\\toms_data\\db_test.db'
    engine = create_engine('sqlite:///%s'%(dbPath), echo=echo) #FIXME, check if the problems with datetime and DateTime on sqlite and sqlite3 modules are present!
    event.listen(engine,'connect',set_sqlite_pragma)

    #create metadata and session
    init_db(engine)
    #session = scoped_session(sessionmaker())
    #session.configure(bind=engine)
    #Session=sessionmaker(bind=engine)

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
        for note in session.query(Note):
            print('\n',note)

    #input('hit something to exit')
    
if __name__=='__main__':
    main()
