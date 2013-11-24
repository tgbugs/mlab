##The keybinding dictionaries themselves!
#functions can help contain stuff and assemble EVEN LONGER sequences
from debug import TDB
#import rpdb2
#rpdb2.settrace()

tdb=TDB()
printD=tdb.printD
printFuncDict=tdb.printFuncDict
tdbOff=tdb.tdbOff
tdbOff()


def dictInit(inDict,clsDict): #putting this here makes everything funny but auto catches errors
    """the only EXTERNAL dicts that should be put in here are ikCtrlDicts ie in=initilized"""
    def parseValue(counter,instanceOfClass,putativeFunc):
        """Recursive parser for keybinding dictionaries that binds the named function to the method it initilizes to?, only works because I'm using classes"""
        #FIXME might be able to simplify this by simply referring to functions? and getting rid of the classes? eh, but inheritance man...
        if counter > 100: #this should be longer than the longest program list you try to pass in
            return None
        try:
            #'function name'
            return instanceOfClass.__getattribute__(putativeFunc)
        except (TypeError,AttributeError) as e:
            #printD(putativeFunc,'wasnt a function')
            if type(putativeFunc)==tuple: #is it a func tupel?
                try:
                    #'function',args
                    function=instanceOfClass.__getattribute__(putativeFunc[0])
                    return argsCaller(function,putativeFunc[1])
                except (TypeError,AttributeError) as e:
                    printD(putativeFunc,'func arg tuple not inited')
                    pass
            elif type(putativeFunc)==list: #is it a list?
                funcList=[]
                for item in putativeFunc:
                    try:
                        funcList.append(parseValue(counter+1,instanceOfClass,item)) #RECURSE AWEYISS
                        printD(item,'successfully appended to function list!')
                    except (TypeError,AttributeError) as e:
                        printD("dictInit: Step '%s' in your list is wrong")
                        return None
                return listCaller(funcList)
            elif type(putativeFunc)==dict: #NOTE this comes LAST because otheriwse it would catch all the key dicts and try to call them (i think?)
                try:
                    return dictCaller(dictInit(inDict, putativeFunc)[1]) #we'll see if this works
                except:
                    raise
                    printD("something may not have been parsed earlier and something leaked through")
            else:
                printD('parseValues: something is wrong!',putativeFunc)
                return None

    def cleanDict(inDict,clsDict):
        """remove any calls to modules that aren't loaded"""
        #try:
            #mode=clsDict['mode'] #THIS IS THE NEW DEFAULT!
        #FOR MOST CASES inDict is ikCtrlDict
        printD('inDict=',inDict)
        delKeys=[]
        newDict={}
        for className in clsDict.keys():
            try:
                #function=inDict[className]
                #inDict[className]
                inDict[className]
                newDict[className]=clsDict[className] #you silly derp
            except:
                pass
                #printD(newDict.pop(className)) #don't need this apparentlyt  :)
                #delKeys.append(className)

        #for className in delKeys:
            #clsDict.pop(className) #THIS IS SILLY! no dynamic updating of keybinds and modules, oh well!
        #printD('new dict',newDict)
        return newDict
        #printD('initDict: at end of try for rig mode=',mode)
        #except:
            #printD('dictInit: could not set mode, did you include it in your dict?')
            #printD('no mode detected, assuming you want to convert a mixed class sequence')



    #printFuncDict(clsDict.items())
    def makeKeyDict(ikCtrlDict,clsDict):
        initedDict={}
        try:
            initedDict['mode']=clsDict['mode'] #see if the dict we are working on has a mode
        except: #this will fail when dictInit is passed a dict that isn't actually a top level mode dict
            pass
        newDict=cleanDict(ikCtrlDict,clsDict) #in here it's nondestructive!
        try:
            for className,keyDict in newDict.items():
                ikCtrl=ikCtrlDict[className]
                for key,funcStr in keyDict.items():
                    #if key=='c':
                    #printD('initDict: function to call is:',ikCtrl,funcStr,'key is:',key)
                    if key=='#!':                        #SPECIAL KEYCODE TO IMMEDIATELY EXECUTE so we can 
                    #FIXME
                    #use of '#!' expects a tuple ('funcName',args)
                        ikCtrl.__getattribute__(funcStr[0])(*funcStr[1]) #pass things in from the config files 
                    else:
                        initedDict[key]=parseValue(0,ikCtrl,funcStr)     #without having to know things in advance
                #printD('hardcoded excape code follows')
                try:
                    if initedDict['mode']=='rig':
                        initedDict['esc']=lambda:0 #hardcoded escape
                    elif initedDict['mode']: #anything with a mode gets this
                        initedDict['esc']=argsCaller(ikCtrl.setMode,'rig')
                except:
                    try:
                        if initedDict['mode']:
                            #initedDict['esc']=argsCaller(ikCtrl.setMode,'rig')
                            initedDict['esc']=argsCaller(ikCtrl.setMode,'rig')
                    except:
                        printD("no mode set, cannot be put in mode dict, so no esc set")
        except:
            printD("### no modules loaded, returning mode=None ###")
            raise
        printFuncDict(initedDict)
        try:
            helpDict={clsDict['mode']:newDict}
        except:
            helpDict={}
        return helpDict, initedDict

    helpDict,initedDict=makeKeyDict(inDict,clsDict)
    return helpDict,initedDict

def makeModeDict(ikCtrlDict,*clsDicts):
    modeDict={}
    if len(clsDicts)==1:
        helpDict,keyActDict=dictInit(ikCtrlDict,clsDicts[0])
        modeDict[keyActDict['mode']]=keyActDict
        return helpDict, modeDict

    helpDict={}
    for clsDict in clsDicts:
        newHD, keyActDict=dictInit(ikCtrlDict,clsDict)
        helpDict.update(newHD)
        modeDict[keyActDict['mode']]=keyActDict
    return helpDict, modeDict

#
#functions to call functions awe yeah
def dictCaller(dict):
    #if [key for key in dict.keys() if type(key)!=int]: #this will do the whole list instead of stopping...
    try:
        ordKeys=list(dict.keys())
        ordKeys.sort()
        return lambda :[dict[key]() for key in ordKeys]
    except TypeError:
        return lambda :[item() for item in dict.items()] #don't need the dict because already in local()

#argsCaller=lambda func,args:(lambda :func(args)) #awe yeah magic! FIXME?
def argsCaller(func,args): return lambda:func(args)

#listCaller=lambda list:(lambda:[func() for func in list]) #this will just fail on me since they dont have try/except
def listCaller(list): return lambda:[func() for func in list] #this will just fail on me since they dont have try/except
