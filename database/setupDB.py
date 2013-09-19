from models import SI_PREFIX, SI_UNIT, SEX, HardwareType, Hardware
from imports import printD

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


def popSIUnit(session):
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
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in _SI_UNITS])

def popNonSIUnit(session):
    _NON_SI_UNITS=(
        #name, symbol
        ('osmole','Osm'), #total moles of solute contributing to osmotic pressure

        ('degree',_degree),
        ('degree','~o'), #also accepted
        ('number','num') #explicitly 'of something'
    )
    session.add_all([SI_UNIT(name=name,symbol=symbol) for name,symbol in _NON_SI_UNITS])

def popSIPrefix(session):
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
    session.add_all([SI_PREFIX(prefix=prefix,symbol=symbol,E=E) for prefix,symbol,E in _SI_PREFIXES])

def popSex(session):
    _SEXES=(
            ('male',_male_symbol,'m',),
            ('female',_female_symbol,'f'),
            ('unknown',_unknown_symbol,'u')
    )
    session.add_all([SEX(name=name,abbrev=abbrev,symbol=symbol) for name,symbol,abbrev in _SEXES])

def popHardwareType(session):
    _HWTYPES=(
        ('rig'), #FIXME want to go ahead and make this whole thing hierarchical? yes
        ('amplifier'),
        ('bnc'),
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
    session.add_all([HardwareType(type=t) for t in _HWTYPES])

def popHardware(session): #FIXME
    root=Hardware(type='rig',name='Tom\'s Rig',parent_id=1)
    session.add(root)
    session.commit()

    session.add(Hardware(Parent=root,type='amplifier',name='Multiclamp 700B',unique_id='serial1'))
    session.add(Hardware(Parent=root,type='amplifier',name='Multiclamp 700B',unique_id='serial2'))
    session.add(Hardware(Parent=root,type='motion controller/driver',name='ESP300'))
    session.add(Hardware(Parent=root,type='digitizer',name='Digidata 1200A'))
    session.add(Hardware(Parent=root,type='digitizer',name='nidaq 1'))
    session.commit()

    amp1=session.query(Hardware).filter_by(unique_id='serial1')[0]
    session.add(Hardware(Parent=amp1,type='headstage',name='hs 0', unique_id='hs0')) #FIXME needs to go via bnc, there has GOT to be a better way?
    session.add(Hardware(Parent=amp1,type='headstage',name='hs 1', unique_id='hs1')) #so the bnc doesn't add anything because it doesn't propagate or constrain pysical reality
    session.commit()
    #basically, make sure reality matches what the computer thinks it is, could make a self test for that asking user to hit 0 and then hit 1?
    #good old corrispondence problems

    nidaq=session.query(Hardware).filter_by(name='nidaq 1')[0]
    session.add(Hardware(Parent=nidaq,type='led',name='led 470'))
    session.commit()

def populateConstraints(session):
    """Populate the tables used to constrain datatypes"""
    popSIUnit(session)
    popNonSIUnit(session)
    popSIPrefix(session)
    popSex(session)
    popHardwareType(session)
    return session.commit()

def populateTables(session):
    """A run once to load current data (not existing elsewhere into the database (ie may use google docs as a web interface for entering/viewing certain types of data eg mice)"""
    popHardware(session)
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

