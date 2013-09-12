#FIXME these imports should really go in a models subfolder to simplify everything :/
from database.constraints       import *
from database.experiments       import *
from database.inventory         import *
from database.people            import *
from database.notes             import *
from database.mice              import *
from database.data              import *

import numpy as np

from debug import ploc


class TEST:
    def __init__(self,session,num=None):
        self.num=num
        self.session=session
        self.make_all()
    def make_date(self):
        from datetime import date,timedelta
        num=self.num
        seed=date.today()
        days=np.random.randint(365*15,365*100,num) #historical dates not supported in the test
        deltas=[timedelta(days=int(d)) for d in days] #fortunately timedelta defaults to days so I dont have to read the doccumentation for map
        return [seed - delta for delta in deltas]

    def make_datetime(self,num=None):
        from datetime import datetime,timedelta
        if not num:
            num=self.num
        seed=date.utcnow()
        days=np.random.randint(0,365*5,num) #historical dates not supported in the test
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
        ntids=np.int32(np.int32(np.random.sample(num)*100000)/2) #still broken
        #ntids=np.random.randint(0,99999,num) #test for non unique
        ntids=list(ntids)


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
        repo.commit()
        paths=(
                '/repotest/asdf1', #yep, it caught the similarity
                'repotest/asdf2',
                'repotest/asdf3/'
              )
        self.records=[]
        for r in repo.records:
            printD(r)
            self.records+=([RepoPath(Repo=r,path=path) for path in paths])

class t_datafile(TEST):
    def make_all(self):
        repop=t_repopath(self.session)
        repop.commit()
        experiment=t_experiment(self.session,100)
        experiment.commit()
        data=[]
        count=0
        for exp in experiment.records:
            count+=1
            for rp in repop.records:
                data+=[DataFile(RepoPath=rp,filename=str(fn)+'.data',Experiment=exp) for fn in range(5*count)]
        self.records=data
            
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
        people.commit()
        #HRM only queries can leverage the power of .filter
        pis=[pi for pi in self.session.query(Person).filter(Person.Role=='pi')]
        pi_n=np.random.choice(len(pis),self.num)

        #people=[p for p in self.session.query(Person)]
        people_n=[np.random.permutation(people.records)[:np.random.randint(1,20)] for i in range(self.num)]
        assocs=[]
        count=0
        for rec,people in zip(self.records,people_n):
            assocs.append(person_to_project(rec,pis[pi_n[count]]))
            assocs+=[person_to_project(rec,person) for person in people]
            #[rec.people.append(person) for person in people] #FIXME somehow this no workey
            count+=1
        self.session.add_all(assocs)
        self.session.commit()


class t_experiment(TEST):
    def make_all(self):
        projects=t_project(self.session,3)
        projects.commit()
        projects.add_people()
        projects.commit() #FIXME do I need to readd? or can I just commit directly?

        self.records=[]
        for p in projects.records:
            mice=[m for m in self.session.query(Mouse).filter(Mouse.dod==None)]
            ms=[mice[i] for i in np.random.choice(len(mice),self.num)]
            #TODO need to test with bad inputs
            exps=[p.people[i] for i in np.random.choice(len(p.people),self.num)]
            datetimes=self.make_datetime()

            self.records+=[Experiment(Project=p,Experimenter=exps[i],Mouse=ms[i],dateTime=datetimes[i])]






def run_tests(session):
    #people=t_people(session,10)
    #people.commit()
    #people.query()

    #repos=t_repo(session)
    #printD([r.url for r in repos.records])

    ps=t_project(session,10)
    ps.commit()
    ps.add_people()
    ps.commit()
    printD([p.pi for p in ps.records])

    #d=t_datafile(session,100)
    #d.commit()



def main():
    pass


if __name__=='__main__':
    main()
