from datetime import datetime,timedelta #ALL TIMES ARE UTC WITH tzinfo=None, CONVERT LATER

#IEEE DOUBLE and numpy float64 have the same format, 1 bit sign, 11 bits exponent, 52 bits mantissa
from sqlalchemy                         import Table
from sqlalchemy                         import Column
from sqlalchemy                         import Integer
from sqlalchemy                         import String
from sqlalchemy                         import DateTime
from sqlalchemy                         import ForeignKey

from sqlalchemy.orm                     import relationship, backref


from debug                              import TDB

tdb=TDB()
printD=tdb.printD
printFD=tdb.printFuncDict
tdboff=tdb.tdbOff
