#Tom Gillespie mouseExpMan, that big old file with classes for all the data I'm going to collect
#lol how this is all actually metadata... >_<
#sqlite3 and/or sqlalchemy backed by sqlite, franky, I'm going to use sqlite one way or another, and I think sqlalchemy is a better fit for my needs
#FIXME:  this is old, should it be here or in the database file to provide a thin layer between the database itself and the functions I want to call from the RIG as opposed to any analysis code?
import numpy as np
from scipy import interpolate as interp
from time import gmtime, strftime
from datetime import datetime,date,time #this may end up being more useful since it auto time deltas

class dataObject:
    def __init__(self):
        self.transactions=list #this should be a list NOT a dict becuase time is ordered
        #we can then use indexing to get only the transactions of a specific target
        #in theory if all targets were classes they could store their own transactions...
    def addData(self,target,value): #i should really just wrap all of this...
        self.transactions.append(datetime.utcnow(),target,value)
        setattr(self,target,value)
        return self
    def listTransactions(self):
        print(self.transactions)
        return self


class timeObj:
    """Base class for things/events that have a start time when the class is initiated and a stop time at some indeterminate point in the future, kept in GMT"""
    def __init__(self):
        self.startGMT=gmtime() #FIXME use datetime objects
        self.stopGMT=None

    def stopTime(self):
        """set stopGMT when finished with the object"""
        self.stopGMT=gmtime()
        return self.stopGMT
        #every transaction should have a time assoicated with it...
        #BUT we dont really want to store transactions


class experiment(timeObj): #this may not exist... 
    """Base experiment class, should work for all ephys experiment types but may need modification of the save method"""
    def __init__(self,npc,expName,expNum): #may also need npCalib, may need to deal with the data path here... it needs to be dealt with explicitly SOMEWHERE
        #FIXME WE DO NOT NEED TO LOAD all the PREVIOUS data into memory when we are COLLECTING
        #at least in theory... even if there are 10k cells
        self.fileMan=fileMan() #FIXME figure out how to do this properly
        #build the file name
        expFileName='{}{}'.format(expName,expNum) #FIXME
        if expFile: #ideally we would always open an existing exp file and add to it
            np.load(expFile) #may need my own load function >_< or use pickle or something

        try:
            #try to find the file based on the expName and expNum
        except IOError:
            super().__init__()
            self.expName=expName
            self.npc=npc #every experiment needs a rig! probably using this to streamline data acquisition HERE rather than in kbControl
            self.expNum=expNum #probably don't actually want to do this, want unique identifiers that know about other experiments

            #do these represent the CURRENT or the PAST, I think they are PAST so why do we need them if we are going to write the data to disk every time we finish with something?
            self.mouseList=[] #ALTERNATELY: DICTIONARIES??!??!?! nah, don't need the keys...
            self.sliceList=[]
            self.cellList=[] #^^^ the above all know about eachother...
            self.stimList=[] #stimList does NOT ?

            self.mouse=None
            self.slc=None #I suppose in some crazy word you could have more than one...
            self.cells=[]

    def addMouse(self,mouseObj):
        try:
            mouseObj.__class__ is mouseObj
        except:
            pass

    def addSlice(self,sliceObj):
        pass

    def addCell(self,cellObj):
        #this is where we want to automatically calculate stimLocations?
        pass

    def addStim(self,stimObj):
        pass

    def addAbf(self,abfObj=None): #this is the data everything else is the metadata
        """This is what we call when we run an experiment, EVERYTHING must be linked to it"""
        abfMan.
        pass

    def saveData(self):
        """call this thing after every addition but ALWAYS keep the previous 2 versions"""
        #for some reason this is raring up to all be saved in a single file...
        pass


class fileMan:
    import pickle
    def __init__(self,datPath,abfPath,self.caliPath):
        self.datPath=datPath #path to the metadata, may change these variables with file xtn
        self.abfPath=abfPath
        self.caliPath=caliPath #may get rid of this and store the calibration data somewhere else
    def saveDat(self):
        #Pickle this shit and don't worry about it!
        #Thus, when it comes time to do data analysis we can get everything into a more reasonable format and convert all the abf files with their attached metadata
        #one big convert instead of continual fiddling, better'd make sure not to tamper with older variables, also danger of data corruption... derp
        #automatically save to two locations! ecc? PAR2 files apparently...
        pass
    def saveCali(self):
        pass
    def formatDat(self):
        """format the data for saving, probably just want to save everything?"""
        pass
    def invFormatDat(self):
        """read the formatted data back in"""
        pass

