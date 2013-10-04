#XXX DEPRICATED
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import *
from database.engines import  sqliteMem, pgTest

def postgresEng(echo=False,wipe_db=False):
    if wipe_db:
        engine = create_engine('postgresql://sqla:asdf@localhost:54321/postgres',echo=echo)
        con=engine.connect()
        con.execute('commit')
        con.execute('drop database if exists db_test')
        con.execute('commit')
        con.execute('create database db_test')
        con.execute('commit')
        con.close()
        del(engine)
    return create_engine('postgresql://sqla:asdf@localhost:54321/db_test',echo=echo)

def sqliteEng(echo=False):
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


engine=sqliteEng(False) #TODO git this setup and ready to go for the big time
from database.models.base import initDBScience
from database.setupDB import populateConstraints,populateTables
session=initDBScience(engine)
populateConstraints(session)
populateTables(session)
session.commit()
session.close()

Session_DBScience=sessionmaker(bind=engine)

def datasources():
    espX=None
    espY=None
    bx51wiZ=None #term
    mccChannelN_
    clx


def currentObjects():
    Experiment
    MetaDataSources #so in theory this can be persisted in experiment type OR in the file for the particular experiment #TODO this should be defined directly from rig/functions.py which means that file needs a rework?
    #TODO yes, assign a metadatasource directly to specific valeus IN functions.py
    DataSources
    DataFile
    Subjects


def writeDataFileMetaData(value,abs_error,sigfigs,experiment_state):
    value
    DataFile
    MetaDataSource
    abs_error
    sigfigs



