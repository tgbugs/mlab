from database import models
from IPython import embed

#this stuff only works for tables that don't have dependencies...
class ModelTest:
    def __init__(self,session,MappedClass,initDict):
        self.session=session
        self.MappedClass=MappedClass
        self.initDict=initDict
        self.insert()
        self.update()
        self.delete()
    def insert(self):
        self.session.add(MappedClass(**self.initDict))
        self.session.commit()
    def update(self):
        pass
    def delete(self):
        pass

for name in models.__all__:
    MappedClass=getattr(models,name)


