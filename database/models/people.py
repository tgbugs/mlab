from database.imports import *
from database.models.base import Base
from database.models.mixins import HasNotes

###---------------
###  People tables
###---------------

class Person(Base):
    """__init__(self,pre,first,middle,last,gender,bd,role,ntid,experiments)"""
    __tablename__='people'
    #FIXME TODO add roles/experiment? or base roll that can change?
    id=Column(Integer,primary_key=True)
    PrefixName=Column(String(50)) #BECAUSE FUCK YOU
    FirstName=Column(String(50))
    MiddleName=Column(String(50))
    LastName=Column(String(50))
    contactinfo_id=Column(Integer) #TODO this probably shouldn't go here? I don't want to handle this stuff...
    #Gender=Column(String(1),ForeignKey('sex.abbrev')) #LOL
    Birthdate=Column(Date) #this is here to match the odML, I actually think it is stupid to have, but whatever
    #role has been moved to person-project
    neurotree_id=Column(Integer,unique=True) #for shits and gigs

    experiments=relationship('Experiment',backref=backref('person',uselist=False)) #SOMETHING SOMETHING ACCESS CONTROL also in theory this might be m-m in some wierd situation where >1 person involved
    p2p_assoc=relationship('person_to_project',backref='people')
    projects=association_proxy('p2p_assoc','projects')

    def __repr__(self):
        def xstr(string):
            return '' if string is None else str(string)
        name='%s %s %s %s'%(xstr(self.PrefixName),xstr(self.FirstName),xstr(self.MiddleName),xstr(self.LastName))
        date=xstr(self.Birthdate)
        role=xstr('')
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
        return '\n%s\t%s\t%s%s '%(name,date,role,ntid)
    

class User(Base): #FIXME no longer a datasource, the person_id shall be assumed for the time being?
    __tablename__='users'
    id=Column(Integer,primary_key=True)
    person_id=Column(Integer,ForeignKey('people.id'),unique=True) #not all users are people and not all people are users
    #BUT each person can only have ONE user associated, something something auditing? I'm sure this is super insecure
    #because why the fuck not...
    pass


class Credentials(Base): #FIXME table per user is safer since can restrict access by user_id?
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey('users.id'))
    pass
