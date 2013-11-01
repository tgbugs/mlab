from datetime import datetime,timedelta #ALL TIMES ARE UTC WITH tzinfo=None, CONVERT LATER; FIXME postgress assumes the times give are from the env timezone >_<, just use func.now

#IEEE DOUBLE and numpy float64 have the same format, 1 bit sign, 11 bits exponent, 52 bits mantissa
#from sqlalchemy                         import func
from sqlalchemy                         import Table
from sqlalchemy                         import Column
from sqlalchemy                         import Integer
from sqlalchemy                         import Boolean
from sqlalchemy                         import Float
from sqlalchemy                         import String
from sqlalchemy                         import Unicode
from sqlalchemy                         import Text
from sqlalchemy                         import Date
from sqlalchemy                         import DateTime
from sqlalchemy                         import Interval
from sqlalchemy                         import ForeignKey
from sqlalchemy                         import ForeignKeyConstraint
from sqlalchemy                         import UniqueConstraint

from sqlalchemy.orm                     import relationship, backref, object_session, validates, reconstructor

from sqlalchemy.orm.exc                 import FlushError

from sqlalchemy.orm.collections         import attribute_mapped_collection

from sqlalchemy.ext.hybrid              import hybrid_property, hybrid_method

from sqlalchemy.ext.declarative         import declared_attr

from sqlalchemy.ext.associationproxy    import association_proxy

from debug                              import TDB,ploc

_tdb=TDB()
printD=_tdb.printD
printFD=_tdb.printFuncDict
