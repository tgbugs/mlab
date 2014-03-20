#file for standard methods to be used throughout the database to maintain consistency of data
#ALL functions used in __init__ to write data and their pairs for reading data from queries should go here

#input sanitization goes here
from urllib import parse
from os import listdir
import socket

from datetime import datetime,timedelta #ALL TIMES ARE UTC WITH tzinfo=None, CONVERT LATER

import requests as r #FIXME :(

###---------------
###  File handling
###---------------

def get_local_abf_path(hostname,osname,program=None): #FIXME make this not hardcoded also derp why does this have to exist
    nt_paths={
            'HILL_RIG':'D:/tom_data/clampex/',
            'andromeda':'C:/tom_data/clampex/', #derp empty and fake
    }

    posix_paths={
            'athena':'/home/tom/Dropbox/mlab/data', #FIXME this is clearly incorrect
    }

    os_hostname_abf_path={ 'nt':nt_paths, 'posix':posix_paths, }

    fpath=os_hostname_abf_path[osname][hostname]
    return fpath

def Get_newest_file(_path,extension): #FIXME TODO: I think the easiest way to do this is just to have watched folders with filetypes to watch, and they can be recursive, and then we can just call a 'go check for changes' function
    print(_path,extension)
    files=listdir(_path)
    print(files)
    ext_files=[file for file in files if file[-3:]==extension]
    print(ext_files)
    ext_files.sort() #FIXME make sure the filenames order correctly
    out=ext_files[-1] #get the last/newest file
    return out


###--------------
###  URL handling
###--------------

class URL_STAND:
    """Standards for url sting termination and initiation for consistently"""
    #TODO should handle matching local files to the computer they actually came from relative to the db
    @staticmethod
    def urlClean(url):
        if url is None:
            return None
        else:
            return url.rstrip('/')+'/' #FIXME make it so this strips to last/
    
    @staticmethod
    def urlHostPath(url):
        p=parse.urlparse(url)
        host=p.netloc
        path=p.path
        if path[2] == ':':
            path = path[1:] #FIXME stupid windows paths
        return host,path

    @staticmethod
    def ping(full_url):
        #FIXME rework this to go through a full url scheme handler that can be extended with resources
        #see if one exists, it should...
        parsed=parse.urlparse(full_url)
        if parsed.scheme == 'file':
            hostname=socket.gethostname()
            host=parsed.netloc
            if host != hostname:
                raise FileNotFoundError('The file is on %s! You are on %s'%host,name) #FIXME this => wierd error handling
                #this is just ping, we are not going to worry about finding the correct file location here
                #TODO this needs to try to access the netloc since this is PING, for actual retrieval we can choose the local repo ourselves
                #printD('The file is on %s! You are on %s. Will try with hst==localhost'%host,name) #FIXME 
            path=parsed.path
            if path[2]==(':'): #FIXME this is not actually valid... windows :/
                path=path[1:]
            try:
                listdir(path)
                return path
            except:
                raise FileNotFoundError('Local path \'%s\' does not exist!'%path) #FIXME this => wierd error handling
        else: #TODO requests does not actually handle anything besides http/s :/
            try:
                if r.head(full_url).status_code == 404: #also data computer on the internet???
                    raise FileNotFoundError('Remote url \'%s\' is not OK!'%full_url) #FIXME this => wierd error handling
                else:
                    return full_url
            except: #connections error TODO FIXME
                #raise FileNotFoundError('Remote url \'%s\' is not OK!'%full_url) #FIXME this => wierd error handling
                pass

    @staticmethod
    def getCreationDateTime(full_url):
        parsed=parse.urlparse(full_url)
        if parsed.scheme is 'file':
            path=parsed.path
            if path[2]==(':'): #FIXME this is not actually valid... windows :/
                path=path[1:]
            try:
                datetime.fromtimestamp(getctime(path))
            except:
                raise FileNotFoundError('Local path does not exist!') #FIXME this => wierd error handling
        else:
            return datetime.now() #FIXME ideally we want to get the remote modified date
###---------------------------------------------------------------
###  Datetime and timedelta functions to be reused for consistency
###---------------------------------------------------------------

def frmtDT(dateTime,formatString='%Y/%m/%d %H:%M:%S',localtime=False):
    if localtime:
        return 'the dt run through some function that converts UTC to whatever the current local timezone is polled from the system' #FIXME
    return datetime.strftime(dateTime,formatString)

def timeDeltaIO(tdORfloat): #FIXME postgres as INTERVAL but it has quirks
    try:
        return tdORfloat.total_seconds()
    except:
        try:
            return timedelta(seconds=tdORfloat)
        except TypeError:
            raise TypeError('That wasn\'t a float OR a timedelta, what the hell are you feeding the poor thing!?')

###-----------
###  DOI tools
###-----------

def XMLfromDOI(doi):
    #TODO go online and lookup the doi
    #YOU LIVE IN INTERNET LAND DAMN IT BRAIN
    pass

def XMLfromISBN(isbn):
    pass
    
