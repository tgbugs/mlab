import numpy as np
from scipy.interpolate import UnivariateSpline, SmoothBivariateSpline, InterpolatedUnivariateSpline

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
    pts=np.array(points) #turns a tuple of tuples into a column vector
    xs=pts[:,0]
    ys=pts[:,1]
    #print(xs)
    #print(ys)
    #spline=InterpolatedUnivariateSpline(xs,ys)
    spline=UnivariateSpline(xs,ys)
    #spline=SmoothBivariateSpline(xs,ys)
    integral=[]
    space=np.linspace(min(xs),max(xs),1000)
    for n in space:
        out=spline.integral(min(xs),n)
        #print(out)
        integral.append(out)
    #print(integral)
    return spline,space,integral,xs,ys


def rand_x2(min_,max_,num):
    base=np.random.uniform(min_,max_,num)
    #print(base)
    noise=lambda a:np.random.randint(-np.abs(a),np.abs(a))*10
    #return [(a,a**2) for a in base]
    return [(a,np.cos(a/4)) for a in base]

def main():
    import pylab as plt

    plt.figure()
    for i in range(9):
        points=rand_x2(-20,20,10)
        spline,space,integral,xs,ys=get_spline(points)
        base=np.linspace(np.min(xs),np.max(xs),10000)
        #print(base)
        #spline(base)
        plt.subplot(3,3,i+1)
        plt.plot(base,spline(base),'b-')
        plt.plot(xs,ys,'ko')
        #plt.plot(space,integral)


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
