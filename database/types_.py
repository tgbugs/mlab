#XXX NOTICE XXX DO NOT NAME THINGS types.py it breaks EVERYTHING
from sqlalchemy.types import PickleType
from sqlalchemy.dialects import postgres,postgresql
from sqlalchemy.ext.mutable import MutableDict

def array_base(column_type):
    array = PickleType()
    array.with_variant(postgres.ARRAY(column_type), 'postgres')
    array.with_variant(postgres.ARRAY(column_type), 'postgresql')
    return array

Array=array_base

_DictType = MutableDict.as_mutable(PickleType)
_DictType.with_variant(MutableDict.as_mutable(postgres.HSTORE), 'postgres')
#_DictType.with_variant(MutableDict.as_mutable(postgresql.HSTORE), 'postgresql')
#_DictType.with_variant(MutableDict.as_mutable(postgresql.HSTORE), 'psycopg2')
#_DictType.with_variant(MutableDict.as_mutable(postgresql.HSTORE), 'postgresql+psycopg2')
DictType=_DictType #FIXME not working as hstore :/


__all__=[
    'Array',
    'DictType',
]

#ArrayFloat = PickleType()
#ArrayFloat.with_variant(postgresql.ARRAY(Float), 'postgresql')

#ArrayString = PickleType()
#ArrayString.with_variant(postgresql.ARRAY(String), 'postgresql')