class abfObj:
    #may want an abfMan instead to manage all the abf files and figure out which will be next...
    #this may simply be overkill since all I really need is a path and a filename...
    #actually, this may be a better object to tie data around becuase it is really what all the data in here is used to interpret
    #other ways of viewing and organizing the data are a... bonus?
    def __init__(self,abfFile):
        self.abfFile=abfFile



class stimObj:
    """Class for stimuation objects""" #FIXME this could apply to light, or to an electrode, fix it
    def __init__(self,pos,intensity):
        self.pos=pos
        self.intensity=intensity #unforunately this will probably have to be entered manually :/
        #we don't need duration because that is stored in the abf files (FOR NOW DAMN IT!)

class rigObj:
    """Class for defining the rig object not needed atm, but could be useful if I get other things working"""
    def __init__(self,hsTup,isVcList):
        if len(isVcList)!=len(hsTup):
            print('hsTup and isVcList must be same length')
            pass
        else:
            self.hsTup=hsTup #a tuple listing the headstages 0,1,2,3
            self.isVCList=isVcList #a list of bools where 1 means that that hs is currently in voltage clamp
            self.hsHasCell=np.zeros_like(hsTup) #assuming that this is started when there are no cells

    def gotCell(self,hs):
        try:
            self.hsHasCell[hs]=1
        except AttributeError:
            print('You don\'t have that many headstages! Spend more money!')
            pass

class litterObj:
    def __init__(self,litName,paired,dob,dam,sire,numMice,dow=None,numSaced=0,cagecard=None):
        self.litName=litName
        self.paired=paired
        self.dob=dob #FTLOG use  ISO8601 WITH NO DASHES
        if dow:
            self.dow=dow #date of weaning use this to pop shit up!
            self.weaned=True
        else:
            self.dow=dob+21
            self.weaned=False
        self.damGeno=damGeno
        self.sireGeno=sireGeno
        self.numMice=numMice
        self.numSaced=numSaced
    def weanLitter(self):
        self.weaned=True
    def sackMouse(self):
        self.numUsed+=1

class mouseObj(timeObj):
    """Base class for all mouse objects"""
    def __init__(self,mouseNum=None,litterObj=None,genotype=None,dod=None,earTag=None,tattoo=None): #FIXME I need so way to assign unique identifirers, mouse nums are no good
        super().__init__()
        self.litter=litterObj #ideally some day this will be integrated with the litter object BUT TODAY IS NOT THAT DAY!
        #do not auto populate, only add mice that have REAL DATA associated with them! UNLESS, I want to look at utilization, in which case seeing how many mice are not used per litter might be useful alternately that can be stored elsewhere
        #in theory I could use the gdata api and store everything in the cloud too...
        self.mouseNum=mouseNum
        self.earTag=earTag
        self.tattoo=tattoo
        self.genotype=genotype #FIXME: may want to create a genotype class since there's so much data on it and it can 
        self.dod=dod #date of death, note that litter contains DOB info so no worries on that account
        #NOTE: unique identifiers for objects? ARGH

    def age(self):
        today=123114 #probably should be a deate FIXME
        return today-self.dob

    def __str__(self):
        return 'Mouse data:\n litter\t\t{}\n mouse\t\t{}\n mouse start\t{}\n mouse stop\t{}\n'\
                .format(self.litter, self.mouseNum, formatTime(self.startGMT), formatTime(self.stopGMT))

class damObj(mouseObj):
    def __init__(self):
        super().__init__()
        
class sireObj(mouseObj):
    def __init__(self):
        super().__init__()

class slcMouseObj(mouseObj):
    """A class for mice that are used for slicing"""
    #how do we deal with conversion of a mouse in a litter to a slice mouse?
    #most logical way is to only convert mice that already exist, so, for example, if I have a mouse that has been genotyped I can create it under and experiment?
    #litter's need not have a mouse for every one of its members, just make sure to increment numSaced whenever one is killed
    #the objective here is to not have to hunt for all the data pertaining to a cell, so a BUNCH of stuff needs to be saved here with the mouse
    #FIXME: init the new slcMosueObj using the old liveMouseObj (or just mouseObj) and del the old one
    def __init__(self):
        super().__init__()
        #these are all potential data points, some of which complicate data collection but could be used for seeing how things are going?
        self.weight=None
        self.uLkx=None
        self.tOut=None
        self.tBOut=None
        self.tDone=None
        self.numSlices=None
        self.epHemi=None

