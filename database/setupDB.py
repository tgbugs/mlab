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


def popSIUnit(session): #FIXME TODO switch over to quanitities for this?
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
        ('number','num'), #explicitly 'of something'
        ('boolean','bool'),
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
        ('surgical tool','forceps, scalpels, spatuals, scissors, you name it'),
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
        ('chamber','Box for keeping dead brain slices alive.'),
        ('actuator','something (usually motoroized) for moving something else very accurately, seems related to a manipulator'),
        ('keyboard','quite useful for typing in data manually >_<'),
    )
    session.add_all([HardwareType(id=t,description=d) for t,d in _HWTYPES])

def popHardware(session):
    root=Hardware(type_id='rig',name='Tom\'s Rig')
    session.add(root)
    session.commit()

    session.add(Hardware(type_id='microscope',name='BX51WI'))
    chamber=Hardware(type_id='chamber',name='interface chamber',Properties={'model':'jim\'s'})
    session.add(chamber)

    patchPipette=Hardware(type_id='pipette',name='patch pipette',Properties={'model':'BF150-110-10','manufacturer':'Sutter Instrument'})
    iuepPipette=Hardware(type_id='pipette',name='iuep pipette',Properties={'model':'3-000-203-G/X','manufacturer':'Drummond Scientific'}) #FIXME is this not a 'type'
    session.add_all([patchPipette,iuepPipette])

    rigcam=Hardware(parent_id=root,type_id='camera',name='rigcam') #TODO

    esp300=Hardware(parent_id=root,type_id='motion controller/driver',name='ESP300')
    session.add(esp300)
    digidata=Hardware(parent_id=root,type_id='digitizer',name='Digidata 1322A',Properties={'unique_id':'105309'})
    session.add(digidata)
    session.add(Hardware(parent_id=root,type_id='digitizer',name='nidaq',Properties={'model':'NI PCIe-6259','unique_id':'0x138FADB'}))
    session.commit()
    
    #wierd, since these can also be controlled directly, but I guess that ok?
    session.add(Hardware(parent_id=esp300,type_id='actuator',name='espX',Properties={'unique_id':'B12 9463'})) #FIXME naming
    session.add(Hardware(parent_id=esp300,type_id='actuator',name='espY',Properties={'unique_id':'B08 2284'}))
    session.add(Hardware(parent_id=digidata,type_id='amplifier',name='mc1',Properties={'model':'Multiclamp 700B','unique_id':'00106956'}))
    session.add(Hardware(parent_id=digidata,type_id='amplifier',name='mc2',Properties={'model':'Multiclamp 700B','unique_id':'00106382'}))
    session.commit()

    amp1=session.query(Hardware).filter_by(name='mc1')[0]
    session.add(Hardware(parent_id=amp1,type_id='headstage',name='hs 0 (left)',Properties={'unique_id':'115054'})) #FIXME needs to go via bnc, there has GOT to be a better way?
    session.add(Hardware(parent_id=amp1,type_id='headstage',name='hs 1 (right)',Properties={'unique_id':'95017'})) #so the bnc doesn't add anything because it doesn't propagate or constrain pysical reality
    session.commit()
    #basically, make sure reality matches what the computer thinks it is, could make a self test for that asking user to hit 0 and then hit 1?
    #good old corrispondence problems

    nidaq=session.query(Hardware).filter_by(name='nidaq')[0]
    session.add(Hardware(parent_id=nidaq,type_id='led',name='470',Properties={'model':'M470L2','unique_id':'M00277763'}))
    session.commit()
    
    session.add(Hardware(name='keyboard',type_id='keyboard'))

def popReagentType(session):
    acsf=ReagentType(name='acsf')#,iupac=None)

def popDataIO(session):
    session.add(DataIO(name='urio',docstring='mareti'))

def popStep(session): #FIXME we really should never have to do this directly!
    session.add(Step(name='no steps',docstring='fixme',dataio_id=1))

def popPeople(session):
    session.add(Person(FirstName='Tom',LastName='Gillespie'))
    session.flush()

def popProject(session):
    proj=Project(lab='Scanziani',blurb='Horizontal projections on to SOM cells')
    session.add(proj)
    tom=session.query(Person).filter(Person.FirstName=='Tom',Person.LastName=='Gillespie').one()
    proj.people.append(tom) #FIXME this should autoprop from experiments?



def popExperimentType(session): #FIXME
    session.add(ExperimentType('acute slice prep','slice',1))
    session.add(ExperimentType('in vitro patch','patch',1))

def popDataFileSources(session):
    session.add(DataFileSource(name='clampex9_scope',extension='abf',docstring='a clampex!'))
    session.add(DataFileSource(name='clampex 9.2',extension='abf',docstring='a clampex!'))
    session.commit() #LOL OOPS

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
    hrr='file://HILL_RIG/D:/tom_data/rigcam'
    hrc='file://HILL_RIG/D:/tom_data/clampex'
    anc='file://andromeda/C:/tom_data/clampex'
    atc='file://athena/home/tom/mlab_data/clampex'
    session.add(Repository(jax,name='jax strain db'))
    session.add(Repository(hrr,name='rig rigcam'))

    r1=Repository(hrc,name='rig clampex')
    r2=Repository(anc,name='andromeda clampex')
    r3=Repository(atc,name='athena clampex')
    session.add(r1)
    session.add(r2)
    session.add(r3)
    r1.mirrors_from_here.extend((r2,r3))

    session.commit()

def popFiles(session):
    rep=session.query(Repository).filter_by(name='jax strain db')[0]
    session.add(File('003718.html',rep))
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

def popSubjectType(session):
    session.add(SubjectType('litter'))
    session.add(SubjectType('mouse',has_sex=True))
    session.add(SubjectType('cell'))
    session.add(SubjectType('slice'))
    session.commit()
def popStrains(session):
    #session.add(Website('http://jaxmice.jax.org/strain/003718.html'))
    session.add(Strain(jax_id='003718',abbrev='dkgin'))
    session.add(Strain(jax_id='009103',abbrev='wfs1')) #wfs1-creERT2 Tg2
    session.commit()

def popDataSourceAssociations(session):
    #TODO make this as simple as possible
    #so that hopefully the hardware tree is only needed for debugging/consistency checks

    #fuck, datasource is going to change depending on the mode the amp is in... how to propagate forward
    pass

def populateConstraints(session): #FIXME this has become testing because of how things have been reworked
    """Populate the tables used to constrain datatypes"""
    popPeople(session)
    popProject(session)
    popSIUnit(session)
    popNonSIUnit(session)
    popSIPrefix(session)
    popSex(session)
    popHardwareType(session)
    popDataIO(session)
    session.flush()
    popStep(session)
    session.flush()
    popExperimentType(session)
    popSubjectType(session)
    return session.commit()

def populateTables(session):
    """A run once to load current data (not existing elsewhere into the database (ie may use google docs as a web interface for entering/viewing certain types of data eg mice)"""
    popHardware(session)
    popRepos(session)
    popFiles(session)
    popCiteType(session)
    popCiteables(session)
    popStrains(session)
    popDataFileSources(session)

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

