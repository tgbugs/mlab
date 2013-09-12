#FIXME these imports should really go in a models subfolder to simplify everything :/
from database.constraints       import *
from database.experiments       import *
from database.inventory         import *
from database.people            import *
from database.notes             import *
from database.mice              import *
from database.data              import *

import numpy as np



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

    def make_sex(self):
        num=self.num
        sex_seed=np.random.choice(2,num,.52)
        sex_arr=np.array(list('m'*num))
        sex_arr[sex_seed==0]='f'
        return sex_arr

    def make_NONE(self,*arrays):
            noneArr=[] 
            num_nones=int(self.num/5)
            [noneArr.append(None) for i in range(num_nones)]
            for array in arrays:
                array[:num_nones]=noneArr
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

        self.make_NONE(pfns,fns,mns,lns,genders,birthdates,roles,ntids)
        #FIXME apparently None works differently than kwargs...

        self.records=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(num)]
        #print(self.people)

    def query(self):
        #print([p.Gender for p in self.session.query(Person)])
        print([p for p in self.session.query(Person)])

###------
###  data
###------

class t_repo(TEST):
    def make_all(self):
        repolist=[
                    Repository(url='file:///C:/'),
                    Repository(url='http://www.google.com/'),
                    Repository(url='https://www.google.com/')
        ]
        self.records=repolist

class t_repopath(TEST):
    def make_all(self):
        repo=t_repo(self.session)
        repo.commit()
        paths=['/repotest/asdf' #FIXME these will error out like crazy
               ,'repotest/asdf'
               ,'repotest/asdf/'
              ]
        self.records=[]
        for r in repo.records:
            self.records+=([RepoPath(Repository=r,path=path) for path in paths])

class t_datafile(TEST):
    def make_all(self):
        repop=t_repopath(self.session)
        repop.commit()
        experiment=t_experiment(self.session)
        experiment.commit()
        data=[]
        count=0
        for exp in experiment.records:
            count+=1
            for rp in repop.records:
                data+=[DataFile(RepoPath=rp,filename=str(fn)+'.data',exp) for fn in range(5*count)]
        self.records=data
            
###-------------
###  experiments
###-------------

class t_project(TEST):
    def make_all(self):
        people=t_people(self.session,50)
        people.commit()
        #HRM only queries can leverage the power of .filter
        pis=[pi for pi in session.query(Person).filter(Person.role='pi')]
        pi_n=np.random.choice(len(pis),self.num)

        protocol_number=None
        blurb=None

        self.recoreds=[Project(PI=PI[pi_n[n]],protocol_number=protocol_number,blurb=blurb) for n in range(self.num)]
        count=0
        def add_people(self): #has to be called after commit :/
            people=[p for p in self.session.query(Person)]
            people_n=[np.permutation(people)[:np.random.randint(1,20)] for i in range(self.num)]
            for rec,people in zip(self.records,people_n):
                for person in people:
                    rec.people.append(person)


class t_experiment(TEST):
    def make_all(self):
        projects=t_project(self.session,3)
        projects.commit()
        projects.add_people()






def run_tests(session):
    #people=t_people(session,100)
    #people.commit()
    #people.query()

    d=t_data()



def main():
    pass


if __name__=='__main__':
    main()
