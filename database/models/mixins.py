from database.imports import *
from database.models.base import Base

#some global variables that are used here and there that would be magic otherwise
_plusMinus='\u00B1'

class HasMirrors: #FIXME this should validate that they actually *are* mirrors?
    @declared_attr
    def mirrors_from_here(cls): #FIXME lots of bugs with files not actually being present!
        ctab=cls.__tablename__
        cname=cls.__name__
        self_assoc=Table('%s_self_assoc'%ctab, cls.metadata,
                        Column('left_id',ForeignKey('%s.id'%ctab),primary_key=True),
                        Column('right_id',ForeignKey('%s.id'%ctab),primary_key=True)
        )
        return relationship('%s'%cname,secondary=self_assoc,primaryjoin=
                '%s.id==%s_self_assoc.c.left_id'%(cname,ctab),
                secondaryjoin='%s.id==%s_self_assoc.c.right_id'%(cname,ctab),
                backref='mirrors_to_here'
                )

    def validate_mirror(self,repository):
        #TODO FIXME how to actually do this...
        if repository.origin_files:
            return False


    @property
    def mirrors(self): #TODO fix append? not sure possible
        return list(set(self.mirrors_to_here+self.mirrors_from_here))

    @property
    def files(self):
        files_ = []
        [files_.extend(m.origin_files) for m in self.mirrors_from_here]
        [files_.extend(m.origin_files) for m in self.mirrors_to_here]
        files_.extend(self.origin_files)
        fs=list(set(files_))
        fs.sort()
        return fs #FIXME ;_; ugly and slow


class selfmtm:
    @declared_attr
    def nodes(cls): #can use this for a self ref m-m mixin?
        ctab=cls.__tablename__
        cname=cls.__name__
        self_assoc=Table('%s_self_assoc'%ctab, cls.metadata,
                        Column('parent_id',ForeignKey('%s.id'%ctab),primary_key=True),
                        Column('child_id',ForeignKey('%s.id'%ctab),primary_key=True) #FIXME we want to keep track of the expeirment too and those THREE need to be consistent
        )
        return relationship('%s'%cname,secondary=self_assoc,primaryjoin=
                '%s.ontpar_id==%s_self_assoc.parent_id'%(cname,ctab),
                secondaryjoin='%s.id==%s_self_assoc.child_id'%(cname,ctab),
                backref='offspring'
                )

###--------------
###  notes mixins
###--------------

class Note: #basically metadata for text... grrrrrr why no arbitrary datatypes :/
    id=Column(Integer,primary_key=True)
    dateTime=Column(DateTime,default=datetime.now) #FIXME holy butts no ntp batman O_O_O_O_O_O
    text=Column(Text,nullable=False)
    user_id=None #Column(Integer,ForeignKey('users.id')) #TODO
    def __init__(self,text,parent_id=None,dateTime=None):
        self.text=text
        self.parent_id=int(parent_id)
        self.dateTime=dateTime #FIXME may not want this...

class fNote(Note):
    def __init__(self,text,parent_id=None,dateTime=None):
        self.text=text
        self.url=parent_id.url #FIXME misleading?
        self.filename=parent_id.filename
        self.dateTime=dateTime


class fHasNotes: #for files :/ #TODO V2 we are switching files to ids
    @declared_attr
    def notes(cls):
        tname=cls.__tablename__
        cls.Note=type(
            '%sNote'%cls.__name__,
            (fNote, Base, ),
            {   '__tablename__':'%s_notes'%tname,
                'url':Column(String, #FIXME nasty errors inbound
                    nullable=False),
                'filename':Column(String, #FIXME nasty errors inbound
                    nullable=False),
                'parent':relationship('%s'%cls.__name__, uselist=False, #FIXME uselist???
                    backref=backref('_notes')),
                '__table_args__':(ForeignKeyConstraint(['url','filename'],['%s.url'%tname,'%s.filename'%tname]),{})
            }
        )
        #return relationship(cls.Note,backref=backref('parent',uselist=False))
        return association_proxy('_notes','text',creator=lambda text: cls.Note(text))# FIXME BROKEN creator


class HasNotes: #FIXME this works ok, will allow the addition of the same note to anything basically
    @declared_attr
    def notes(cls):
        tname=cls.__tablename__
        cls.Note=type(
            '%sNote'%cls.__name__,
            (Note, Base, ),
            {   '__tablename__':'%s_notes'%tname,
                'parent_id':Column(Integer, #FIXME nasty errors inbound
                    ForeignKey('%s.id'%tname),nullable=False),
                'parent':relationship('%s'%cls.__name__, uselist=False, #FIXME uselist???
                    backref=backref('_notes')),
            }
        )
        #return relationship(cls.Note,backref=backref('parent',uselist=False))
        return association_proxy('_notes','text',creator=lambda text: cls.Note(text))

