from database.models import *

import numpy as np

from database.imports import printD,ploc,datetime,timedelta

#FIXME TODO, make all these things use queries instead of generating you nub
#and failover to create if absent

#creation order
#order=(Person,Project,Experiment,SlicePrep,Repository,RepoPath,DOB,Mouse,Sire,Dam,MatingRecord,Litter) #TODO
#order=(t_people,t_dob)# you get the idea... maybe make a tree in a dict or something?

class TEST:
    def __init__(self,session,num=None,autocommit=True,Thing=None):
        self.Thing=Thing
        self.num=num
        self.session=session
        self.records=[] #this is the output
        self.setup()
        self.make_all()
        if autocommit:
            self.commit()
    def make_date(self):
        from datetime import date,timedelta
        num=self.num
        seed=date.today()
        days=np.random.randint(365*15,365*100,num) #historical dates not supported in the test
        deltas=[timedelta(days=int(d)) for d in days] #fortunately timedelta defaults to days so I dont have to read the doccumentation for map
        return [seed - delta for delta in deltas]

    def make_datetime(self,num=None,years=5):
        from datetime import datetime,timedelta
        if not num:
            num=self.num
        seed=datetime.now()
        days=np.random.randint(0,365*years,num) #historical dates not supported in the test
        hours=np.random.randint(0,12,num) #historical dates not supported in the test
        deltas=[timedelta(days=int(d),hours=int(h)) for d,h in zip(days,hours)] #fortunately timedelta defaults to days so I dont have to read the doccumentation for map
        return [seed - delta for delta in deltas]

    def make_sex(self):
        num=self.num
        #sex_seed=np.random.choice(2,num,.52)
        #sex_seed=np.ones(num)
        sex_arr=np.array(list('m'*num))
        sex_arr[:int(num/2)]='f'
        return sex_arr

    def make_NONE(self,*arrays): #FIXME very broken for strings
            noneArr=[] 
            num_nones=int(self.num/5)+1
            [noneArr.append(None) for i in range(num_nones)]
            noneArr=np.array(noneArr)
            for array in arrays:
                #array=np.array(array)
                array[:num_nones]=noneArr
                printD([n for n in array])
                np.random.shuffle(array)

    #methods every class should have
    def setup(self):
        #self.Thing
        query=self.session.query(Mouse)
        if not query.count():
            pass

    def make_all(self):
        pass

    def commit(self):
        self.session.add_all(self.records)
        self.session.commit()


###--------
###  people
###--------

class t_people(TEST):
    def make_name(self,names_per=1):
        num=self.num
        names=open('names.txt')
        nlist=[] 
        while 1:
            name=names.readline()
            if name:
                nlist.append(name[:-1])
            else:
                break
        num=len(nlist)
        #FIXME lol broekn!!!! though if I test w/ more than 5000 names..
        all_names=[np.random.permutation(nlist)[:num] for i in range(names_per)]
        return all_names

    def make_role(self):
        num=self.num
        roles=['wanker','narf','pi','turd','subject','gradstudent','postdoc']
        #for the recored putting subjects in with everyone else is TOTALLY a HIPA violation
        rollseed=np.random.choice(len(roles),num)
        out=[roles[i] for i in rollseed]
        return out
        
    def make_all(self):
        num=self.num
        pfns, fns, mns, lns = self.make_name(4)
        #print(pfns[num],fns[num],mns[num],lns[num])
        genders=self.make_sex()
        #print(genders)
        birthdates=self.make_date()
        roles=self.make_role()
        ntids=np.unique(np.int32(np.random.sample(num*2)*50000))[:num] #still broken
        #ntids=np.random.randint(0,99999,num) #test for non unique
        #ntids=list(ntids)
        ntids=[int(n) for n in ntids]


        #self.make_NONE(pfns,fns,mns,lns,genders,birthdates,roles,ntids) #BROKEN

        self.records=[]
        self.records+=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(8,num)]
        self.records+=[Person(FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(1)]
        self.records+=[Person(PrefixName=pfns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(1,2)]
        self.records+=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(2,3)]
        self.records+=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(3,4)]
        self.records+=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(4,5)]
        self.records+=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(5,6)]
        self.records+=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            Birthdate=birthdates[i]) for i in range(6,7)]
        self.records+=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i]) for i in range(7,8)]

    def query(self):
        #print([p.Gender for p in self.session.query(Person)])
        print([p for p in self.session.query(Person)])

###------
###  Mice
###------

class t_dob(TEST):
    def __init__(self,session,num=None,datetimes=None):
        self.datetimes=datetimes
        super().__init__(session,num)
    def make_all(self):
        if not self.datetimes:
            dts=self.make_datetime(years=2)
            self.records=[DOB(d) for d in dts]
        else:
            self.records=[DOB(d) for d in self.datetimes]


