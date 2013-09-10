from sqlalchemy                         import Column
from sqlalchemy                         import Integer
from sqlalchemy.ext.declarative         import declarative_base, 

class DefaultBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id=Column(Integer, primary_key=True)

    def strHelper(self,depth=0,attr='id'):
        tabs='\t'*depth
        return '\n%s%s %s'%(tabs,self.__class__.__name__,getattr(self,attr))
    def __repr__(self,attr='id'):
        return '\n%s %s'%(self.__class__.__name__,getattr(self,attr))

Base=declarative_base(cls=DefaultBase)