###-------------
###  datasource mixins
###-------------

class HasDataFileSources:
    @declared_attr
    def datafilesources(cls):
        datafilesource_association = Table('%s_dfs_assoc'%cls.__tablename__, cls.metadata,
            Column('datafilesource_id',ForeignKey('datafilesources.id'),primary_key=True),
            Column('%s_id'%cls.__tablename__,ForeignKey('%s.id'%cls.__tablename__), #FIXME .id may not be all?
                   primary_key=True)
        )
        return relationship('DataFileSource',secondary=datafilesource_association,
            primaryjoin='{0}_dfs_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='DataFileSource.id=={0}_dfs_assoc.c.datafilesource_id'.format(cls.__tablename__),
            backref=backref('%s'%cls.__tablename__) #FIXME do we really want this?
        )


class HasMetaDataSources:
    @declared_attr
    def metadatasources(cls):
        metadatasource_association = Table('%s_mds_assoc'%cls.__tablename__, cls.metadata,
            Column('metadatasource_id',ForeignKey('metadatasources.id'),primary_key=True),
            Column('%s_id'%cls.__tablename__,ForeignKey('%s.id'%cls.__tablename__), #FIXME .id may not be all?
                   primary_key=True)
        )
        return relationship('MetaDataSource',secondary=metadatasource_association,
            primaryjoin='{0}_mds_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            secondaryjoin='MetaDataSource.id=={0}_mds_assoc.c.metadatasource_id'.format(cls.__tablename__),
            backref=backref('%s'%cls.__tablename__) #FIXME do we really want this?
        )


###-------------
###  data mixins
###-------------

class MetaData: #the way to these is via ParentClass.MetaData which I guess makes sense?
    #this stuff is not vectorized... a VectorizedData might be worth considering ala ArrayData
    dateTime=Column(DateTime,default=datetime.now)
    #value=Column(Float(53),nullable=False)
    #abs_error=Column(Float(53))
    value=Column( Array(Float(53)) ,nullable=False) #TODO 
    abs_error=Column( Array(Float(53)) ) #TODO
    @validates('parent_id','metadatasource_id','dateTime','value','abs_error')
    def _wo(self, key, value): return self._write_once(key, value)


    def __init__(self,value,parent_id,metadatasource_id,abs_error=None,dateTime=None): #FIXME want *args @ all?
        self.value=value
        self.abs_error=abs_error
        self.parent_id=int(parent_id) #this is here because of the write once
        self.dateTime=dateTime
        self.metadatasource_id=int(metadatasource_id)
            
    def __int__(self):
        return int(self.value) #FIXME TODO think about this
    
    def __round__(self):
        return round(self.value)

    def __repr__(self):
        mantissa=''
        error=''
        if self.metadatasource.mantissa: mantissa='mantissa: %s'%self.metadatasource.mantissa
        if self.abs_error != None: error='%s %s'%(_plusMinus,self.abs_error)
        return '\n%s %s %s %s %s %s'%(self.parent_id,self.dateTime,self.value,self.metadatasource.strHelper(),mantissa,error) #TODO this is where quantities really pays off


class HasMetaData: #FIXME based on how I'm using this right now, the relationship should probably return a dictionary collection indexed by metadatasource_id and ordered by datetime???
    #I intentionally do not allow explicit groupings of metadata into higher dimensions, I don't think we will need that, but getting the alignment right for multiple multidimensional measurements will be a problem FIXME
    @declared_attr
    def metadata_(cls): #FIXME naming...
        cls.MetaData = type(
                '%sMetaData'%cls.__name__,
                (MetaData, Base,),
                {   '__tablename__':'%s_metadata'%cls.__tablename__,
                    'id':Column(Integer,primary_key=True),
                    'parent_id':Column(Integer, #FIXME nasty errors inbound
                        ForeignKey('%s.id'%cls.__tablename__),nullable=False),
                    'metadatasource_id':Column(Integer,
                        ForeignKey('metadatasources.id'),nullable=False),
                    'metadatasource':relationship('MetaDataSource'), #keep it one way
                    #'hardware_id':Column(Integer, #FIXME I *could* put this here but it seems like overkill?
                        #ForeignKey('hardware.id'),nullable=False), #since w/in experiment it wont change?
                 #conflict between desire for doccumentation and need for linkage when recording data
                 #this is the easiest solution but leads to massive data duplication
                }
        )
        return relationship(cls.MetaData) #FIXME may need a primaryjoin on this


