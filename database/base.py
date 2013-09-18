from database.imports               import Column, declared_attr
from sqlalchemy.ext.declarative     import declarative_base

class DefaultBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id=Column(Integer, primary_key=True)
    #__table_args__={'schema':'public'}
    #__table_args__={}

    def AssignID(self,cls): #FIXME does this go here?
        if cls:
            if cls.id:
                setattr(self,'%s_id'%cls.__class__.__name__.lower(),cls.id)
            else:
                raise AttributeError('%s has no id! Did you commit before referencing the instance directly?'*cls.__class__.__name__)

        def strHelper(self,depth=0,attr='id'):
            tabs='\t'*depth
            return '\n%s%s %s'%(tabs,self.__class__.__name__,getattr(self,attr))
        def __repr__(self,attr='id'):
            return '\n%s %s'%(self.__class__.__name__,getattr(self,attr))

Base=declarative_base(cls=DefaultBase)

#def init_db(engine):
    #Base.metadata.create_all(engine)#, checkfirst=True)
    

