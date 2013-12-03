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
    try:
        engine=create_engine(pg%(username,password,host,port,database),echo=echo)
        con=engine.connect()

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


pgEng=pgTest #XXX switch over at some point

engine=pgReal('sqla','asdf','localhost',54321,'scidb_v1',False) #XXX THIS IS THE ONE YOU SHOULD USE! update when ready!
#engine=pgTest()
