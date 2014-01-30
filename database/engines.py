import socket
import os
from sqlalchemy import create_engine
from psycopg2.extras import register_hstore

def sqliteMem(echo=False):
    from sqlalchemy.engine import Engine
    from sqlalchemy import event
    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()
    engine = create_engine('sqlite:///:memory:',echo=echo)
    event.listen(engine,'connect',set_sqlite_pragma)
    return engine

def pgTest(echo=False,wipe_db=False,username='sqla',password='asdf',host='localhost',port=54321):
    if socket.gethostname()=='athena' and os.name == 'posix':
        port=5432
    pg='postgresql://%s:%s@%s:%s/%s'
    if wipe_db:
        engine = create_engine(pg%(username,password,host,port,'postgres'),echo=echo)
        con=engine.connect()
        con.execute('commit')
        con.execute('drop database if exists db_test')
        con.execute('commit')
        con.execute('create database db_test')
        con.execute('commit')
        con.close()
        del(engine)
    engine=create_engine(pg%(username,password,host,port,'db_test'),echo=echo)
    return engine

def pgReal(username,password,host,port=54321,database='postgres',echo=False): #FIXME postgres probably shouldn't be default
    pg='postgresql://%s:%s@%s:%s/%s'
    if socket.gethostname()=='athena' and os.name == 'posix':
        port=5432
        database='scidb_v2_test'
    if socket.gethostname()=='andromeda':
        database='scidb_v2_test'
    engine=create_engine(pg%(username,password,host,port,database),echo=echo)
    con=engine.connect()
    try:
        pass #XXX WHEN CREATING A NEW DATABSE MOVE engine and con here, DO NOT LEAVE HERE WHEN RUNNING FOR REAL
    except: #FIXME specific please
        del(engine)
        print('database not found: creating!')
        engine = create_engine(pg%(username,password,host,port,'postgres'),echo=echo)
        con=engine.connect()
        con.execute('commit')
        con.execute('create database %s'%database)
        con.execute('commit')
        con.close()
        del(engine)
        engine=create_engine(pg%(username,password,host,port,database),echo=echo)

    #con.execute('CREATE EXTENSION hstore;')
    #register_hstore(engine.raw_connection(),True)
    return engine



###
# Database version definition, this is currently managed by git since the whole codebase changes >_<
###
#engine=pgReal('sqla','asdf','localhost',54321,'scidb_v2',False) #XXX THIS IS THE ONE YOU SHOULD USE! update when ready!
engine=pgTest()

#pgEng=engine #XXX switch over at some point
pgEng=pgTest #XXX switch over at some point
