import pylab as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes
from neo.io import AxonIO as aio
from tgplot import centerSpines,visTicks,visSpines,format_axes
from IPython import embed

def align_plot(file,mean_start,mean_stop):
    b=aio(file)
    d=b.read_block()
    #embed()
    traces=[s.analogsignals[0] for s in d.segments]
    led=d.segments[0].analogsignals[1].base
    led_times=d.segments[0].analogsignals[1].times.base[led<3]
    means=[np.mean(t.base[mean_start:mean_stop]) for t in traces]
    aligned=[t.base-mean for t,mean in zip(traces,means)]
    times=traces[0].times.base
    fig,ax=plt.subplots(1,figsize=(10,10))
    offset=14.97
    for i in range(len(aligned)):
        if i not in [3,5]:
            plt.plot(times-offset,aligned[i],'k-')
        elif i == 3:
            plt.plot(times-offset,aligned[i],'g-')
        elif i == 5:
            plt.plot(times-offset,aligned[i],'r-')

    plt.xlim(-1,10)
    plt.ylim(-1500,1500)
    #plt.axis([])
    plt.ylabel('Photocurrent (pA)')
    plt.xlabel('Time from LED onset (s)')
    plt.title('Current vs time for 10mV steps from -80mV to +10mV, Cs internal')
    #plt.plot([15,15.050],[1350,1350],'b-',linewidth=3,label='470nm LED ON')
    plt.plot(led_times-offset,np.ones_like(led_times)*1350,'b-',linewidth=3,label='470nm LED ON')
    plt.legend(loc=4)
    #format_axes(ax)
    plt.savefig('traces.png',bbox_inches='tight',pad_inches=.1)

    #fig=plt.figure(figsize=(4,4))
    #plt.axes([20,24,500,1400])
    offset=14.97*1000
    axins=inset_axes(ax,width=2.5,height=2.5,loc=1)
    axins.spines['right'].set_visible(0)
    axins.spines['top'].set_visible(0)
    plt.plot(times*1000-offset,aligned[3],'g-')
    plt.plot(times*1000-offset,aligned[5],'r-')
    plt.plot(led_times*1000-offset,np.ones_like(led_times)*305,'b-',linewidth=3,label='470nm LED ON')
    plt.ylim(-300,310)
    plt.xlim(14.96*1000-offset,15.01*1000-offset)
    #plt.xticks([])
    #plt.yticks([])
    visTicks(plt)
    plt.xlabel('ms')
    plt.ylabel('pA')
    #plt.setp(a,xticks=[],yticks=[])
    plt.savefig('traces_inset.png',bbox_inches='tight',pad_inches=.1)

    fig=plt.figure(figsize=(4,4))
    plt.plot(times*1000,aligned[5],'r-')
    plt.xlim(14.96*1000,15.01*1000)
    plt.ylim(-100,400)
    plt.plot(led_times*1000,np.ones_like(led_times)*350,'b-',linewidth=3,label='470nm LED ON')
    visSpines(fig)
    visTicks(plt)
    plt.savefig('traces_inset1.png',bbox_inches='tight',pad_inches=.1)

    fig=plt.figure(figsize=(4,4))
    plt.plot(times*1000,aligned[3],'g-')
    plt.xlim(14.96*1000,15.01*1000)
    plt.ylim(-400,100)
    plt.plot(led_times*1000,np.ones_like(led_times)*50,'b-',linewidth=3,label='470nm LED ON')
    visSpines(fig)
    visTicks(plt)
    plt.savefig('traces_inset2.png',bbox_inches='tight',pad_inches=.1)


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
        plt.title('Cell %s IV plot, g = %1.2f nS, E= %1.2f mV, GABA reversal = -75mV'%(cell,g,Echan))
        plt.ylabel('Photocurrent (pA)')
        plt.xlim(-89,-11)
        visSpines(fig,target=i)
        centerSpines(fig,target=i,left=0)
        visTicks(plt)
        plt.xlabel('Holding potential (mV)')

    plt.savefig('cells.png',bbox_inches='tight',pad_inches=.1)

    mx_gs=[
        15.41996,
        12.04144,
        10.76820,
        4.10410,
        17.18420,
        28.03825,
        16.49540,
    ]
    gs.extend(mx_gs)

    plt.figure(figsize=(5,5))
    plt.plot(np.ones_like(gs),gs,'ko',mfc='none')
    plt.errorbar(1,np.mean(gs),fmt='r-',yerr=np.std(gs),capsize=4)
    plt.plot([.9,1.1],[np.mean(gs)]*2,'r-',label='mean, std')
    plt.xlim(0,2)
    plt.ylim((0,max(gs)*1.25))
    plt.title('ChloR conductances, n = %s, $\mu$ = %1.2f'%(len(gs),np.mean(gs)))

    plt.ylabel('Conductance nS')
    plt.legend()
    plt.xticks([])
    plt.savefig('cond.png',bbox_inches='tight',pad_inches=.1)

    #align_plot('C:/users/root/Dropbox/mlab/chlr project/20140305_0011 Cs.abf',139000,149000)
    align_plot('/home/tom/Dropbox/mlab/chlr project/20140305_0011 Cs.abf',139000,149000)

    #plt.show()

    plt.figure(figsize=(5,5))
    ledv=[
        0.047619047619048,
        0.166666666666667,
        0.285714285714286,
        0.404761904761905,
        0.523809523809524,
        0.642857142857143,
        0.761904761904762,
        0.880952380952381,
        1,
    ]
    normpa1=np.array([
    0.612544939541774,
    0.878575743633962,
    0.840518585319828,
    0.931070226099345,
    0.934237151915221,
    1,
    0.939360688229655,
    0.954353272178835,
    0.999640585559338,
    ])
    normpa2=np.array([
0.744838851670776,
0.879814959037862,
0.712928057576996,
0.618422919060498,
0.881860482768391,
0.879689246793273,
0.887210455967224,
0.978096760766479,
1,
    ])
    normpa3=np.array([
0.678290253302955,
0.894949115528883,
0.97827917992336,
0.889747787495332,
1,
0.899894042956028,
0.916889714446732,
0.964763336064285,
0.99981703592407,
    ])
    stack=np.vstack([normpa1,normpa2])#,normpa3])
    print(stack)
    npam=np.mean(stack,axis=0)
    npas=np.std(stack,axis=0)
    #plt.errorbar(ledv,npam,yerr=npas,fmt='ko')

    plt.plot(ledv,normpa1,'ko')
    #plt.plot(ledv,normpa2,'go')
    #plt.plot(ledv,normpa3,'bo')
    plt.xlim((0,1.05))
    plt.ylim((.5,1.05))
    plt.title('Norm. photocurrent vs LED intensity')
    plt.xlabel('Norm. LED intensity')
    plt.ylabel('Norm. Photocurrent')
    plt.savefig('intensity.png')
    

if __name__ == '__main__':
    main()

