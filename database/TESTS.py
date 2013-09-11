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
        ntids=np.random.randint(0,999999,num)

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
        print(self.session.query(People))

class t_data(TEST):
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
    people=t_people(session,1000)
    people.commit()

def main():
    pt=t_people(None,100)

if __name__=='__main__':
    main()
