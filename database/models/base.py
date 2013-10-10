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

    def AssignID(self,cls): #FIXME does this go here?
        if cls:
            if cls.id:
                setattr(self,'%s_id'%cls.__class__.__name__.lower(),cls.id)
                #setattr(self,'%s_id'%cls.__tablename__,cls.id)
            else:
                raise AttributeError('%s has no id! Did you commit before referencing the instance directly?'*cls.__class__.__name__)

    def strHelper(self,depth=0,attr='id'):
        tabs='\t'*depth
        return '\n%s%s %s'%(tabs,self.__class__.__name__,getattr(self,attr))
    def __repr__(self,attr='id'):
        return '\n%s %s'%(self.__class__.__name__,getattr(self,attr))
    def __str__(self):
        return '%s'%(self.__class__.__name__)

Base=declarative_base(cls=DefaultBase)

def initDBScience(engine):
    """initilize all the models in ScienceDB on the given engine"""
    Base.metadata.create_all(engine, checkfirst=True) #FIXME check if tables match __all__ in __init__.py
    return Session(engine)
    
