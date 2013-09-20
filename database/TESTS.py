from database.models import *

import numpy as np

from imports import printD,ploc,datetime,timedelta

#FIXME flush instead of commit will populate primary keys!

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
        seed=datetime.utcnow()
        days=np.random.randint(0,365*years,num) #historical dates not supported in the test
        hours=np.random.randint(0,12,num) #historical dates not supported in the test
        deltas=[timedelta(days=int(d),hours=int(h)) for d,h in zip(days,hours)] #fortunately timedelta defaults to days so I dont have to read the doccumentation for map
        return [seed - delta for delta in deltas]

    def make_sex(self):
        num=self.num
        sex_seed=np.random.choice(2,num,.52)
        sex_arr=np.array(list('m'*num))
        sex_arr[sex_seed==0]='f'
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
        self.Thing
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
        mice.commit()
        sires=self.session.query(Mouse).filter(Mouse.sex_id=='m')
        dams=self.session.query(Mouse).filter(Mouse.sex_id=='f')
        self.records=[Sire(sire) for sire in sires[:self.num]]+[Dam(dam) for dam in dams[:self.num]]


class t_mating_record(TEST):
    def make_all(self):
        from datetime import datetime,timedelta
        breeders=t_breeders(self.session,int(self.num/6)+1)
        breeders.commit()

        sires=[s for s in self.session.query(Sire)]
        dams=[d for d in self.session.query(Dam)]
        sire_arr=np.random.choice(len(sires),self.num)
        dam_arr=np.random.choice(len(sires),self.num)

        
        mins=np.random.randint(-60,60,self.num)
        now=datetime.utcnow()

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
        mrs.commit()

        self.records=[Litter(mr) for mr in mrs.records]
    def add_members(self):
        mice=[] #FIXME there has to be a better way
        #litter_sizes=np.random.randint(6,20,self.num) #randomize litter size
        litter_sizes=np.int32(np.ones(self.num)*20)

        #compare the two following methods: Second one seems faster, need to verify

        #ms=[self.records[i].make_members(litter_sizes[i]) for i in range(self.num)]
        #[mice.extend(m) for m in ms]
        #self.session.add_all(mice)

        #VS
        [self.session.add_all(self.records[i].make_members(litter_sizes[i])) for i in range(self.num)]

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
        preps=t_sliceprep(self.session, int(self.num/6)) #8 being the average number of slices per mouse
        
        self.records=[]
        [[self.records.append(Slice(Prep=prep,startDateTime=datetime.utcnow()+timedelta(hours=i))) for i in range(self.num)] for prep in preps.records] #FIXME amplification of numbers


class t_cell(TEST):
    def make_all(self):
        Cell(Cell=None)
        self.records=None

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
        from time import sleep
        projects=t_project(self.session,self.num_projects)
        projects.add_people()
        #projects.commit() #FIXME do I need to readd? or can I just commit directly?

        lits=t_litters(self.session,50)
        lits.add_members()
        #lits.commit()

        mice=[m for m in self.session.query(Mouse).filter(Mouse.breedingRec==None,Mouse.dod==None)]

        #mice=[m for m in self.session.query(Mouse).filter(Mouse.dod==None)]
        self.records=[]
        for p in projects.records:
            #printD(p) #FIXME apparently p.__dict__ is not populated until AFTER you call the object...
            #printD([t for t  in p.__dict__.items()]) #FIXME what the fuck, sometimes this catches nothing!?
            ms=[mice[i] for i in np.random.choice(len(mice),self.num)] #FIXME missing mouse
            #TODO need to test with bad inputs
            exps=[p.people[i] for i in np.random.choice(len(p.people),self.num)]
            datetimes=self.make_datetime()

            self.records+=[Experiment(Project=p,Person=exps[i],Mouse=ms[i],startDateTime=datetimes[i]) for i in range(self.num)] #FIXME lol this is going to reaveal experiments on mice that aren't even born yet hehe


class t_sliceprep(TEST):
    def make_all(self):
        project=self.session.query(Project)[0]
        person=self.session.query(Person)[0]
        mice=self.session.query(Mouse).filter_by(sex_id='u')[:5]
        self.records=[SlicePrep(Project=project,Person=person,startDateTime=datetime.utcnow()-timedelta(int(np.random.randint(1))),mouse_id=mouse.id,sucrose_id='poop') for mouse in mice]


###------
###  data
###------

class t_repo(TEST):
    def make_all(self):
        self.records=[]
        repos=(
                    'file:///C:/',
                    'http://www.google.com/', #FIXME broken as expected?
                    'https://www.google.com/' #FIXME broken as expected?
        )
        self.records+=[Repository(url=r) for r in repos]
        #FIXME for some reason adding the fully inited Repository(url='asdf') inside the list didn't work...
        #figure out why please?!