class scepMouseObj(mouseObj):
    """A class for mice that are used for scep"""
    def __init__(self):
        super().__init__()

class sliceObj(mouseObj):
    """Slice object class"""
    def __init__(self,mouseObj,sliceNum,posList,APpos,thickness,timeOut):
        super().__init__(mouseObj.litter,mouseObj.mouseNum) #this duplicates data, oh well
        self.mouse=mouseObj
        self.sliceNum=sliceNum #THIS SHOULD AUTO PROPAGATE FROM SOMEWHERE! ZERO BASED INDEXING
        self.posList=np.array(posList)
        self.APpos=APpos #need to think about how to manage this
        self.thickness=thickness
        self.timeOut=timeOut #the time at which the slice(s) were removed from the 34C bath
        self.splineInterp()

    def __str__(self):
        return '{}\nSlice data:\n slice\t\t{}\n thickness\t{}\n APpos\t\t{}\n slice start\t{}\n slice stop\t{}\n'\
                .format(self.mouse, self.sliceNum, self.thickness, self.APpos, formatTime(self.startGMT), formatTime(self.stopGMT))

    def __plot__(self):
        """use with myplot"""
        return self.posList[:,0],self.posList[:,1],'ko',self.corSurfCoords[0],self.corSurfCoords[1],'k-'

    def splineInterp(self):
        """Interpolate from self.posList the surface of the cortex/slice, want to add the ability to specify things and test"""
        self.tck=interp.splrep(self.posList[:,0],self.posList[:,1]) #tck relevant for computing other stuff on cells
        x=np.linspace(np.min(self.posList[:,0]), np.max(self.posList[:,0]), 1000)
        y=interp.splev(x, self.tck)
        self.corSurfCoords=(x,y)
        return self.corSurfCoords

class cellObj(mouseObj):
    """Class for holding all the data about a cell, this is where we will keep ALL data about origin of cell"""
    #the litter identifier can be used to pull up data on the dam and sire, thus will not store it here
    def __init__(self,sliceObj,cellNum,headstage,depth,pos,cType=None):
        super().__init__(sliceObj.litter,sliceObj.mouseNum) #a bit wierd way to do it, but whatever
        self.slc=sliceObj
        self.cellNum=cellNum
        self.headstage=headstage
        self.depth=depth #note: this is depth IN the slice not anatomical depth in the brain
        self.pos=pos
        self.cType=cType #cell type som,pv,vip,pyr, default to None when I do not know

    def __str__(self):
        return '{}\nCell data:\n cell\t\t{}\n hs\t\t{}\n depth\t\t{}\n pos\t\t{}\n cell start\t{}\n cell stop\t{}\n'\
                .format(self.slc, self.cellNum, self.headstage, self.depth, self.pos, formatTime(self.startGMT), formatTime(self.stopGMT))

    def __plot__(self):
        """use with myplot"""
        return self.pos[0],self.pos[1],'go'

    def calcAntDepth(self):
        """calculate the depth from the cortex surface using the spline representation"""
        diffs=self.slice.corSurfCoords.T-self.pos
        norms=np.apply_along_axis(np.linalg.norm,1,diffs)
        self.antDepth=np.min(norms)


def formatTime(timeObj):
    try:
        return strftime("%Y%m%d%H%M%S",timeObj)
    except:# TypeError:
        return timeObj

def myplot(plotObj):
    """function to make plotting objects use their own plotting setup"""
    from pylab import plot #This is slow OH WELL!
    try:
        plot(*plotObj.__plot__())
    except:# AttributeError:
        print(plotObj.__class__,' doesn\'t know how to plot itself!')


def main():
    from pylab import show
    litter=
    mouse=mouseObj('sctdt1',0)
    slc=sliceObj(mouse,0,[(0,0),(1,1),(2,1.5),(3,1),(4,0)],(-2.6,-2.3),400)
    cell=cellObj(slc,0,0,35,(2,.5))
    cell.stopTime()
    print(cell)
    myplot(cell)
    myplot(slc)
    myplot(mouse)
    show()

if __name__=='__main__':
    main()
