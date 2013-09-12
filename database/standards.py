#file for standard methods to be used throughout the database to maintain consistency of data
#ALL functions used in __init__ to write data and their pairs for reading data from queries should go here

#input sanitization goes here
from urllib import parse,request
from os import listdir

class URL_STAND:
    """Standards for url sting termination and initiation for consistently composing paths"""
    @staticmethod
    def baseClean(base_url): return None if base_url is None else base_url.rstrip('/')
    @staticmethod
    def pathClean(path): return None if path is None else '/'+path.strip('/').rstrip('/')
    @staticmethod
    def test_url(full_url):
        #FIXME rework this to go through a full url scheme handler that can be extended with resources
        #see if one exists, it should...
        parsed=parse.urlparse(full_url)
        if parsed.scheme is 'file':
            path=parsed.path
            if path.count(':'): #windows, stupid / mucking with C:
                path=path[1:]
            try:
                listdir(path)
            except:
                raise FileNotFoundError('Local path does not exist!') #FIXME this => wierd error handling
        else:
            print('not a file, not implemented, will not catch')
            #raise NotImplemented

            




