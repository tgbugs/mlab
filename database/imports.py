from datetime import datetime,timedelta #ALL TIMES ARE UTC WITH tzinfo=None, CONVERT LATER

#IEEE DOUBLE and numpy float64 have the same format, 1 bit sign, 11 bits exponent, 52 bits mantissa
from sqlalchemy                         import Table
from sqlalchemy                         import Column
from sqlalchemy                         import Integer
from sqlalchemy                         import Float
from sqlalchemy                         import String
from sqlalchemy                         import Unicode
from sqlalchemy                         import Text
from sqlalchemy                         import Date
from sqlalchemy                         import DateTime
from sqlalchemy                         import ForeignKey
from sqlalchemy                         import ForeignKeyConstraint

from sqlalchemy.orm                     import relationship, backref

from sqlalchemy.ext.declarative         import declared_attr

from sqlalchemy.ext.associationproxy    import association_proxy

from debug                              import TDB

_tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
