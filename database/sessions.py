#XXX deprecated just import the engines directly this is too prone to issues
from sqlalchemy.orm import Session #sessionmaker
from database.engines import sqliteMem, pgTest, pgEng

from database.table_logic import logic_StepEdge

#class LogicSessionMaker(sessionmaker): #FIXME not working...
    #def __call__(self,**local_kw):
        #out=super().__call__(**local_kw)
        #out=add_table_logic(out)
        #return out
    


#note: done this way so that engines wont be created willy nilly

#pgt_engine=pgTest()
#pgt_sessionmaker=add_table_logic(sessionmaker(bind=pgt_engine))

#sqm_engine=sqliteMem()
#sqm_sessionmaker=add_table_logic(sessionmaker(bind=sqm_engine))

#pge_engine=pgEng()
#pge_sessionmaker=sessionmaker(bind=pge_engine)

#pg_sessionmaker=pgt_sessionmaker #XXX CHANGE WHEN NO LONGER TESTING!