class t_repopath(TEST):
    def make_all(self):
        repo=t_repo(self.session)
        paths=(
                '/repotest/asdf1', #yep, it caught the similarity
                'repotest/asdf2',
                'repotest/asdf3/'
              )
        self.records=[]
        for r in repo.records:
            printD(r.url)
            self.records+=([RepoPath(Repo=r,path=path) for path in paths])


class t_datasource(TEST):
    def make_all(self):
        self.records=[DataSource(name='tom',prefix='u',unit='F')]


class t_datafile(TEST):
    def __init__(self,session,num=None,num_experiments=None,num_projects=None):
        self.num_projects=num_projects
        self.num_experiments=num_experiments
        super().__init__(session,num)
    def make_all(self):
        repop=t_repopath(self.session)
        experiment=t_experiment(self.session,self.num_experiments,self.num_projects) #I am getting  3x the number I request here, a yes, that is because I'm looking at 3 projects
        data=[]
        ds=t_datasource(self.session)
        count=0
        for exp in experiment.records:
            for rp in repop.records:
                data+=[DataFile(RepoPath=rp,filename='exp%s_%s.data'%(exp.id,df),Experiment=exp,DataSource=ds.records[0]) for df in range(self.num)] #so it turns out that the old naming scheme was causing the massive slowdown as the number of datafiles went as the square of the experiment number! LOL
        self.records=data

class t_dfmetadata(TEST):
    def make_all(self):
        ds=self.session.query(DataSource)[0]
        self.records=[]
        [self.records.extend([d.MetaData(i,DataFile=d,DataSource=ds) for i in range(self.num)]) for d in self.session.query(DataFile)]
###-----------
###  inventory
###-----------

class t_hardware(TEST):
    def setup(self):
        self.amps=[Hardware(type='amplifier',unique_id='0012312'),Hardware(type='amplifier',unique_id='bob')]
        self.session.add_all(self.amps)
        self.session.commit()

    def make_all(self):
        self.records=[]
        [[self.records.append(Hardware(type='headstage',unique_id='%s'%i, Parent=amp)) for i in range(2)] for amp in self.amps]
        #printD(self.records) #FIXME this whole make all is broken

class t_hwmetadata(TEST):
    def make_all(self):
        ds=self.session.query(DataSource)[0]
        self.records=[]
        [self.records.extend([h.MetaData(i,Parent=h,DataSource=ds) for i in range(self.num)]) for h in self.session.query(Hardware)]
        

class t_reagent(TEST):
    def make_all(self):
        self.records=[ReagentInventory(name='poop')]
    

def run_tests(session):
    #FIXME for some reason running these sequentially causes all sorts of problems...
    #RESPONSE turns out it is because I'm trying to make EXACTLY the same tables again and an identical mapped instance already exists
    #so it doesnt happen with people, but a collision *could* happen
    #people=t_people(session,10)
    #people.commit()
    #people.query()

    #repos=t_repo(session)
    #repos.commit()
    #printD([r.url for r in repos.records])

    #rps=t_repopath(session)
    #rps.commit()
    #printD([r.id for r in rps.records])

    #ps=t_project(session,10)
    #ps.commit()
    #ps.add_people()
    #ps.commit()
    #printD([[t for t in p.__dict__] for p in ps.records])

    #p=t_project(session,3)
    #p.commit()
    #p.add_people()
    #printD([[t for t in p.__dict__.items()] for p in session.query(Project)])

    #e=t_experiment(session,100)
    #e.commit()


    #FIXME the real test will be to vary the number of projects, experiments and datafiles
    #compare these two cases with profiler
    #d=t_datafile(session,5000,2,4) #add 1000 datafiles to 3 projects each with 10 experiments takes about 16 seconds, I'd say we're ok here
    #d=t_datafile(session,20,500,4) #add 1000 datafiles to 3 projects each with 10 experiments takes about 16 seconds, I'd say we're ok here

    #d=t_datafile(session,10,50,4)
    d=t_datafile(session,1,1,1)
    dfmd=t_dfmetadata(session,50)
    
    #[print(df.creation_DateTime) for df in session.query(DataFile)]

    h=t_hardware(session)
    hwmd=t_hwmetadata(session,20)

    i=t_reagent(session)

    s=t_slice(session,100)


    #l=t_litters(session,20) #FIXME another wierd error here... saying that I tried to add a mouse as a breeder twice... hrm...
    #l.add_members()

    #printD([m for m in session.query(Mouse)]) #FIXME mice arent getting made?


def main():
    pass


if __name__=='__main__':
    main()
