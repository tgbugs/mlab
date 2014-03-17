""" Decorators to automatically trigger addition of information to the database go here
"""
import os
import socket
import inspect
from sqlalchemy.orm import sessionmaker, object_session
from database.table_logic import logic_StepEdge
from database.models import DataFile,DataFileSource,Experiment,Hardware,MetaDataSource,Repository
from database.engines import engine #FIXME tests >_< need a way to synchornize this ;_; need a way to make decorators based on the session, but right now we are just going to switch stuff manually
from database.imports import printD
from database.standards import Get_newest_file

_Session=sessionmaker(bind=engine)
def Session():
    session=_Session()
    logic_StepEdge(session)
    return session

def session_add_wrapper(object_to_add):
    session=Session()
    session.add(object_to_add)
    try:
        session.commit()
    except BaseException as e:
        print(e)
        print('[!] %s could not be added! Rolling back!'%object_to_add)
        session.rollback()
        raise
    finally:
        session.close()

def Get_newest_id(MappedClass): #FIXME this doesnt go here...
    session=Session()
    out=session.query(MappedClass).order_by(MappedClass.id.desc()).first() #FIXME dangerous hack
    session.close()
    printD(out.id)
    return out

#def Get_current_experiment():

def Get_current_datafile():
    session=Session()
    out= session.query(DataFile).order_by(DataFile.creationDateTime.desc()).first()
    session.close()
    return out

def Get_newest_abf(_path):
    print(_path)
    files=os.listdir(_path)
    abf_files=[file for file in files if file[-3:]=='abf']
    abf_files.sort() #FIXME make sure the filenames order correctly
    out=abf_files[-1] #get the last/newest file
    return out

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

def get_local_jpg_path(hostname,osname,program=None): #TODO FIXME there are multiple jpg paths

    os_hostname_jpg_path={ #;alksdjf;laksdjf;laksdjf;laksdjf;laksdjf FIXME
    'nt':{'HILL_RIG':'D:/tom_data/rigcam/'},
    'posix':{'athena':'/home/tom/mlab_data/rigcam/'},
    }
    fpath=os_hostname_jpg_path[osname][hostname]
    return fpath

def get_local_extension_path(extension,program=None):
    hostname=socket.gethostname()
    osname=os.name
    exDict={'abf':get_local_abf_path,
            'jpg':get_local_jpg_path,
    }
    fpath = exDict[extension](hostname,osname,program)
    return hostname,fpath



###
#function decorators
def new_DataFile(extension,subjects_getter=None): #TODO could wrap it one more time in a file type or url #FIXME broken if there is more than one path per extension type >_<
    def inner(function): #TODO could wrap it one more time in a file type or url
        #fpath='D:/tom_data/clampex/' #FIXME
        hostname,fpath=get_local_extension_path(extension)
        url='file://%s/%s'%(hostname,fpath)

        init_sess=Session()

        repo=init_sess.query(Repository).filter_by(url=url).first() #FIXME try/except?
        dfs=init_sess.query(DataFileSource).filter_by(name='clampex 9.2').first()
        #printD(repo)
        if not repo or not dfs:
            if not repo:
                init_sess.add(Repository(url=url))
            if not dfs:
                dfs=DataFileSource(name='lol wut!?',extension=extension,docstring='a whoknows!') #FIXME TODO generalize!
                init_sess.add(dfs)
            try:
                init_sess.commit()
            except:
                init_sess.rollback()
            finally:
                init_sess.close()
                del(init_sess)
        else:
            init_sess.close()
            del(init_sess)

        def wrapped(*args,subjects=[],**kwargs):
            function(*args,**kwargs)
            experiment=Get_newest_id(Experiment)
            if not subjects:
                try:
                    subjects=subjects_getter()
                except:
                    pass
            filename=Get_newest_file(fpath,extension) #FIXME this can be faster than the snapshot!
            print(filename,'will be added to the current experiment!')
            new_df=DataFile(filename=filename,url=url,datafilesource_id=dfs.id,
                            experiment_id=experiment.id,Subjects=subjects)
            session=object_session(new_df) #need this because new_df may be on subjects session
            if session:
                session.add(new_df)
                try:
                    session.commit()
                except:
                    print('[!] %s could not be added! Rolling back!'%new_df)
                    session.rollback()
                    raise
            else:
                session_add_wrapper(new_df)
        wrapped.__name__=function.__name__
        wrapped.is_dfs=True #XXX this function is the literal datafile source# TODO perhaps update to match is_mds
        return wrapped
    return inner

def new_abf_DataFile(subjects_getter=None): #TODO could wrap it one more time in a file type or url
    def inner(function): #TODO could wrap it one more time in a file type or url
        #fpath='D:/tom_data/clampex/' #FIXME
        hostname,fpath=get_local_extension_path('abf')
        url='file://%s/%s'%(hostname,fpath)

        init_sess=Session()

        repo=init_sess.query(Repository).filter_by(url=url).first() #FIXME try/except?
        dfs=init_sess.query(DataFileSource).filter_by(name='clampex 9.2').first()
        #printD(repo)
        if not repo or not dfs:
            if not repo:
                init_sess.add(Repository(url=url))
            if not dfs:
                dfs=DataFileSource(name='clampex 9.2',extension='abf',docstring='a clampex!')
                init_sess.add(dfs)
            try:
                init_sess.commit()
            except:
                init_sess.rollback()
            finally:
                init_sess.close()
                del(init_sess)
        else:
            init_sess.close()
            del(init_sess)

        def wrapped(*args,subjects=[],**kwargs):
            function(*args,**kwargs)
            experiment=Get_newest_id(Experiment)
            if not subjects:
                try:
                    subjects=subjects_getter()
                except:
                    pass
            filename=Get_newest_abf(fpath)
            print(filename,'will be added to the current experiment!')
            new_df=DataFile(filename=filename,url=url,datafilesource_id=dfs.id,
                            experiment_id=experiment.id,Subjects=subjects)
            session=object_session(new_df) #need this because new_df may be on subjects session
            if session:
                session.add(new_df)
                try:
                    session.commit()
                except:
                    print('[!] %s could not be added! Rolling back!'%new_df)
                    session.rollback()
                    raise
            else:
                session_add_wrapper(new_df)
        wrapped.__name__=function.__name__
        wrapped.is_dfs=True #XXX this function is the literal datafile source# TODO perhaps update to match is_mds
        return wrapped
    return inner

