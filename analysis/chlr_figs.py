import pylab as plt
import numpy as np
from tgplot import centerSpines,visTicks,visSpines


def get_mv_pa(cell,data):
    cell_data=data[data[:,1]==cell]
    mv=cell_data[:,4]
    pa=cell_data[:,5]
    return mv,pa

def main():
    data=np.genfromtxt('chlr_compiled.csv',delimiter=',')
    cells=1,8,10,14
    gs=[]
    es=[]
    plt.figure(figsize=(20,20))
    for i in range(len(cells)):
        cell=cells[i]
        mv,pa=get_mv_pa(cell,data)
        #p,res,cov,s=np.polyfit(mv,pa,1)
        p=np.polyfit(mv,pa,1)
        g=p[0]
        b=p[1]
        Echan=-b/g
        gs.append(g)
        es.append(Echan)
        xs=np.linspace(min(mv),max(mv),10)
        pa_fit=g*xs+b

        plt.subplot(2,2,i+1)
        plt.plot(mv,pa,'ko')
        plt.plot(xs,pa_fit,'r-')
        plt.title('Cell %s I/V plot g = %s nS, E= %s mV'%(cell,g,Echan))
        plt.xlabel('Holding potential mV')
        plt.ylabel('Photocurrent pA')

    plt.figure(figsize=(5,5))
    plt.plot(np.ones_like(gs),gs,'ko')
    plt.ylim((0,max(gs)*1.5))
    plt.title('Conductances')

    plt.show()

if __name__ == '__main__':
    main()