###----------------------------------
###  data - datasource history mixins
###----------------------------------

class SWC_HW_EXP_BIND: #FIXME move directly into experiments?
    datafile_subdata_id=None #TODO? as long as I can get to the things needed for analysis it should be ok
    @validates('hardware_id')
    def _wo(self, key, value): return self._write_once(key, value)
    def __init__(self,parent_id,experiment_id,datafilesource_id,channel_id,hardware_id):
        self.parent_id=int(parent_id)
        self.experiment_id=int(experiment_id)
        self.datafilesource_id=int(datafilesource_id) #this works fine, you just have to pass in SWC twice
        self.channel_id=str(channel_id)


class HasSwcHwRecords: #TODO
    """Record of what hardware collected which software channel for which datafilesource/type for a given experiment and the subject that was associated with it what a mess, actually this is a reasonable solution"""
    @declared_attr
    def swc_hw_records(cls):
        tname=cls.__tablename__
        cls.SwcHwRecord=type(
                '%s_SwcHwRecord'%cls.__name__,
                (SWC_HW_EXP_BIND, Base,),
                {   '__tablename__':'%s_swchwrecords'%tname,
                    'parent_id':Column(Integer,ForeignKey('%s.id'%tname), primary_key=True), #has to be here
                    'experiment_id':Column(Integer,ForeignKey('experiments.id'), primary_key=True),
                    'softwarechannel_id':Column(Integer,ForeignKey('softwarechannel.id'),primary_key=True),
                    #'datafilesource_id':Column(Integer, primary_key=True), #pull these from subject.hardware
                    #'channel_id':Column(String(20), primary_key=True),
                    #'__table_args__':(
                        #ForeignKeyConstraint(['datafilesource_id', 'channel_id'],
                            #['softwarechannel.datafilesource_id','softwarechannel.channel_id']), {}),
                    #'datafilesource':relationship('DataFileSource',
                        #primaryjoin='foreign(DataFileSource.id)==%s_swchwrecords.c.datafilesource_id'%tname,
                        #uselist=False),
                    'softwarechannel':relationship('SoftwareChannel',
                        primaryjoin='SoftwareChannel.id==%s_swchwrecords.c.softwarechannel_id'%tname,
                        #primaryjoin=('and_(SoftwareChannel.datafilesource_id=='
                            #'%s_swchwrecords.c.datafilesource_id,'
                            #'SoftwareChannel.channel_id==%s_swchwrecords.c.channel_id)')%(tname,tname),
                        uselist=False),
                    'hardware_id':Column(ForeignKey('hardware.id'),nullable=False),
                }
        )
        return relationship(cls.SwcHwRecord)


class DFS_HW_BIND:
    #how to use to associate a cell to a channel:
    #the cell or subcompartment will have a hardware_id
    #join that hardware_id against the DFS_MW_BIND and then the datafile structure when unpacked must match
    #I should come up with a way to verify the match, even if it is very simple
    @validates('hardware_id') #basically if shit breaks half way through, new experiment
    def _wo(self, key, value): return self._write_once(key, value)
    def __init__(self,Parent=None,DataFileSource=None,Hardware=None,parent_id=None,datafilesource_id=None,hardware_id=None):
        self.parent_id=parent_id
        self.datafilesource_id=datafilesource_id
        self.hardware_id=hardware_id #FIXME probably need hardware=relationship()
        self.AssignID(DataFileSource)
        self.AssignID(Hardware)
        if Parent:
            if Parent.id:
                self.parent_id=Parent.id
            else:
                raise AttributeError


class HasDfsHwRecords: #we bind DFSes to hardware that collects that datafile property #FIXME multiple hardware
    @declared_attr
    def dfs_hw_records(cls):
        cls.DfsHwRecord = type(
                '%s_DfsHwRecord'%cls.__name__,
                (DFS_HW_BIND, Base,),
                {   '__tablename__':'%s_dfshwrecord'%cls.__tablename__,
                    'parent_id':Column(Integer,
                        ForeignKey('%s.id'%cls.__tablename__),primary_key=True),
                    'datafilesource_id':Column(Integer,
                        ForeignKey('datafilesources.id'),primary_key=True),
                    'hardware_id':Column(Integer, #FIXME relationship()
                        ForeignKey('hardware.id')) #FIXME there are multiple hardwares!
                }
        )
        return relationship(cls.DfsHwRecord) #FIXME ideally this should trigger... :/


