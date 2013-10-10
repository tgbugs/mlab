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


class Gene(HasCiteables, Base): #NOT subjects because they are actually the exact opposite, genes are universals with many, many instantiations, the complete object of subjects
    #you can't study a gene as if it is an organism Dawkins, because the notion that genes exist in the way we idealize them is completely wrong, the context of the gene is different for pretty much every cell (type if you must be a bit stodgy about initial conditions), I cant even draw a good analogy at the moment to some higher level phenomenon
    #incidentlaly you *could* study a single gene if you could go in to a single cell and look at how frequently that section of dna was transcribed but if you did that you would pretty soon realize that the causal story is so much more complicated that the central dogma starts to look pretty silly, just think of all the intervening steps and interactions between the product of a dna squence in a single cell and the phenotype of an organism, in fact, that cell will usually die long before it alone could impact the phenotype of the organism...
    #something about information does mislead us, you're right Dan...
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
    gene_id=Column(Integer,ForeignKey('gene.id'))
    #will be VERY useful when converting for real things
    #FIXME: by reflection from jax??? probably not
    #id=Column(String(20),primary_key=True,autoincrement=False)
    #TODO can just use datafiles to get the data on them via
    #http://jaxmice.jax.org/strain/*.html
    #make a way to put the data in via a url
    def __init__(self,jax_id,name=None,abbrev=None,Citeables=[]):
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