class t_breeders(TEST):
    """makes n pairs of breeders"""
    def make_all(self):
        mice=t_mice(self.session,4*self.num)
        sires=self.session.query(Mouse).filter(Mouse.sex_id=='m')
        dams=self.session.query(Mouse).filter(Mouse.sex_id=='f')
        self.records=[Sire(sire) for sire in sires[:self.num]]+[Dam(dam) for dam in dams[:self.num]]


class t_mating_record(TEST):
    def make_all(self):
        from datetime import datetime,timedelta
        breeders=t_breeders(self.session,int(self.num/6)+1)

        sires=[s for s in self.session.query(Sire)]
        dams=[d for d in self.session.query(Dam)]
        sire_arr=np.random.choice(len(sires),self.num)
        dam_arr=np.random.choice(len(sires),self.num)

        
        mins=np.random.randint(-60,60,self.num)
        now=datetime.now()

        self.records=[MatingRecord(Sire=sires[sire_arr[i]],Dam=dams[dam_arr[i]],startDateTime=now+timedelta(hours=i),stopDateTime=now+timedelta(hours=int(i)+12,minutes=int(mins[i]))) for i in range(self.num)]


class t_litters(TEST):
    def make_all(self): #FIXME also need to test making without a MR
        from datetime import timedelta
        mrs=t_mating_record(self.session,self.num)

        td=timedelta(days=19)
        dts=[mr.est_e0+td for mr in mrs.records]
        dobs=t_dob(self.session,datetimes=dts)
        for mr,dob in zip(mrs.records,dobs.records):
            mr.dob_id=dob.id 

        self.records=[Litter(mr) for mr in mrs.records]
    def add_members(self):
        mice=[] #FIXME there has to be a better way
        #litter_sizes=np.random.randint(6,20,self.num) #randomize litter size
        litter_sizes=np.int32(np.ones(self.num)*20)

        #compare the two following methods: Second one seems faster, need to verify

        #ms=[self.records[i].make_members(litter_sizes[i]) for i in range(self.num)]
        #[mice.extend(m) for m in ms]
        #self.session.add_all(mice)
        for lit,i in zip(self.records,range(self.num)):
            lit.members.extend([Mouse(Litter=lit,sex_id='u') for i in range(litter_sizes[i])])

        #VS
        #[self.session.add_all(self.records[i].make_members(litter_sizes[i])) for i in range(self.num)]

        self.session.commit()


class t_mice(TEST):
    def make_all(self):
        dobs=t_dob(self.session,self.num)
        tags=np.random.randint(0,1000,self.num)
        sexes=self.make_sex()
        self.records=[Mouse(eartag=int(tags[i]),sex_id=sexes[i],DOB=dobs.records[i]) for i in range(self.num)]

###--------------------
###  subjects continued
###--------------------

class t_slice(TEST):
    def make_all(self):
        preps=self.session.query(Experiment).filter_by(type='acute slice prep')
        
        self.records=[]
        [[self.records.append(Slice(Prep=prep,startDateTime=datetime.now()+timedelta(hours=i))) for i in range(self.num)] for prep in preps] #FIXME amplification of numbers


class t_cell(TEST):
    def make_all(self):
        slices=[s for s in self.session.query(Slice)]
        patches=[p for p in self.session.query(Experiment).filter_by(type='acute slice prep')]
        headstages=[h for h in self.session.query(Hardware).filter_by(type='headstage')][:2]
        self.records=[]
        z=0
        for p in patches:
            for i in range(z,len(slices)): #120 #FIXME pretty sure RI is broken here
                s=slices[i]
                for j in range(self.num):
                    self.records.extend([Cell(Hardware=[h],Slice=s,Experiments=[p]) for h in headstages])
                try:
                    if slices[i+1].mouse_id != s.mouse_id: #FIXME this should catch automatically when using session.add
                        z=i+1 #FIXME constraint!!!!
                        break
                except IndexError: pass


class t_c2c(TEST):
    def make_all(self):
        cells=self.session.query(Cell)
        #circular link
        self.records=[]
        self.records.extend([CellPairs(cells[i-2],cells[i]) for i in range(cells.count())]) #this adds tripplets since a single row here is treated as simultaneous, INCIDENTALLY FIXME this is a problem because it means that a=b=c IS NOT TRUE on this set a=b b=c a!=c fuck
        #HOWEVER: this is less of an integrity concern than having to make two entries for each pair, for higher numbers of recordin I should probably do this as cell1 cell2 cell3 cell4 to prevent stuipd combinatorial nightmares

        #pairs
        self.records.extend([CellPairs(cells[i],cells[i+1]) for i in range(0,cells.count()-1,2)])
        #self.records.extend([CellPairs(cells[i+1],cells[i]) for i in range(0,cells.count()-1,2)])



