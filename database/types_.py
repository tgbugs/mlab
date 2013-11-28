#XXX NOTICE XXX DO NOT NAME THINGS types.py it breaks EVERYTHING
from sqlalchemy.types import PickleType
from sqlalchemy.dialects import postgresql
from sqlalchemy import Float, String

ArrayFloat = PickleType()
ArrayFloat.with_variant(postgresql.ARRAY(Float), 'postgresql')

ArrayString = PickleType()
ArrayString.with_variant(postgresql.ARRAY(String), 'postgresql')

DictType = PickleType()
DictType.with_variant(postgresql.HSTORE(), 'postgresql')
