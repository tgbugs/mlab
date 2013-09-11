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
    def __init__(self,session,num):
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

        self.people=[Person(PrefixName=pfns[i],
                            FirstName=fns[i],
                            MiddleName=mns[i],
                            LastName=lns[i],
                            Gender=genders[i],
                            Role=roles[i],
                            neurotree_id=ntids[i],
                            Birthdate=birthdates[i]) for i in range(num)]
        #print(self.people)

    def commit(self):
        self.session.add_all(self.people)
        self.session.commit()

    def query(self):
        #print([p.Gender for p in self.session.query(Person)])
        print([p for p in self.session.query(Person)])

class t_data(TEST):
    def get_repopath(self):
        self.session.query(RepoPath)
    def make_datafile(self):
    pass


class t_experiment(TEST):
    def add_projects(self):
        PI,People,protocol_number=None
        pass
    def add_experiments(self):
        pass
    def add_cells(self):
        pass



def run_tests(session):
    people=t_people(session,100)
    people.commit()
    people.query()

def main():
    pass


if __name__=='__main__':
    main()
