from database.imports import *
from database.models.base import Base
from database.standards import frmtDT

#from database.base import Base
#all I want is a many-many relationship between targets and notes but that doesn't quite work ;_; Association per tble maybe?? that way we don't need a mixin

class Note(Base):
    __tablename__='notes'
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey('users.id')) #TODO
    text=Column(Text,nullable=False)
    dateTime=Column(DateTime,default=datetime.now) #FIXME holy butts no ntp batman O_O_O_O_O_O
    #lbRefs=Column(Integer,ForeignKey('labbook.id') #FIXME
    @property
    def noted(self):
        return [getattr(self,name) for name in self.__dir__() if name[:6]=='parent']

    def __init__(self,text,dateTime=None):
        self.text=text
        self.dateTime=dateTime
    def __repr__(self):
        return '\n%s %s %s\n%s\n\t"%s"'% (self.__class__.__name__, frmtDT(self.dateTime), self.text) #FIXME



