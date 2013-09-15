#contains all the constraint tables and their initial values 
from database.imports   import *

from sqlalchemy         import Unicode

from database.base      import Base

#some global variables that are used here and there that would be magic otherwise
#most of these need chcp 65001 on windows and that requires py33
#FIXME ALL these things need to be converted to bytes :/
_OMEGA='\u03A9'#.encode('utf-8') #use this instead of 2126 which is for backward compatability 
_degree='\u00B0'#.encode('utf-8')
_mu='\u03BC'#.encode('utf-8')
_male_symbol='\u2642'#.encode('utf-8') #U+2642 #FIXME stupid windows console crashing symbol output >_<; in windows shell chcp 65001 #also unicode trouble with this one too what the hell
_female_symbol='\u2640'#.encode('utf-8') #U+2640
_unknown_symbol='\u26AA'#.encode('utf-8') #using unicode U+26AA for this #FIXME chcp 65001 doesn't work for displaying this one; also apparently lucidia console required? nope, didn't fix it #also apparently sqlalchemy doesnt like this

###----------------------------------------------------------------
###  Helper classes/tables for mice (normalization and constraints)
###----------------------------------------------------------------

class File(Base): #FIXME reinventing the wheel here kids, detect ft don't constraint it
    id=None
    type=Column(String(3),primary_key=True)
    #hdf5, abf, py etc

class SI_PREFIX(Base): #Yes, these are a good idea because they are written once, and infact I can enforce viewonly=True OR even have non-root users see those tables as read only
    id=None
    symbol=Column(String(2),primary_key=True)
    prefix=Column(String(5),nullable=False)
    E=Column(Integer,nullable=False)
    #relationship('OneDData',backref='prefix') #FIXME makesure this doesn't add a column!
    def __repr__(self):
        return '%s'%(self.symbol)
    
class SI_UNIT(Base):
    id=None
    symbol=Column(String(3),primary_key=True) #FIXME varchar may not work
    name=Column(String(15),primary_key=True) #this is also a pk so we can accept plurals :)
    #conversion??
    #relationship('OneDData',backref='units') #FIXME make sure this doen't add a column
    def __repr__(self):
        return '%s'%(self.symbol)

class SEX(Base):
    """Static table for sex"""
    id=None
    name=Column(String(14),primary_key=True) #'male','female','unknown' #FIXME do I need the autoincrement 
    symbol=Column(Unicode(1),nullable=False,unique=True) #the actual symbols
    #symbol=Column(Unicode(1)) #the actual symbols
    abbrev=Column(String(1),nullable=False,unique=True) #'m','f','u'
    def __repr__(self):
        return '\n%s %s %s'%(self.name,self.abbrev,self.symbol) #FIXME somehow there are trailing chars here >_<

class Strain(Base): #TODO
    #FIXME class for strain IDs pair up with the shorthand names that I use and make sure mappings are one to one
    #will be VERY useful when converting for real things
    #FIXME: by reflection from jax??? probably not
    pass

###----------------------------
###  Populate Constraint tables
###----------------------------

#all names, prefixes, symbols, and Es from wikipedia
#http://en.wikipedia.org/wiki/SI_base_unit
#http://en.wikipedia.org/wiki/SI_derived_units
#http://en.wikipedia.org/wiki/Units_accepted_for_use_with_SI

