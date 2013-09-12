from database.imports import *
from sqlalchemy                         import Date
from sqlalchemy                         import ForeignKeyConstraint
from sqlalchemy.ext.associationproxy    import association_proxy


from database.base import Base, HasNotes
#from notes import HasNotes

###---------------
###  People tables
###---------------

class Person(HasNotes, Base):
    __tablename__='people'
    PrefixName=Column(String) #BECAUSE FUCK YOU
    FirstName=Column(String)
    MiddleName=Column(String)
    LastName=Column(String)
    #Gender=Column(String,ForeignKey('sex.id')) #LOL
    Gender=Column(String(1),nullable=True) #FIXME tests will fail as soon as I add a real foreign key >_<
    #ForeignKeyConstraint('Person.Gender',['sex.name','sex.symbol','sex.abbrev'])
    Birthdate=Column(Date) #this is here to match the odML, I actually think it is stupid to have, but whatever
    #Role=Column(String,ForeignKey('role.id'))
    Role=Column(String)
    neurotree_id=Column(Integer,unique=True) #for shits and gigs

    ##experiments=relationship('Experiment',backref=backref('person',uselist=False)) #SOMETHING SOMETHING ACCESS CONTROL also in theory this might be m-m in some wierd situation where >1 person involved
    p2p_assoc=relationship('person_to_project',backref='people')
    projects=association_proxy('p2p_assoc','projects')
    def __repr__(self):
        def xstr(string):
            return '' if string is None else str(string)
        name='%s %s %s %s'%(xstr(self.PrefixName),xstr(self.FirstName),xstr(self.MiddleName),xstr(self.LastName))
        role=xstr(self.Role)
        date=xstr(self.Birthdate)
        if type(self.neurotree_id)==type(b''):
            ntid=str(int.from_bytes(self.neurotree_id,'little'))
        #elif type(self.neurotree_id)-=int:
        else:
            ntid=xstr(self.neurotree_id)
        def cols(strings,widths): #FIXME put this in utils?
            out=[]
            for i in range(len(widths)):
                string=strings[i]
                width=widths[i]
                out.append(string+' '*(width-len(string)))
            return out
        name,role,date,ntid=cols((name,role,date,ntid),(35,15,10,10))
        return '\n%s%s\t%s\t%s%s '%(name,xstr(self.Gender),date,role,ntid)

class User(Base):
    __tablename__='users'
    person_id=Column(Integer,ForeignKey('people.id'),unique=True) #not all users are people and not all people are users
    #BUT each person can only have ONE user associated, something something auditing? I'm sure this is super insecure
    #because why the fuck not...
    pass


class Credentials(Base): #FIXME table per user is safer since can restrict access by user_id?
    user_id=Column(Integer,ForeignKey('users.id'))
    pass
