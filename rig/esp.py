#npcpy newport controller python
#control for newport esp300
#Tom Gillespie
import serial as ser
from threading import RLock
#import rpdb2

"""
Codes used in this file can be found in the Newport ESP300 User's Manual
The most relevant string codes are as follows:
TB Get error message
TP Get position
DH Define home
PA move to absolute position
PR move to relative position
FE Set following error threshold VERY important to prevent lockups
HN new group
HO group motors on
HL move group along line
HX degroup

When dealing with an axis (motor) or groups syntax is as follows
[axis][2 letter code][value]
eg
1TP will send the position of axis 1 back down the serial
1PA0 will move axis 1 two position 0

"""

class espControl:
    """controller class for esp300, attempts to be
    nonblocking on the serial port by only connecting
    when a command is delivered, may change so that
    only one controller is needed and it will handle
    ALL the connections, that might bebetter? but then
    any individual scrips would need to look for an
    existing controller in memory which is frankly,
    too complicated right now, maybe in the future"""
    def __init__(self,port=0,baudrate=19200,bytesize=8,parity='N',stopbits=1,timeout=.03,feLim=5):
        #self._cX, self._cY, self.feLim are READ ONLY, you can write them but you will get bugs
        #control of the serial port
        #all of these can then be referenced under self.esp for the lifetime of the npC object
        self.rlock=RLock()
        try:
            self.esp=ser.Serial(port,baudrate,bytesize,parity,stopbits,timeout) #port is now open!
            self.write('1HX\r\n')
            self.POST()
            self.sim=0
        except IOError:
            print('No serial port found, running in sim mode.')
            self.esp=_fakeEsp(port,baudrate,bytesize,parity,stopbits,timeout)
            self.sim=1
            #FIXME and go into a loop and periodically check to see if we've got it

        self.dirDict={'up':('1',1),'down':('1',-1),'left':('2',1),'right':('2',-1)} #apparently the keyboard has this correct...
        self.axisDict={'x':'2','y':'1'}#1:'y',2:'x', 
        self.toDefault=timeout
        self.grouped=0
        self.target=None

        #control of the newport
        self.feLim=None
        self.setFeLim(feLim)

        self.jhSpd=1 #FIXME check this!
        self.jwSpd=.1
        self.setSpeedDefaults()



        #defs to control motion with the keyboard instead of the joystick, we'll find a key to toggle between them
        self.write('1TJ1;2TJ1')
        self.getPos() #intialize the position FIXME this locks up if the esp is off

    def POST(self):
        self.esp.read(100)
        self.esp.write(b'TP2\r\n')
        out=self.esp.read(100)
        if not len(out):
            raise IOError('esp300 not responding, is it on?')


    def write(self,string,writeback=0): #FIXME may need an rlock here... yep, writeTimeout doesnt work
        out=string+'\r\n'
        try:
            self.rlock.acquire() #MAGIC :D
            self.esp.write(out.encode('ascii'))
            if writeback: #FIXME in theory we could make a list of all the commands that need to be read, but then I would have to parse the string :/ someday, some day
                return self.read()
        except:
            raise IOError('Could not acquire lock to write to serial')
        finally:
            self.rlock.release()

    def read(self):
        try:
            self.rlock.acquire() #aweyiss
            out=b''
            while 1:
                a=self.esp.read(1) 
                if a==b'\n':
                    a=self.esp.read(1)
                if a==b'\r':
                    break
                else:
                    out+=a
        finally:
            self.rlock.release()
        return out

    def readProgram(self):
        out=b''
        self.write("LP")
        hold=self.esp.timeout
        self.esp.timeout=2
        out+=self.esp.read(10000)+b'\n'
        """
        try:
            self.rlock.acquire() #aweyiss
            out=b''
            while 1:
                a=self.esp.read(1) 
                if a==b'E':
                    out+=a
                    a=self.esp.read(1)
                    if a==b'N':
                        out+=a
                        a=self.esp.read(1)
                        if a==b'D':
                            out+=a
                            break
                else:
                    out+=a
        finally:
            self.rlock.release()
        """
        self.esp.timeout=hold
        return out

    def setFeLim(self,feLim):
        """FE prevents problems when going too far"""
        if feLim!=self.feLim: #there has got to be a better way to do this...
            self.feLim=feLim
        self.write('1FE{0};2FE{0}'.format(self.feLim)) #set the following error to feLim
        return 1

    def setSpeedDefaults(self):
        """set speed defaults to override the build in joystick speeds, eventually should rewrite the bloody program"""
        self.write('1JH%f;1JW%f;2JH%f;2JW%f'%(self.jhSpd,self.jwSpd,self.jhSpd,self.jwSpd)) #FIXME check
        return 1

    def getPos(self):
        """TP return the raw x,y position of the actuators
           If you do not need to poll the esp use self._cX or self._cY
           Returns: _cX,_cY as a tuple
        """
        #for the current setup Y=1, X=2  who knows why... just make sure they match yours...
        #also, the X axis values are *-1 because of motor orientation... want to fix??
        x=self.write('2TP',1)  #X
        y=self.write('1TP',1)  #Y
        self._cX,self._cY=float(x),float(y)
        return self._cX,self._cY
    
    def _BgetPos(self):
        """get position and degroup if we are at the target... used when in displacement mode"""
        #do we want to consolidate all this into a single function, I think it's probably worth it since I have all the trys...
        x=self.write('2TP',1)  #X
        y=self.write('1TP',1)  #Y
        self._cX,self._cY=float(x),float(y)
        if (self._cX,self._cY)==self.target:
            self.write('1HX') #degroup oh man this is ugly and not transparent
            self.target=None
        return self._cX,self._cY

    def degroup(self,group=1):
        """degroup a group, probably should fix so I can use with _BgetPos"""
        self.write('1HX')
        return 1

    def BsetPos(self,pos):
        """set the position of the newport to tuple of floats (x,y) NOTE this command is BLOCKING"""
        self.getPos() #need to do this first
        if np.abs(self.cX-pos[0])>self.feLim or np.abs(self.cY-pos[1])>self.feLim:
            print('You are farther away than your feLim! I will fix this later with KP or KD or KI!')
            return 0
        else: #set them to where we are going!
            if self.cX==pos[0] and self.cY==pos[1]:
                print('Yer already thar mate!')
                return 0
            self.target=pos
            self.cX=pos[0]
            self.cY=pos[1]
            #group axes 1&2, velocity to two (mm/s?), acc/dec to 1, motors on, move, wait, degroup
            self.write('1HN1,2;1HV2;1HA1;1HD1;1HO;1HL'+str(self.cY)+','+str(self.cX)) #HW also blocks
            while 1:
                print(self.getPos())
                if (self.cX,self.cY)==self.target: #this SHOULD always trigger...
                    self.write('1HX') #degroup oh man this is ugly and not transparent
                    self.target=None
                    return self.cX,self.cY

    def setPos(self,pos): #this lets the output of getPos feed directly in to set pos FIXME may need BsetPos
        """1HW and/or 1HX block the newport's queue set the position of the newport to floats x,y""" 
        self.getPos() #need to do this first
        if self._cX==pos[0] and self._cY==pos[1]:
            print('Yer already thar mate!')
            return 0
        self._cX=pos[0]
        self._cY=pos[1]
        #group axes 1&2, velocity to two (mm/s?), acc/dec to 1, motors on, move, wait, degroup
        self.write('1HN1,2;1HV2;1HA1;1HD1;1HO;1HL'+str(self._cY)+','+str(self._cX)+';1HW;1HX')
        return 1

    def getErr(self):
        """TB read errors and return the byte array"""
        errstr=self.write('TB',1)
        return errstr

    def move(self,direction,distance): #FIXME follow errors on diagonal movement :/
        """this uses PR, the move relative command"""
        axis=self.dirDict[direction][0]
        self.write(axis+'PR'+str(distance*self.dirDict[direction][1]))#+';'+axis+'WS;'+axis+'TJ3')
        #TJ sets the jog mode, 1 sets it to trapezoidal for keyboard, then 6 sets ot back to vel for joystick

    def discon(self):
        """just incase it is needed during testing makes tying faster"""
        self.esp.close()
        return 1

    def cleanup(self):
        self.write('ST')
        self.esp.close()
        return 1

class _fakeEsp:
    """this creates a fake serial connection to the esp for testing"""
    def __init__(self,port,baudrate,bytesize,parity,stopbits,timeout):
        import numpy as np
        self.port=port
        self.baudrate=baudrate
        self.bytesize=bytesize
        self.parity=parity
        self.stopbits=stopbits
        self.timeout=timeout
        self._x,self._y=np.random.uniform(-10,10,2)
        self.outbuff=['\r']
    def read(self,n):
        out=''
        out+=self.outbuff.pop()
        return out.encode('ascii')
    def write(self,s):
        #print(s)
        if s.split(b';')[0]==b'1HN1,2':
            y,x=s.split(b';')[5].split(b',')
            self._x=float(x)
            self._y=float(y[3:])
        outstr='%.5f\r\n%.5f\r\n'%(self._x,self._y)
        self.outbuff=list(outstr)
        self.outbuff.reverse()
        return 1
    def close(self):
        pass
    def open(self):
        pass

def main():
    esp=espControl()
    import inspect
    from debug import TDB
    tdb=TDB()
    printFD=tdb.printFuncDict
    printFD(inspect.getmembers(esp))
    print(esp.getPos())
    print(esp.getErr())


if __name__=='__main__':
    main()

