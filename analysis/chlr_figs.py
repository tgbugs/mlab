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
    fig=plt.figure(figsize=(20,20))
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
        #fig=plt.figure(figsize=(5,5))
        plt.plot(mv,pa,'ko')
        plt.plot(xs,pa_fit,'r-',label='best fit')
        plt.title('Cell %s IV plot, g = %1.2f nS, E= %1.2f mV'%(cell,g,Echan))
        plt.xlabel('Holding potential mV')
        plt.ylabel('Photocurrent pA')
        plt.xlim(-89,-11)
        visSpines(fig,target=i)
        centerSpines(fig,target=i,left=0)
        visTicks(plt)

    plt.savefig('cells.png',bbox_inches='tight',pad_inches=.1)

    plt.figure(figsize=(5,5))
    plt.plot(np.ones_like(gs),gs,'ko')
    plt.plot(1,np.mean(gs),'ro',yerr=np.std(gs),label='mean with std')
    plt.ylim((0,max(gs)*1.5))
    plt.title('ChloR conductances, mean= %1.2f'%(np.mean(gs)))
    plt.ylabel('Conductance nS')
    plt.xticks([])
    plt.savefig('cond.png',bbox_inches='tight',pad_inches=.1)

    #plt.show()

if __name__ == '__main__':
    main()

