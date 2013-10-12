def readProFile(path): #DOESNT WORK RIGHT
    file=open(path,'rb')
    lines=file.readlines()
    file.close()
    #last=lines[-1]
    insbyline=[]
    ps=[]
    for line in lines:
        psplit=[thing for thing in line.split(b'\x00') if thing!=b'']
        ps.extend(psplit)
        ins=[byte for byte in line.split(b'\x00') if byte[:2]==b'IN']
        insbyline.extend(ins)
    #return insbyline
    return ps

def main():
    import os
    path='C:/tom_axon'
    names=[name for name in os.listdir(path) if name[-3:]=='pro']
    fullpaths=[path+'/'+filename for filename in names]
    inCounts=[print(fn,readProFile(fp)) for fp,fn in zip(fullpaths,names)]

if __name__=='__main__':
    main()

