from database.models import *
from database.imports import printD

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
        ('rig','ALL THE THINGS'),
        ('amplifier','MAKE SIGNAL BIG'),
        ('bnc','Connector between amps and digitizers etc. Could be used to make really specific HW trees but since atm there is no use for those it is sort of pointless.'),
        ('headstage','the thing that actually holds the pipette holder and electrode'),
        ('computer','beep boop!'),
        ('manipulator','the thing a headstage sits on so it can be moved around with high percision and accuracy'),
        ('motion controller/driver','A box for controlling actuators and/or motors, usually for moving an objective around.'),
        ('led','Electrically controllable photon source, probably has a specific wavelenght or distribution of wavelengths it produces.'),
        ('filter','Super expensive piece of glass for bandpassing or high/low passing photons.'),
        ('microscope','Light! Focus! Objectives! Filters! Oh my!'),
        ('objective','That super expensive thing for focusing light.'),
        ('camera','Pictures thing!'),
        ('digitizer','DAC, probably hooked to your computer, metadata should have how many bits it is'),
        ('signal generator','things like a master8 that can generate arbitrary waveforms without a computer'),
        ('pipette','the unpulled glass cappilary tube'), #FIXME is this a reagent?@??@?
        ('pipette puller','Make that cappilary pointy!'),
        ('chamber','Box for keeping dead brain slices alive.')
    )
    session.add_all([HardwareType(type=t,description=d) for t,d in _HWTYPES])

def popHardware(session):
    root=Hardware(type='rig',name='Tom\'s Rig')
    session.add(root)
    session.commit()

    chamber=Hardware(type='chamber',name='interface chamber',model='jim\'s',blueprint_id=None)
    session.add(chamber)

    patchPipette=Hardware(type='pipette',name='patch pipette',model='BF150-110-10',manufacturer='Sutter Instrument')
    iuepPipette=Hardware(type='pipette',name='iuep pipette',model='3-000-203-G/X',manufacturer='Drummond Scientific')
    session.add_all([patchPipette,iuepPipette])

    session.add(Hardware(Parent=root,type='motion controller/driver',name='ESP300'))
    digidata=Hardware(Parent=root,type='digitizer',name='Digidata 1322A',unique_id='105309')
    session.add(digidata)
    session.add(Hardware(Parent=root,type='digitizer',name='nidaq',model='NI PCIe-6259',unique_id='0x138FADB'))
    session.commit()
    
    #wierd, since these can also be controlled directly, but I guess that ok?
    session.add(Hardware(Parent=digidata,type='amplifier',name='mc1',model='Multiclamp 700B',unique_id='00106956'))
    session.add(Hardware(Parent=digidata,type='amplifier',name='mc2',model='Multiclamp 700B',unique_id='00106382'))
    session.commit()

    amp1=session.query(Hardware).filter_by(unique_id='00106956')[0]
    session.add(Hardware(Parent=amp1,type='headstage',name='hs 0 (left)', unique_id='115054')) #FIXME needs to go via bnc, there has GOT to be a better way?
    session.add(Hardware(Parent=amp1,type='headstage',name='hs 1 (right)', unique_id='95017')) #so the bnc doesn't add anything because it doesn't propagate or constrain pysical reality
    session.commit()
    #basically, make sure reality matches what the computer thinks it is, could make a self test for that asking user to hit 0 and then hit 1?
    #good old corrispondence problems

    nidaq=session.query(Hardware).filter_by(name='nidaq')[0]
    session.add(Hardware(Parent=nidaq,type='led',name='470',model='M470L2',unique_id='M00277763'))
    session.commit()

def popReagentType(session):
    acsf=ReagentType(name='acsf')#,iupac=None)


def popExperimentType(session):
    session.add(ExperimentType('acute slice prep','prep'))
    session.add(ExperimentType('in vitro patch','patch'))

def popDataSources(session):
    #session.add(DataSource(name='jax'))
    pass

def popMetaDataSources(session):
    espX=None
    espY=None
    stage_z=None
    tomsEyeballs=None
    number_from_protocol=None
    super_accurate_scale=None
    mouse_scale=None
    multiclampcommmader_shit_tons_of_fields_shit=None
    clampex_same_problem_as_above_fuck=None
    pass

def popRepos(session):
    jax='http://jaxmice.jax.org/strain'
    session.add(Repository(jax,name='jax strain db'))
    session.commit()
    pass

def popFiles(session):
    rep=session.query(Repository).filter_by(name='jax strain db')[0]
    session.add(File(rep,'003718.html'))
    pass

def popCiteType(session):
    session.add(CiteableType('publication'))
    session.add(CiteableType('website'))
    session.add(CiteableType('methods'))
    session.add(CiteableType('blueprint'))
    session.commit()
    
def popCiteables(session):
    f=session.query(File).filter_by(filename='003718.html')[0]
    session.add(Citeable(type='website',Files=[f])) #FIXME
    session.commit()

def popStrains(session):
    #session.add(Website('http://jaxmice.jax.org/strain/003718.html'))
    session.add(Strain(jax_id='003718',abbrev='dkgin'))
    session.commit()

def popDataSourceAssociations(session):
    #TODO make this as simple as possible
    #so that hopefully the hardware tree is only needed for debugging/consistency checks

    #fuck, datasource is going to change depending on the mode the amp is in... how to propagate forward
    pass

def populateConstraints(session):
    """Populate the tables used to constrain datatypes"""
    popSIUnit(session)
    popNonSIUnit(session)
    popSIPrefix(session)
    popSex(session)
    popHardwareType(session)
    popExperimentType(session)
    return session.commit()

def populateTables(session):
    """A run once to load current data (not existing elsewhere into the database (ie may use google docs as a web interface for entering/viewing certain types of data eg mice)"""
    popHardware(session)
    popRepos(session)
    popFiles(session)
    popCiteType(session)
    popCiteables(session)
    popStrains(session)
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

