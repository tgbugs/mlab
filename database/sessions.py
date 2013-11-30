from sqlalchemy.orm import sessionmaker
from database.engines import sqliteMem, pgTest, pgEng
from database.table_logic import add_table_logic

#note: done this way so that engines wont be created willy nilly

@add_table_logic
def get_pgt_sessionmaker():
    pgt_engine=pgTest()
    return sessionmaker(bind=pgt_engine)

@add_table_logic
def get_sqm_sessionmaker():
    sqm_engine=sqliteMem()
    return sessionmaker(bind=sqm_engine)

@add_table_logic
def get_pge_sessionmaker():
    pge_engine=pgEng()
    return sessionmaker(bind=pge_engine)

get_pg_sessionmaker=get_pgt_sessionmaker #XXX CHANGE WHEN NO LONGER TESTING!
#get_pg_sessionmaker=get_pge_sessionmaker #XXX CHANGE WHEN NO LONGER TESTING!