###-------------
###  experiments
###-------------

class t_project(TEST):
    def make_all(self):
        iacuc_protocol_id=None
        blurb=None

        self.records=[Project(lab='Scanziani',iacuc_protocol_id=iacuc_protocol_id,blurb=blurb) for n in range(self.num)]
        count=0
    def add_people(self): #has to be called after commit :/
        people=t_people(self.session,100)
        #HRM only queries can leverage the power of .filter
        pis=[pi for pi in self.session.query(Person).filter(Person.Role=='pi')]
        pi_n=np.random.choice(len(pis),self.num)

        #people=[p for p in self.session.query(Person)]
        people_n=[np.random.permutation(people.records)[:np.random.randint(1,20)] for i in range(self.num)] #+pis[pi_n[i]] 
        assocs=[]
        count=0
        for rec,people in zip(self.records,people_n):
            #assocs.append(person_to_project(rec,pis[pi_n[count]]))
            assocs+=[person_to_project(rec,person) for person in people]
            #[rec.people.append(person) for person in people] #FIXME somehow this no workey
            count+=1
        self.session.add_all(assocs)
        self.session.commit()


class t_experiment(TEST):
    def __init__(self,session,num=None,num_projects=None):
        self.num_projects=num_projects
        super().__init__(session,num)
    def make_all(self):
        #from time import sleep
        projects=t_project(self.session,self.num_projects)
        projects.add_people()
        #projects.commit() #FIXME do I need to readd? or can I just commit directly?

        lits=t_litters(self.session,1)
        lits.add_members()
        #lits.commit()

        mice=[m for m in self.session.query(Mouse).filter(Mouse.breedingRec==None,Mouse.dod==None)] #FIXME


        #mice=[m for m in self.session.query(Mouse).filter(Mouse.dod==None)]
        self.records=[]
        for p in projects.records:
            #printD(p) #FIXME apparently p.__dict__ is not populated until AFTER you call the object...
            #printD([t for t  in p.__dict__.items()]) #FIXME what the fuck, sometimes this catches nothing!?
            ms=[mice[i] for i in np.random.choice(len(mice),self.num)] #FIXME missing mouse
            #TODO need to test with bad inputs
            exps=[p.people[i] for i in np.random.choice(len(p.people),self.num)]
            datetimes=self.make_datetime()

            self.records+=[Experiment(Project=p,Person=exps[i],startDateTime=datetimes[i],type='in vitro patch') for i in range(self.num)] #FIXME lol this is going to reaveal experiments on mice that aren't even born yet hehe


class t_patch(TEST):
    def make_all(self):
        #mice=[m for m in self.session.query(Mouse).filter(Mouse.dod==None)]
        preps=[p for p in self.session.query(Experiment).filter_by(type='acute slice prep')]
        project=self.session.query(Project)[0]
        person=self.session.query(Person)[0]
        acsf=self.session.query(Reagent).filter_by(type_id=2)[0] #FIXME these are terrible useage patterns
        internal=self.session.query(Reagent).filter_by(type_id=3)[0] #FIXME these are terrible useage patterns
        self.session.add_all([acsf,internal])
        #self.session.flush() #shit not working FIXME
        self.session.commit()
        exptype=self.session.query(ExperimentType).filter_by(abbrev='patch')[0]

        self.records=[]
        datetimes=self.make_datetime()
        [self.records.extend([Experiment(Project=project,Person=person,Reagents=[internal,acsf],startDateTime=datetimes[i],ExpType=exptype) for i in range(self.num)]) for p in preps] #FIXME classic mouse not born yet problem


class t_sliceprep(TEST):
    def make_all(self):
        project=self.session.query(Project)[0]
        person=self.session.query(Person)[0]
        sucrose=self.session.query(Reagent).filter_by(type_id=1)[0]
        exptype=self.session.query(ExperimentType).filter_by(abbrev='prep')[0]
        self.records=[Experiment(Project=project,Person=person,Reagents=[sucrose],startDateTime=datetime.now()-timedelta(int(np.random.randint(1))),ExpType=exptype) for i in range(self.num)] #FIXME need to find a way to propagate mouse w/ RI
    def add_mice(self):
        mice=self.session.query(Mouse).filter_by(sex_id='u')[100:100+self.num]
        np.random.shuffle(mice)
        for i in range(self.num):
            #mice[i].experiment_id=self.records[i].id
            self.records[i].subjects.append(mice[i])
        self.session.commit()
        


###------
###  data
###------

class t_repo(TEST):
    def make_all(self):
        self.records=[]
        repos=(
                    'file:///C:/asdf/test1',
                    'file:///C:/asdf/test2//',
                    #'http://www.google.com/', #FIXME broken as expected?
                    #'https://www.google.com/' #FIXME broken as expected?
        )
        self.records+=[Repository(url=r) for r in repos]
        #FIXME for some reason adding the fully inited Repository(url='asdf') inside the list didn't work...
        #figure out why please?!


