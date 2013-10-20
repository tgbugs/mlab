from IPython import embed
from database.TESTS import *
from database.models import *
from database.engines import *
from database.queries import *
from database.table_logic import *
from sqlalchemy.orm import Session
engine=pgTest(True)
session=Session(engine)
s=session
embed()
