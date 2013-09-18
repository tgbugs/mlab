from database.imports import *
from database.base import Base

###----------
###  Projects
###----------

class person_to_project(Base):
    id=None
    person_id=Column(Integer,ForeignKey('people.id'),primary_key=True)
    project_id=Column(Integer,ForeignKey('project.id'),primary_key=True)
    #TODO add some nice info about what the person is doing on the project or some shit
    def __init__(self, Project=None, Person=None, project_id=None,person_id=None):
        self.project_id=project_id
        self.person_id=person_id
        if Project:
            if Project.id:
                self.project_id=Project.id
            else:
                raise AttributeError
        if Person:
            if Person.id:
                self.person_id=Person.id
            else:
                raise AttributeError


class Project(Base): #FIXME ya know this looks REALLY similar to a paper or a journal article
    #move to the 'data/docs' place?!??! because it is tehcnically a container for data not a table that will actively have data written to it, it is a one off reference
    #FIXME somehow experiment is dependent on this... which suggests that it doesn't quite belong in data
    lab=Column(String(15),nullable=False) #this is how we are going to replace the bloodly PI, and leave at the filter Role=='pi'
    #pi_id=Column(Integer,ForeignKey('people.id')) #FIXME need better options than fkc... need a check constraint on people.role=='PI', or really current role... because those could change and violate certain checks/constraints...??? maybe better just to leave it as a person
    #FIXME projects can have multiple PIs! damn it >_<, scaling this shit...
    iacuc_protocol_id=Column(Integer,ForeignKey('iacucprotocols.id'))
    blurb=Column(Text)

    #PI=relationship('Person',primaryjoin='and_(Project.pi_id==Person.id,Person.Rold=="pi")') #FIXME pi should also be in people list :/
    p2p_assoc=relationship('person_to_project',backref='projects')
    #FIXME do we really want write access here? viewonly=True might be useful?
    people=association_proxy('p2p_assoc','people') #people.append but make sure nothing wierd happends
    relationship
    def __init__(self,lab=None,iacuc_protocol_id=None,blurb=None):
        #self.pi_id=pi_id
        self.lab=lab
        self.iacuc_protocol_id=iacuc_protocol_id
        self.blurb=blurb
        #if PI:
            #if PI.id:
                #pi_id=PI.id
            #else:
                #raise AttributeError

###------------
###  Doccuments
###------------

class Citeable(Base):
    #TODO base class for all citable things, such as personal communications, journal articles, books
    __tablename___='citeable'
    type=Column(String(15),nullable=False)
    __mapper_args__={
        'polymorphic_on':type,
        'polymorphic_identity':'citeable'
    }


class IACUCProtocols(Base): #note: probs can't store them here, but just put a number and a link (frankly no sense, they are kept in good order elsewere)
    pass


class Methods(Base):
    pass


class Recipe(HasNotes, Base):
    id=Column(Integer,primary_key=True)
    #acsf
    #internal
    #sucrose