class t_datasource(TEST):
    def make_all(self):
        self.records=[
            DataSource(name='tom'),
        ]


class t_metadatasource(TEST):
    def make_all(self):
        self.records=[
            MetaDataSource(name='the void',prefix='T',unit='Pa'),
        ]


class t_datafile(TEST):
    #def __init__(self,session,num=None,num_experiments=None,num_projects=None):
        #self.num_projects=num_projects
        #self.num_experiments=num_experiments
        #super().__init__(session,num)
    def make_all(self):
        repo=t_repo(self.session)
        ds=self.session.query(DataSource)[0]
        data=[]
        count=0
        cells=self.session.query(Cell)
        for c1,c2 in zip(cells[:-1],cells[1:]):
            for rp in repo.records:
                data+=[DataFile(Repo=rp,filename='exp%s_cells_%s_%s_%s.data'%(c1.experiments[0].id,c1.id,c2.id,df),DataSource=ds,Subjects=[c1,c2]) for df in range(self.num)] 
        self.records=data


class t_dfmetadata(TEST):
    def make_all(self):
        ds=self.session.query(MetaDataSource)[0]
        self.records=[]
        [self.records.extend([d.MetaData(i,DataFile=d,MetaDataSource=ds) for i in range(self.num)]) for d in self.session.query(DataFile)]
###-----------
###  inventory
###-----------

class t_hardware(TEST):
    def setup(self):
        self.amps=[Hardware(type='amplifier',unique_id='0012312'),Hardware(type='amplifier',unique_id='bob')]
        self.session.add_all(self.amps)
        self.session.flush()

    def make_all(self):
        self.records=[]
        [[self.records.append(Hardware(type='headstage',unique_id='%s'%i, Parent=amp)) for i in range(2)] for amp in self.amps]
        #printD(self.records) #FIXME this whole make all is broken


class t_hwmetadata(TEST):
    def make_all(self):
        ds=self.session.query(MetaDataSource)[0] #TODO make sure this breaks, FIXME it breaks but not where expected...
        self.records=[]
        [self.records.extend([h.MetaData(i,Parent=h,MetaDataSource=ds) for i in range(self.num)]) for h in self.session.query(Hardware)]
        

class t_reagenttype(TEST):
    def make_all(self):
        self.records=[
            ReagentType(name='poop'),
            ReagentType(name='poop1'),
            ReagentType(name='poop2')
        ]
    

class t_reagent(TEST):
    def make_all(self):
        rts=self.session.query(ReagentType)
        self.records=[Reagent(Type=r) for r in rts]


def run_tests(session):
    #FIXME for some reason running these sequentially causes all sorts of problems...
    #RESPONSE turns out it is because I'm trying to make EXACTLY the same tables again and an identical mapped instance already exists
    #so it doesnt happen with people, but a collision *could* happen

    #FIXME the real test will be to vary the number of projects, experiments and datafiles
    #compare these two cases with profiler
    #d=t_datafile(session,5000,2,4) #add 1000 datafiles to 3 projects each with 10 experiments takes about 16 seconds, I'd say we're ok here
    #d=t_datafile(session,20,500,4) #add 1000 datafiles to 3 projects each with 10 experiments takes about 16 seconds, I'd say we're ok here

    #d=t_datafile(session,10,50,4)
    
    #[print(df.creation_DateTime) for df in session.query(DataFile)]

    ds=t_datasource(session)
    mds=t_metadatasource(session)
    #h=t_hardware(session)
    hwmd=t_hwmetadata(session,5)
    #t_experiment(session,1,4) #FIXME argh, so many things can become inconsistent...
    t_people(session,20)
    t_project(session,1)
    #t_mice(session,300)
    l=t_litters(session,20)
    l.add_members()


    rt=t_reagenttype(session)
    i=t_reagent(session)

    sp=t_sliceprep(session,5)
    sp.add_mice()
    p=t_patch(session,1) #FIXME you know it might be good to force a new exp rec when any of the variables changes... like the internal...? think think

    s=t_slice(session,4)
    c=t_cell(session,5)
    #c2c=t_c2c(session) #no longer used

    d=t_datafile(session,5)#,2,1) #FIXME eating memory
    dfmd=t_dfmetadata(session,10) #as in 8 gigs of memory...

    #session.commit()


    #l=t_litters(session,20) #FIXME another wierd error here... saying that I tried to add a mouse as a breeder twice... hrm...
    #l.add_members()

    #printD([m for m in session.query(Mouse)]) #FIXME mice arent getting made?


def main():
    pass


if __name__=='__main__':
    main()
