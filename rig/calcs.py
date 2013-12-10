import numpy as np
from scipy.interpolate import UnivariateSpline, SmoothBivariateSpline, InterpolatedUnivariateSpline
from scipy import integrate


def intersperse(iterable,delim):
    it = iter(iterable)
    yield next(it) #this prevents the delimiter from showing up first
    for x in it:
        yield delim
        yield x

def vector_points(origin_x,origin_y,vec_x,vec_y,number=10,spacing=.01):
    """ returns a list of points spaced along the line between origin and vector"""
    norm=spacing
    dx=(vec_x-origin_x)
    dy=(vec_y-origin_y)
    sx=np.sign(dx)
    theta=np.arctan2(dy,dx)
    #theta=np.arctan(dy/dx)
    def imstupid(sx):
        """ I CANNOT MATH HALP """
        if sx < 0: #if the x coord is negative arctan will be wonky
            return np.pi
        else:
            return 0
    cost=np.cos(theta)#+imstupid(sx))
    sint=np.sin(theta)#+imstupid(sx))
    #x coord = norm * cos(o)
    #y coord = norm * sin(o)
    points=[(n*norm*cost+origin_x,n*norm*sint+origin_y) for n in range(number)]
    return points

def random_vector_points(origin_x,origin_y,vec_x,vec_y,number=10,spacing=.01):
    out=vector_points(origin_x,origin_y,vec_x,vec_y,number,spacing)
    np.random.shuffle(out)
    return out

def random_vector_ret_start(origin_x,origin_y,vec_x,vec_y,number=10,spacing=.01):
    out=vector_points(origin_x,origin_y,vec_x,vec_y,number,spacing)
    np.random.shuffle(out)
    out=[i for i in intersperse(out,(origin_x,origin_y))] #FIXME
    return out

def get_spline(points):
    """ min 5 points """
    #TODO may need a way to flip xy
    pts=np.array(points) #turns a tuple of tuples into a column vector
    xs=pts[:,0]
    ys=pts[:,1]
    #print(xs)
    #print(ys)
    #spline=InterpolatedUnivariateSpline(xs,ys)
    spline=UnivariateSpline(xs,ys)
    #spline=SmoothBivariateSpline(xs,ys)
    integral=[]
    space=np.linspace(min(xs),max(xs),1000) #XXX NOTE XXX
    #for n in space:
        #start=np.random.randint(0,1000)
        #out=spline.integral(start,n)
        #out=spline.integral(min(xs),n)
        #out=spline.integral(0,1)
        #print(out)
        #integral.append(out)
    #print(integral)
    return spline,space,integral,xs,ys


def rand_x2(min_,max_,num):
    base=np.random.uniform(min_,max_,num)
    #print(base)
    noise=lambda a:np.random.randint(-np.abs(a),np.abs(a))*10
    return [(1,1)]+[(a,a**2) for a in base]
    #return [(a,np.cos(a/4)) for a in base]

def arc_lengths(spline,space,start):
    dspline=spline.derivative()
    def abs_ds(t):
        #return (1+dspline(t)**2)**.5 #norm in higher dimensions
        return np.abs(dspline(t))
    arc_length=[]
    for b in space:
        s,base=integrate.quad(abs_ds,start,b)
        arc_length.append(abs(s))
    return np.array(arc_length)

def get_xys_at_dist(spline,base,start_x,distances): #FIXME which way to mount the slice?
    arcs=arc_lengths(spline,base,start_x)
    #print(arcs)
    points=[]
    for distance in distances:
        span=np.argwhere(arcs <= distance)
        #print(span)
        left=span[0] #FIXME
        right=span[-1] #FIXME
        x1=base[left][0]
        y1=spline(base)[left][0]
        points.append((x1,y1))
        x2=base[right][0]
        y2=spline(base)[right][0]
        points.append((x2,y2))
    return points

def get_points_from_spline(points,number=10,spacing=.05):
    """ note that total points is number*2 """
    spline,base,inte,xs,ys=get_spline(points)
    dists=[spacing*i for i in range(1,number)]
    start_x=points[0][0]
    out=[(start_x,spline(start_x))]
    out+=get_xys_at_dist(spline,base,start_x,dists)
    return out



def main():
    import pylab as plt
    from ipython import embed

    plt.figure()
    for i in range(9):
        points=rand_x2(-20,20,10)
        spline,space,integral,xs,ys=get_spline(points)
        base=np.linspace(np.min(xs),np.max(xs),10000)
        #print(base)
        #spline(base)
        #left,right=get_xys_at_dist(spline,space,space[500],5)
        dists=get_points_from_spline(points,number=10,spacing=5)
        arcs=arc_lengths(spline,space,points[0][0])
        plt.subplot(3,3,i+1)
        for dist in dists:
            plt.plot(dist[0],dist[1],'go')
        #plt.plot(left[0],left[1],'go')
        #plt.plot(right[0],right[1],'go')
        plt.plot(space,arcs,'r-')
        plt.plot(base,spline(base),'b-')
        #plt.plot(xs,ys,'ko')
        #plt.show()
        #plt.plot(space,integral)

    #embed()

    def test_vec():
        plt.figure()
        for i in range(25):
            points=np.random.uniform(-10,10,10)
            plist=vector_points(*points,number=10,spacing=1)
            plist=np.array(plist)
            plt.subplot(5,5,i+1)
            plt.plot(points[0],points[1],'ko') #ls='ko'
            plt.plot(points[2],points[3],'bo')
            plt.plot(points[0::2],points[1::2],'g-')
            plt.plot(plist[:,0],plist[:,1],'ro')

    plt.show()


if __name__ == '__main__':
    main()
