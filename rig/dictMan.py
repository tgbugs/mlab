##The keybinding dictionaries themselves!
#functions can help contain stuff and assemble EVEN LONGER sequences
from debug import TDB
#import rpdb2
#rpdb2.settrace()

tdb=TDB()
printD=tdb.printD
printFuncDict=tdb.printFuncDict
tdb.off()

#XXX WARNING XXX Spagetti code be here! some day we will refactor

def dictInit(inDict,clsDict,kr_dict): #putting this here makes everything funny but auto catches errors
    """the only EXTERNAL dicts that should be put in here are ikCtrlDicts ie in=initilized"""
    def parseValue(counter,instanceOfClass,putativeFunc,keyRequesters,kr_dict):
        """Recursive parser for keybinding dictionaries that binds the named function to the method it initilizes to?, only works because I'm using classes"""
        #FIXME might be able to simplify this by simply referring to functions? and getting rid of the classes? eh, but inheritance man...
        if counter > 100: #this should be longer than the longest program list you try to pass in
            return None,None
        key_request_count=0
        try:
            #'function name'
            if putativeFunc in keyRequesters: #see if this is a key requester
                key_request_count+=1
                #TODO
            return instanceOfClass.__getattribute__(putativeFunc), key_request_count

        except (TypeError,AttributeError) as e:
            #printD(putativeFunc,'wasnt a function')
            if type(putativeFunc)==tuple: #is it a func tupel?
                try:
                    #'function',args
                    function=instanceOfClass.__getattribute__(putativeFunc[0])
                    if putativeFunc[0] in keyRequesters: #check and wrap if kr
                        key_request_count+=1
                    return argsCaller(function,putativeFunc[1]), key_request_count
                except (TypeError,AttributeError) as e:
                    printD(putativeFunc,'func arg tuple not inited')
                    pass
            elif type(putativeFunc)==list: #is it a list?
                funcList=[]
                for item in putativeFunc:
                    try:

                        function,kr_count=parseValue(counter+1,instanceOfClass,item,keyRequesters,kr_dict) #RECURSE AWEYISS
                        funcList.append(function)
                        key_request_count+=kr_count
                        printD(item,'successfully appended to function list!')
                    except (TypeError,AttributeError) as e:
                        printD("dictInit: Step '%s' in your list is wrong")
                        return None,key_request_count
                return listCaller(funcList),key_request_count
            elif type(putativeFunc)==dict: #NOTE this comes LAST because otheriwse it would catch all the key dicts and try to call them (i think?)
                try:
                    help,idict,krc=dictInit(inDict, putativeFunc, kr_dict)

                    return dictCaller(idict),key_request_count+sum(krc.values()) #we'll see if this works FIXME
                except:
                    raise
                    printD("something may not have been parsed earlier and something leaked through")
            else:
                printD('parseValues: something is wrong!',putativeFunc)
                return None,key_request_count

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
    def makeKeyDict(ikFuncDict,clsDict,kr_dict):
        initedDict={}
        keyRequestDict={}
        try:
            initedDict['mode']=clsDict['mode'] #see if the dict we are working on has a mode
        except: #this will fail when dictInit is passed a dict that isn't actually a top level mode dict
            pass
        newDict=cleanDict(ikFuncDict,clsDict) #in here it's nondestructive!
        try:
            for className,keyDict in newDict.items():
                ikFunc=ikFuncDict[className]
                keyRequesters=kr_dict.get(className,tuple()) #XXX get the key requesters in this class
                for key,funcStr in keyDict.items():
                    #if key=='c':
                    #printD('initDict: function to call is:',ikCtrl,funcStr,'key is:',key)
                    if key=='#!':                        #SPECIAL KEYCODE TO IMMEDIATELY EXECUTE so we can 
                    #FIXME
                    #use of '#!' expects a tuple ('funcName',args)
                        name,args=funcStr
                        functionToCall=getattr(ikFunc,name)
                        functionToCall(*args)
                        #ikFunc.__getattribute__(funcStr[0])(*funcStr[1]) #pass things in from the config files 
                    else:
                        initedDict[key],keyRequestDict[key]=parseValue(0,ikFunc,funcStr,keyRequesters,kr_dict) #without having to know things in advance FIXME this is a god damned maze

                #printD('hardcoded excape code follows')
                try:
                    if initedDict['mode']=='rig':
                        initedDict['esc']=lambda:0 #hardcoded escape
                    elif initedDict['mode']: #anything with a mode gets this
                        initedDict['esc']=argsCaller(ikFunc.setMode,'rig')
                except:
                    try:
                        if initedDict['mode']:
                            #initedDict['esc']=argsCaller(ikCtrl.setMode,'rig')
                            initedDict['esc']=argsCaller(ikFunc.setMode,'rig')
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
        return helpDict, initedDict, keyRequestDict

    helpDict,initedDict,keyRequestDict=makeKeyDict(inDict,clsDict,kr_dict)
    return helpDict,initedDict,keyRequestDict

def makeModeDict(ikFuncDict,kr_dict,*clsDicts):
    modeDict={}
    modeKRDict={}
    if len(clsDicts)==1:
        helpDict,keyActDict,keyRequestDict=dictInit(ikFuncDict,clsDicts[0],kr_dict)
        modeDict[keyActDict['mode']]=keyActDict
        modeKRDict[keyActDict['mode']]=keyRequestDict
        return helpDict, modeDict, modeKRDict

    helpDict={}
    for clsDict in clsDicts:
        newHD, keyActDict, keyRequestDict=dictInit(ikFuncDict,clsDict,kr_dict)
        helpDict.update(newHD)
        modeDict[keyActDict['mode']]=keyActDict
        modeKRDict[keyActDict['mode']]=keyRequestDict
    return helpDict, modeDict, modeKRDict

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