class MDS_HW_BIND:
    """Class that keeps a record of what hardware was used to record the metadata"""
    @validates('hardware_id') #basically if shit breaks half way through, new experiment
    def _wo(self, key, value): return self._write_once(key, value)
    def __init__(self,parent_id,metadatasource_id,hardware_id):
        self.parent_id=int(parent_id) #experiment_id
        self.metadatasource_id=int(metadatasource_id) #FIXME watchout on the switch to string pk
        self.hardware_id=int(hardware_id) #FIXME probably need hardware=relationship()


class HasMdsHwRecords: #TODO how to enforce a trigger on __init__ unforunately cant because parent_id is needed
    #SessionEvents.after_flush()
    @declared_attr
    def mds_hw_records(cls):
        cls.MdsHwRecord = type(
                '%s_MdsHwRecord'%cls.__name__,
                (MDS_HW_BIND, Base,),
                {   '__tablename__':'%s_mdshwrecord'%cls.__tablename__,
                    'parent_id':Column(Integer, #experiment_id
                        ForeignKey('%s.id'%cls.__tablename__),primary_key=True),
                    'metadatasource_id':Column(Integer,
                        ForeignKey('metadatasources.id'),primary_key=True),
                    'hardware_id':Column(Integer,
                        ForeignKey('hardware.id'),nullable=False)
                }
        )
        return relationship(cls.MdsHwRecord)
    def __init__(self): #FIXME >_<
        session=object_session(self)
        mdses=session.query(self.type_id)[0].metadatasources
        [session.add(self.MdsHwRecord(self.id,mds.id,mds.hardware_id)) for mds in mdses]
    #who the fuck knows how to get event listeners to work for this >_<


###-------------
###  file mixins
###-------------

