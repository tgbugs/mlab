from database.imports               import Column, Integer, declared_attr
from sqlalchemy.orm                 import Session
from sqlalchemy.ext.declarative     import declarative_base

class DefaultBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() #FIXME cls.__name__ could fix?

    def _write_once(self, key, value): #base for all write once validators
        if getattr(self, key) is not None:
            raise ValueError('%s is write once!'%key)
        return value

    def strHelper(self,depth=0,attr='id'): #FIXME naming?
        tabs='\t'*depth
        return '%s%s %s'%(tabs,self.__class__.__name__,getattr(self,attr,'no id, set this to primary key column'))
    def __int__(self): #MAGIC when called during __init__ for the simple cases
        #FIXME TODO make sure to override this for MetaData!
        if type(getattr(self,'id',None)) is int:
            return self.id
        else:
            raise TypeError('%s has no id or id is not an int'%self.__class__.__name__)
            return None
    def __repr__(self,attr='id'):
        return '%s %s'%(self.__class__.__name__,getattr(self,attr,'no id, set this to primary key column'))
    def __str__(self):
        return '%s'%(self.__class__.__name__)

Base=declarative_base(cls=DefaultBase)

def initDBScience(engine):
    """initilize all the models in ScienceDB on the given engine"""
    Base.metadata.create_all(engine, checkfirst=True) #FIXME check if tables match __all__ in __init__.py
    return Session(engine)
    
