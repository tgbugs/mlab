#function to render position data and image data in the same figure
import numpy as np
import pylab as plt


def norm(a,b):
    """ get the distance between two points in r2, could generalize to rn but no """
    return np.linalg.norm(np.array(a)-np.array(b))


def getTransitionMatrix(a,b):
    """ takes two basies (two 2x2 square matricies) and returns the transition matrix
        solves the equation [a11 a21] = m*b for m and [a12 a22] = n*b for n
        note that numpy represents column vectors as lists in pythoneses for purposes of solving

        to use the transition matrix: np.dot(np.array(point),transmatrix)
    """
    n,m=np.linalg.solve(b,a[0]) #first colunn should be [x y] 
    p,q=np.linalg.solve(b,a[1]) #second column

    return np.array([[n,m],[p,q]])



def makeTransformation(harpPOS,imgPOS):
    newHP=np.array(harpPOS)
    newHP=newHP-newHP[1]

    ip_add=np.array(imgPOS[1])
    newIP=np.array(imgPOS)
    newIP=newIP-ip_add

    a=np.array([newHP[0],newHP[2]])
    b=np.array([newIP[0],newIP[2]])
    
    transMat=getTransitionMatrix(a,b)

    def h_to_i(x,y): #FIXME 
        """ takes the 3 points and uses the middle as the new origin, thus, subtract a2 and add b2 """
        x_subtract_ho=x-harpPOS[1][0]
        y_subtract_ho=y-harpPOS[1][1]
        new_points=np.dot(np.array([x_subtract_ho,y_subtract_ho]),transMat)
        out = new_points + np.array(ip_add)[1]
        return out

    return h_to_i


def pi_plot(harpPOS,imgPOS,xs,ys,img):
    """ Plot x vs y on top of the image, minimum three reference points will be needed 
        harp positions should be a tuple of at least 3 x,y pairs
        image positions should be a tuble of x,y pixel locations corrisponding to the x,y pairs

        NOTE: xy pos should genearlly be recorded dorsal to ventral for sake of consistency
    """
    pass

def main():

    harp=(
        (1.231,1.0121),
        (2.3123,3.1021),
        (4.1231,2.313)
    )

    img=[(2*a,2*b) for a,b in harp]
    

    transform=makeTransformation(harp,img)
    

    t1=(0,0)
    t2=(-1.12312,3.12314)
    t3=(-2.32311,1.32134)

    points=t1,t2,t3

    orig=np.array(points)
    trans=np.array([transform(*point) for point in points])

    plt.figure()
    plt.plot(orig[:,0],orig[:,1],'ro')
    plt.plot(trans[:,0],trans[:,1],'ko')
    plt.savefig('/tmp/test.png')


if __name__ == '__main__':
    main()

    