def _new_DF_MetaData(function):
    """ add metadata to the most recent datafile"""
    def wrapper(*args,**kwargs):
        value=function(*args,**kwargs)
        df=Get_current_datafile()
        mds=None #XXX TODO
        df.metadata_.append(df.MetaData(value,metadatasource_id=None))

def is_mds(prefix,unit,hardware_name,mantissa=None,wt_getter=None):
    """ Turn a function into a metadatasource if write is on... 
        wt_getter should return an iterable of MappedInstances
    """
    #TODO figure out how to make write switchable
    #TODO have this add the function to the gobla dataio dict!
    def inner(function):
        name=function.__name__
        #if not hardware_name:
            #try:
                #hardware_id=function.hardware_id #FIXME what!? if this is decorated TWICE?!
            #except:
                #raise TypeError('You must specify a harware_id or mark the parent'
                                #' class with @hardware_interface. %s'%name)
        init_sess=Session()
        hardware=init_sess.query(Hardware).filter_by(name=hardware_name).one()
        try:
            mds=init_sess.query(MetaDataSource).filter(MetaDataSource.hardware_id==hardware.id).filter_by(name=name).one()
            mds_id=mds.id
        except:
            mds=MetaDataSource(name=name,prefix=prefix,unit=unit,mantissa=mantissa,
                               hardware_id=hardware,docstring=function.__doc__)
            init_sess.add(mds)
            try:
                init_sess.commit()
                mds_id=mds.id
            except:
                print('[!] Commit failed! Rolling back!')
                raise
            finally:
                init_sess.close()
                del(init_sess)
        def wrapper(*args,write_targets=[],**kwargs): #is this really a cool way to do it?! :D
                                        #yes because we can just use '.c_datafile' in datFuncs! :D
            value=function(*args,**kwargs)

            if not write_targets:
                try:
                    write_targets=wt_getter() #FIXME this doesnt quite work because datFuncs has a state :/
                except:
                    #raise
                    return value
            if type(value)==tuple and len(value) == 2: #TODO have functions that do abs error return a tuple!
                abs_error=value[2]
            else:
                abs_error=None

            md_kwargs={'value':value,'abs_error':abs_error,'metadatasource_id':mds_id}
            for write_target in write_targets:
                wt_id=write_target.id
                md=write_target.MetaData(parent_id=wt_id,**md_kwargs)
                session_add_wrapper(md) #FIXME we *may* encounter session collisions here
            return value

        wrapper.__name__=function.__name__
        wrapper.__doc__=function.__doc__+"\n This function REQUIRES a write_target, a fake one won't work"
        wrapper.hardware_name=hardware_name
        wrapper.is_mds=True
        if hasattr(function,'keyRequester'): #FIXME
            wrapper.keyRequester=True
        return wrapper
    return inner


###
#class decorators

def hardware_interface(name): #XXX FIXME rename
    """ Make cls into a hardware interface that is recorded by the database.
        Most useful for the *Control classes eg espControl.
        Should be used in conjunction with the @is_mds decorator
        For write targets to work the class needs to have a self._wt_getter method
    """
    def get_wt_hack(cls,member): #reproduce for dfs
        def wt_func(self,*args,**kwargs):
            func=getattr(self,member.__name__)
            printD(func)
            wt=self._wt_getter()
            return func(*args,write_targets=wt,**kwargs)
        wt_func.__name__='getWT_'+member.__name__
        wt_func.__doc__=member.__doc__
        if hasattr(member,'keyRequester'): #FIXME
            wt_func.keyRequester=True
        setattr(cls,wt_func.__name__,wt_func)
        return cls

    def inner(cls):
        for name,member in inspect.getmembers(cls):
            if inspect.isfunction(member) and hasattr(member,'is_mds'):
                cls=get_wt_hack(cls,member)
        return cls
    return inner

def datafile_maker(cls):
    """ mark classes that have methods that get datafiles
        class must implement functions:
        _sub_getter     returns iterables
        _new_datafile
    """
    def get_sub_hack(cls,member): #reproduce for dfs
        def sub_func(self,*args,**kwargs):
            func=getattr(self,member.__name__)
            subs=self._sub_getter()
            out=func(*args,subjects=subs,**kwargs)
            self._new_datafile() #FIXME really crappy way to communicate that there is a new datafile
            return 
        sub_func.__name__='getSub_'+member.__name__
        sub_func.__doc__=member.__doc__
        setattr(cls,sub_func.__name__,sub_func)
        return cls

    for name,member in inspect.getmembers(cls):
        if inspect.isfunction(member) and hasattr(member,'is_dfs'):
            cls=get_sub_hack(cls,member)
    return cls
