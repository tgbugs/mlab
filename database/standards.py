#file for standard methods to be used throughout the database to maintain consistency of data
#ALL functions used in __init__ to write data and their pairs for reading data from queries should go here

#input sanitization goes here
from urllib import parse
from os import listdir

from datetime import datetime,timedelta #ALL TIMES ARE UTC WITH tzinfo=None, CONVERT LATER

import requests as r #FIXME :(

###--------------
###  URL handling
###--------------

class URL_STAND:
    """Standards for url sting termination and initiation for consistently"""
    #TODO should handle matching local files to the computer they actually came from relative to the db
    @staticmethod
    def urlClean(url):
        p=parse.urlparse(url)
        if p.scheme is 'file':
            #TODO get relatvie computer path #the good news is that only the database is remote, this code won't be, it will be local yay for transparency!
            pass
        return None if url is None else url.rstrip('/')+'/' #FIXME make it so this strips to last/
    
    @staticmethod
    def ping(full_url):
        #FIXME rework this to go through a full url scheme handler that can be extended with resources
        #see if one exists, it should...
        parsed=parse.urlparse(full_url)
        if parsed.scheme is 'file':
            path=parsed.path
            if path[2]==(':'): #FIXME this is not actually valid... windows :/
                path=path[1:]
            try:
                listdir(path)
                return path
            except:
                raise FileNotFoundError('Local path does not exist!') #FIXME this => wierd error handling
        else: #TODO requests does not actually handle anything besides http/s :/
            if not r.head(full_url).ok: #also data computer on the internet???
                raise FileNotFoundError('Remote path is not OK!') #FIXME this => wierd error handling
            else:
                return path

    @staticmethod
    def getCreationDateTime(full_url):
        parsed=parse.urlparse(full_url)
        if parsed.scheme is file:
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
    
