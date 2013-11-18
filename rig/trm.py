#this may eventually be rolled into key.py and a keyControl or something of the sort
#even though keyControl really is term control since I'm using terminal input not key input
#dataio from the keyboard
#FIXME this is actually an inpFuncs in the rig world even though it is a dataio in the database world
from sys import stdout
class _trmControl: #FIXME input is so much easier to use...
    #note that all of these are SUPPOSED to block
    def __init__(self,modestate):
        self.charBuffer=modestate.charBuffer
        self.keyHandler=modestate.keyHandler

    def __getChars__(self):
        chars=[]
        while 1:
            self.keyHandler(1)
            key=self.charBuffer.get()
            if key == '\r': #FIXME make sure this is portable
                break
            elif key == '\x08':
                chars=chars[:-1]
                stdout.flush()
                stdout.write('\r'+''.join(chars)+' ')
            else:
                chars.append(key)
                stdout.flush()
                stdout.write('\r'+''.join(chars))
        return ''.join(chars)

    def getKbdHit(self):
        self.keyHandler(1)
        self.charBuffer.get()
        return True

    def getString(self):
        return self.__getChars__()

    def getBool(self):
        true_key=' '
        self.keyHandler(1) #requesting key passthrough
        return self.charBuffer.get() == true_key

    def getFloat(self):
        while 1:
            string=self.__getChars__()
            try:
                out=float(string)
                return out
            except:
                print('could not convert value to float, try again!')

    def getInt(self):
        while 1:
            string=self.__getChars__()
            try:
                out=int(string)
                return out
            except ValueError as e:
                print(e,'try again!')
                #print('could not convert value to int, try again!')

class trmControl:
    """Controller for text entry, uses input()"""
    #note that all of these are SUPPOSED to block
    def __init__(self):
        pass

    def __getChars__(self):
        return input()

    def getString(self):
        print('Please enter a string')
        return self.__getChars__()

    def getFloat(self):
        print('Please enter a floating point value.')
        while 1:
            string=self.__getChars__()
            try:
                out=float(string)
                return out
            except:
                print('could not convert value to float, try again!')

    def getInt(self):
        print('please enter an integer')
        while 1:
            string=self.__getChars__()
            try:
                out=int(string)
                return out
            except ValueError as e:
                print(e,'try again!')
                #print('could not convert value to int, try again!')