#TODO make auto unit conversions for DA?
#TODO need some way to implement sets of units? bugger
_SI_UNITS=(
    #name, symbol
    ('meter','m'),
    ('meters','m'),

    ('gram','g'), #and now I see why they have kg as the base...
    ('grams','g'),

    ('liter','L'),
    ('liters','L'),

    ('mole','mol'),
    ('moles','mol'),

    ('molarity','M'),
    ('molar','M'),
    ('molality','_m'), #FIXME
    ('molal','_m'), #FIXME

    ('kelvin','K'),

    ('degree Celcius',_degree+'C'), #degrees = U+00B0
    ('degrees Celcius',_degree+'C'), #FIXME
    ('degree Celcius','~oC'), #Tom also accepts using the digraph for the degree symbol...
    ('degrees Celcius','~oC'),

    ('candela','ca'),
    ('candelas','ca'),

    ('lumen','lm'),
    ('lumens','lm'),

    ('lux','lx'),

    ('second','s'),
    ('seconds','s'),

    ('hertz','Hz'),

    ('minute','min'),
    ('minutes','min'),

    ('hour','h'),
    ('hours','h'),

    ('day','d'),
    ('days','d'),

    ('radian','rad'),
    ('radians','rad'),

    ('steradian','sr'),
    ('steradians','sr'),

    ('newton','N'),
    ('newtons','N'),

    ('pascal','Pa'),
    ('pascals','Pa'),

    ('joule','J'),
    ('joules','J'),

    ('watt','W'),
    ('watts','W'),

    ('ampere','A'),
    ('amperes','A'),
    ('amp','A'),
    ('amps','A'),

    ('coulomb','C'),
    ('coulombs','C'),

    ('volt','V'),
    ('volts','V'),

    ('farad','F'),
    ('farads','F'),

    ('ohm',_OMEGA), #unicode=U+03A9, this is upper case greek and should be used instead of 2126
    ('ohms',_OMEGA),

    ('ohm','R'), #R also accepted as per the note on wikipedia and some brit standard
    ('ohms','R'),

    ('siemens','S'),

    ('weber','Wb'),
    ('webers','Wb'),

    ('tesla','T'),
    ('teslas','T'),

    ('henry','H'),
    ('henrys','H'),


    ('becquerel','Bq'),
    ('becquerels','Bq'),

    ('gray','Gy'),
    ('grays','Gy'),

    ('sievert','Sv'),
    ('sieverts','Sv'),

    ('katal','kat'),
    ('katals','kat'),
    
    ('decibel','dB'),
    ('decibels','dB')
)
_NON_SI_UNITS=(
    #name, symbol
    ('osmole','Osm'), #total moles of solute contributing to osmotic pressure
    ('osmoles','Osm'),

    ('degree',_degree), #unicode for the symbol is U+00B0
    ('degrees',_degree),
    ('degree','~o'), #also accepted
    ('degrees','~o'),
    ('number','num') #explicitly 'of something'
)
_SI_PREFIXES=(
                #prefix, symbol, E
                ('yotta','Y',24),
                ('zetta','Z',21),
                ('exa','E',18),
                ('peta','P',15),
                ('tera','T',12),
                ('giga','G',9),
                ('mega','M',6),
                ('kilo','k',3),
                ('hecto','h',2),
                ('deca','da',1),
                ('','',0),
                ('deci','d',-1),
                ('centi','c',-2),
                ('milli','m',-3),
                ('micro',_mu,-6),
                ('micro','u',-6,), #also unoffically used
                ('nano','n',-9),
                ('pico','p',-12),
                ('femto','f',-15),
                ('atto','a',-18),
                ('zepto','z',-21),
                ('yocto','y',-24)
)
_SEXES=(
        ('male',_male_symbol,'m',),
        ('female',_female_symbol,'f'),
        ('unknown',_unknown_symbol,'u')
)


def populateConstraints(session):
    session.add_all([SI_PREFIX(prefix=prefix,symbol=symbol,E=E) for prefix,symbol,E in _SI_PREFIXES])
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in _SI_UNITS])
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in _NON_SI_UNITS])
    session.add_all([SEX(name=name,abbrev=abbrev,symbol=symbol) for name,symbol,abbrev in _SEXES])
    return session.commit()

if __name__=='__main__':
    import re
    printT=lambda tup:print(re.sub('\), ','),\r\n',str(tup)))
    printT(_SI_UNITS)
    print('')
    printT(_NON_SI_UNITS)
    print('')
    printT(_SI_PREFIXES)
    print('')
    printT(_SEXES)
