#all string/float/int input goes here, all single key hit stuff is in trmFuncs

class trmControl:
    """Controller for text entry, uses input()"""

    def __getChars__(self): #use this to make a refactor easier
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
                print('Could not convert value to float, try again!')

    def getInt(self):
        print('please enter an integer')
        while 1:
            string=self.__getChars__()
            try:
                out=int(string)
                return out
            except ValueError as e:
                print(e,'Try again!')
                #print('could not convert value to int, try again!')
