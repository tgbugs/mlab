from IPython import embed
from database.TESTS import *
from database.models import *
from database.engines import *
from database.queries import *
from database.table_logic import *
from sqlalchemy.orm import Session
engine=pgTest(False)
session=Session(engine)
s=session

#table logic
logic_StepEdge(session)

#tests
dirAll(s)
#t_steps(s,100)
#s.commit()
#print(session.query(Step).all())
#t_edges(s)

#give me some ipython!
embed()