class HasDataFiles:
    @declared_attr
    def datafiles(cls):
        datafile_association = Table('%s_df_assoc'%cls.__tablename__, cls.metadata,
            #Column('datafile_url',String,primary_key=True),
            #Column('datafile_filename',String,primary_key=True),
            #ForeignKeyConstraint(['datafile_url','datafile_filename'],
                                 #['datafile.url','datafile.filename']),
            Column('datafile_id', ForeignKey('datafile.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__),
                   primary_key=True),
        )
        return relationship('DataFile', secondary=datafile_association,
            primaryjoin='{0}_df_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            #secondaryjoin='and_(DataFile.url=={0}.datafile_url,DataFile.filename=={0}.datafile_filename)'.format(cls.__tablename__+'_df_assoc.c'),
            secondaryjoin='DataFile.id=={0}.datafile_id'.format(cls.__tablename__+'_df_assoc.c'),
            backref=backref('%s'%cls.__tablename__),
        )


class HasFiles:
    @declared_attr
    def files(cls):
        file_association = Table('%s_f_assoc'%cls.__tablename__, cls.metadata,
            #Column('file_url',String,primary_key=True),
            #Column('file_filename',String,primary_key=True),
            #ForeignKeyConstraint(['file_url','file_filename'],
                                 #['file.url','file.filename']),
            Column('file_id', ForeignKey('file.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__),
                   primary_key=True),
        )
        return relationship('File', secondary=file_association,
            primaryjoin='{0}_f_assoc.c.{0}_id=={0}.c.id'.format(cls.__tablename__),
            #secondaryjoin='and_(File.url=={0}.file_url,File.filename=={0}.file_filename)'.format(cls.__tablename__+'_f_assoc.c'),
            secondaryjoin='File.id=={0}.file_id'.format(cls.__tablename__+'_f_assoc.c'),
            backref=backref('%s'%cls.__tablename__),
        )


###---------------
###  Has citeables
###---------------

class HasCiteables:
    @declared_attr
    def citeables(cls):
        cite_association = Table('%s_citeables'%cls.__tablename__,cls.metadata,
            Column('citeable_id', ForeignKey('citeable.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('Citeable', secondary=cite_association,backref=backref('%s_citer'%cls.__tablename__))

###--------------
###  Has reagents
###--------------

class HasReagentTypes:
    @declared_attr
    def reagenttypes(cls):
        reagenttype_association = Table('%s_reagenttypes'%cls.__tablename__,cls.metadata,
            Column('reagenttype_id', ForeignKey('reagenttypes.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('ReagentType', secondary=reagenttype_association,backref=backref('%s_used'%cls.__tablename__))


class HasReagents:
    @declared_attr
    def reagents_used(cls): #FIXME figure out if we can get away with having only one things...
        reagent_association = Table('%s_reagents'%cls.__tablename__,cls.metadata,
            Column('reagent_id', ForeignKey('reagents.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True),
            #removed foreigkeyconstraint because switched reagents to a surrogate primary key
        )
        return relationship('Reagent', secondary=reagent_association,backref=backref('used_in_%s'%cls.__tablename__))

###--------------
###  Has hardware
###--------------

class HasHardware:
    @declared_attr
    def hardware(cls):
        hardware_association = Table('%s_hardware'%cls.__tablename__,cls.metadata,
            Column('hardware_id', ForeignKey('hardware.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('Hardware', secondary=hardware_association,backref=backref('%s_used'%cls.__tablename__))

###-----------------
###  Has experiments
###-----------------

class HasExperiments:
    paramNames=tuple #persistable values that are not filled in at init
    preStepNames=tuple
    interStepNames=tuple
    postStepNames=tuple
    child_type=Base #FIXME?
    @declared_attr
    def experiments(cls):
        experiments_association = Table('%s_experiments'%cls.__tablename__,cls.metadata,
            Column('experiments_id', ForeignKey('experiments.id'), primary_key=True),
            Column('%s_id'%cls.__tablename__, ForeignKey('%s.id'%cls.__tablename__), primary_key=True))
        return relationship('Experiment', secondary=experiments_association,backref=backref('%s'%cls.__tablename__))

###-----------------------------------------
###  Has properties, hstore, key/value store
###-----------------------------------------

class Properties: #FIXME HasKeyValueStore
    """Not for data!""" #TODO how to query this...
    #FIXME this is hstore from postgres except slower and value is not a blob
    key=Column(String(50),primary_key=True) #tattoo, eartag, name, *could* use coronal/sagital for slices, seems dubious... same with putting cell types in here... since those are technically results... #FIXME for some reason this accepts ints for a key... FIXME WATCH OUT for the type change on commit! it doesn't update the instace! make sure to expire them
    value=Column(String(50)) #if the strings actually need to be longer than 50 we probably want something else
    def __repr__(self):
        return '\n%s {%s,%s}'%(self.parent_id,self.key,self.value)
    def strHelper(self,depth=0):
        tabs='\t'*depth
        return '%s{%s,%s}'%(tabs,self.key,self.value)


class HasProperties: #FIXME set this up to use hstore if postgres is detected
    #TODO __init__ with kwargs and the like for all these or what?
    @declared_attr
    def properties(cls):
        return Column(DictType)
    """
    @declared_attr
    def properties(cls): #this is an UNVALIDATED STORE
        cls.Properties=type(
                '%sProperties'%cls.__name__,
                (Properties, Base,),
                {   '__tablename__':'%s_properties'%cls.__tablename__,
                    'parent_id':Column(Integer, #FIXME nasty errors inbound
                        ForeignKey('%s.id'%cls.__tablename__),primary_key=True), #FIXME check autoincrement
                    'parent':relationship('%s'%cls.__name__, uselist=False,
                        backref=backref('__properties',collection_class=attribute_mapped_collection('key')))
                }
        )
        #FIXME I don't understand why I do not need to init with parent_id...
        return association_proxy('__properties','value',creator=lambda k,v: cls.Properties(key=k,value=v))
        #return relationship(cls.Properties,collection_class=attribute_mapped_collection('key'))
    """


###-------------------------------------------
###  Class for things that have tree structure
###-------------------------------------------

class HasTreeStructure:
    """useful methods for objects w/ tree structure defined by parent and children"""
    @property
    def rootParent(self): #FIXME probably faster to do this with a func to reduce queries
        if self.parent:
            return self.parent.rootParent
        else:
            return self

    @property
    def lastChildren(self):
        def recurse(allChilds):
            new_allChilds=[]
            for child in allChilds:
                try:
                    new_allChilds.extend(child.children)
                except:
                    pass
            if new_allChilds: #this prevents getting self.children again
                return recurse(new_allChilds)
            else:
                return allChilds
        if self.children:
            return recurse(self.children)
        else:
            return []

    def nthChildren(self,n=0,allChilds=[]):
        if n:
            if not allChilds and self.children:
                return self.nthChildren(n-1,self.children)
            else:
                new_allChilds=[]
                for child in allChilds:
                    try:
                        new_allChilds.extend(child.children)
                    except:
                        pass
                return self.nthChildren(n-1,new_allChilds)
        else:
            return allChilds




