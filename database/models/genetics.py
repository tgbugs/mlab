from database.imports import *
from database.models.base import Base
from database.models.mixins import HasCiteables


class Genotype(Base): #TODO HasGenotype note this is an association table
    """technically inferred genotype since we have to measure it somehow"""
    subject_id=Column(Integer,ForeignKey('subjects.id'),primary_key=True)
    gene_id=Column(Integer,ForeignKey('gene.id'),primary_key=True)
    copy_number=Column(Integer,nullable=False) #FIXME something something alleles?!? this is measured... actually a relation
    raw_value=Column(Float(53))


class Phenotype(Base):
    subject_id=Column(Integer,ForeignKey('subjects.id'),primary_key=True)
    measured_thing_value=None


class Gene(HasCiteables, Base):
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(Unicode(50))
    locus=Column(Unicode(50))
    symbol=Column(Unicode(50))
    abbrev=Column(String(15))


class Background(HasCiteables, Base):
    id=Column(Integer,primary_key=True) #FIXME
    name=Column(Unicode(50)) #scrape from jax
    abbrev=Column(String(15))


class Strain(HasCiteables, Base): #TODO somehow this looks like mouse type
    id=Column(Integer,primary_key=True) #FIXME
    jax_id=Column(String(10))
    name=Column(Unicode(50)) #scrape from jax
    abbrev=Column(String(15))
    background_id=Column(Integer,ForeignKey('background.id'))
    gene_id=Column(Integer,ForeignKey('gene.id')) #FIXME better to do a m-m here? same w/ bg?
    #FIXME TODO how to handle the 'tree' of strains... do it in the mice? or run it parallel, I think it is better to run it parallel in its own system and just use logic to constuct the strain ID based on the parent strain ids keeps things comaprtmentalized

    def getFromParents(self,*parents): #TODO trying to implement this reveals that strain needs way more thought
        for p in parents:
            pass
        return 1


    def __init__(self,jax_id=None,name=None,abbrev=None,Citeables=[]):
        #name=getJaxData(jax_id) #TODO
        self.jax_id=jax_id
        self.name=name
        self.abbrev=abbrev
        self.citeables.extend(Citeables)


class Species(HasCiteables, Base): #dont know how I would use this atm... havent thought comparatively...
    id=Column(Integer,primary_key=True) #FIXME
    genus=Column(String(50))
    species=Column(String(50))
    binomial_name=Column(String(100))
    @hybrid_property
    def binomial_name(self):
        return self.genus+' '+self.species
    abbrev=Column(String(50))
