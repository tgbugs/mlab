#this may eventually be rolled into key.py and a keyControl or something of the sort
#even though keyControl really is term control since I'm using terminal input not key input
class trmControl:
    @class_method
    def getFloatInput(cls):
        while 1:
            try:
                out=float(input('please enter a float')) #FIXME check interactions with key.py this might get rolled in to that
                break
            except:
                print('could not convert value to float, try again!')
        return out
