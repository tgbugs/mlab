#XXX NOTICE XXX DO NOT NAME THINGS types.py it breaks EVERYTHING
from sqlalchemy.types import PickleType
from sqlalchemy.dialects import postgres
from sqlalchemy.ext.mutable import MutableDict

def array_base(column_type):
    array = PickleType()
    array.with_variant(postgres.ARRAY(column_type), 'postgres')
    return array

Array=array_base

DictType = MutableDict.as_mutable(PickleType)
DictType.with_variant(MutableDict.as_mutable(postgres.HSTORE), 'postgres')


__all__=[
    'Array',
    'DictType',
]

#ArrayFloat = PickleType()
#ArrayFloat.with_variant(postgresql.ARRAY(Float), 'postgresql')

#ArrayString = PickleType()
#ArrayString.with_variant(postgresql.ARRAY(String), 'postgresql')

