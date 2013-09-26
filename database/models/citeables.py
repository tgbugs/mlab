from database.imports import *
from database.base import Base
from database.standards import URL_STAND
from database.mixins import HasFiles

###----------
###  Projects
###----------

class person_to_project(Base):
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
    id=Column(Integer,primary_key=True)
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

#FIXME how the fuck do I query for these!??!?!
class Citeable(HasFiles, Base):
    #see: http://www2.liu.edu/cwis/cwp/library/workshop/citation.htm
    #TODO base class for all citable things, such as personal communications, journal articles, books
    #this is now a wrapper for datafiles (among other things) and it should allow for easy querying
    __tablename___='citeable'
    id=Column(Integer,primary_key=True)
    type=Column(String(15),nullable=False)
    #FIXME should this be metadata like the rest? eh... probs not
    title=None

    version=Column(Integer) #for things like protocols... TODO can we version some of these with git??
    accessDateTime=Column(DateTime,default=datetime.now)
    
    """
    __mapper_args__={
        'polymorphic_on':type,
        'polymorphic_identity':'citeable'
    }
    """


    #TODO create the columns here so that they can propagate people correctly when I pass in a pubmed citation
    #once the columns are in place I can just make it so that the output format is whatever I want

    def __init__(self,type=None,DataFiles=None,accessDateTime=None):
        self.type=type
        self.datafiles.extend(DataFiles)
        self.accessDateTime=accessDateTime


class Citation(Base): #FIXME HasDOI mixin should make life real supe easy
    #TODO crossref seems to have the raw xml??!
    #fuck it man, I don't need all this shit, I just need the xml to be parsed >_<
    #TODO delete all this shit
    __tablename__='publication'
    id=Column(Integer,primary_key=True)
    authors=None #relationship('Person')
    Date=Column(Date)
    book_title=Column(String)
    website_title=Column(String)
    article_title=Column(String)
    webpage_title=Column(String)
    periodical_title=Column(String)
    blog_title=Column(String)
    volume=Column(String)
    startPage=Column(Integer)
    stopPage=Column(Integer)
    pages=Column(String)
    @hybrid_property
    def pages(self):
        return '%s-%s'%(self.startPage,self.stopPage)
    place_of_publication=Column(String)
    publisher=Column(String)
    database=Column(String)
    other=Column(String)
    doi=Column(String)
    pmid=Column(String)
    isbn=Column(String(20)) #room to grow ;)
    #urls shall be saved via the DataFile interface

    def output(format):
        #TODO, does this go here, I don't think it does, I think it goes somewhere else...
        string=None
        return string

"""
class Website(Citeable):
    __tablename__='website'
    id=Column(Integer,ForeignKey('citeable.id'),primary_key=True)
    url=Column(String)
    cached=None #TODO wget it with a timestamp?!
    credentials_id=Column(Integer,ForeignKey('credentials.id')) 
    __mapper_args__={'polymorphic_identity':'website'}
    def __init__(self,url,credentials_id=None):
        self.url=url
        self.credentials_id=credentials_id
    def __repr__(self):
        return super().__repr__('url')
"""


class IACUCProtocols(Base): #note: probs can't store them here, but just put a number and a link (frankly no sense, they are kept in good order elsewere)
    id=Column(Integer,primary_key=True)
    pass


class Methods(Base):
    id=Column(Integer,primary_key=True)
    pass


class Recipe(Base):
    id=Column(Integer,primary_key=True)
    #acsf
    #internal
    #sucrose


