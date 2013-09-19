from models import SI_PREFIX, SI_UNIT, SEX, HardwareType

###----------------------------
###  Populate Constraint tables
###----------------------------

#global variables that would be magic otherwise
#most of these need chcp 65001 on windows and that requires py33
_OMEGA='\u03A9' #use instead of 2126 which is for backward compatability 
_degree='\u00B0'
_mu='\u03BC'
_male_symbol='\u2642'
_female_symbol='\u2640'
_unknown_symbol='\u26AA'


#all names, prefixes, symbols, and Es from wikipedia
#http://en.wikipedia.org/wiki/SI_base_unit
#http://en.wikipedia.org/wiki/SI_derived_units
#http://en.wikipedia.org/wiki/Units_accepted_for_use_with_SI

#TODO make auto unit conversions for DA?
#TODO need some way to implement sets of units? bugger
_SI_UNITS=(
    #name, symbol
    ('meter','m'),

    ('gram','g'), #and now I see why they have kg as the base...

    ('liter','L'),

    ('mole','mol'),

    ('molarity','M'),
    #('molar','M'),
    ('molality','_m'), #FIXME
    #('molal','_m'), #FIXME

    ('kelvin','K'),

    ('degree Celcius',_degree+'C'), #degrees = U+00B0
    ('degree Celcius','~oC'), #Tom also accepts using the digraph for the degree symbol...

    ('candela','ca'),

    ('lumen','lm'),

    ('lux','lx'),

    ('second','s'),

    ('hertz','Hz'),

    ('minute','min'),

    ('hour','h'),

    ('day','d'),

    ('radian','rad'),

    ('steradian','sr'),

    ('newton','N'),

    ('pascal','Pa'),

    ('joule','J'),

    ('watt','W'),

    ('ampere','A'),
    #('amp','A'),

    ('coulomb','C'),

    ('volt','V'),

    ('farad','F'),

    ('ohm',_OMEGA),

    ('ohm','R'), #R also accepted per the note on wikipedia and brit standard

    ('siemens','S'),

    ('weber','Wb'),

    ('tesla','T'),

    ('henry','H'),


    ('becquerel','Bq'),

    ('gray','Gy'),

    ('sievert','Sv'),

    ('katal','kat'),
    
    ('decibel','dB'),
)
_NON_SI_UNITS=(
    #name, symbol
    ('osmole','Osm'), #total moles of solute contributing to osmotic pressure

    ('degree',_degree),
    ('degree','~o'), #also accepted
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

_HWTYPES=(
    ('amplifier'),
    ('headstage'),
    ('computer'),
    ('manipulator'),
    ('motion controller/driver'),
    ('led'),
    ('filter'),
    ('microscope'),
    ('digitizer'),
    ('signal generator'),
    ('pipette'), #FIXME is this a reagent?@??@?
    ('pipette puller')
)

def populateConstraints(session):
    session.add_all([SI_PREFIX(prefix=prefix,symbol=symbol,E=E) for prefix,symbol,E in _SI_PREFIXES])
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in _SI_UNITS])
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in _NON_SI_UNITS])
    session.add_all([SEX(name=name,abbrev=abbrev,symbol=symbol) for name,symbol,abbrev in _SEXES])
    session.add_all([HardwareType(type=t) for t in _HWTYPES])
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

