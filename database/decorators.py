""" Decorators to automatically trigger addition of information to the database go here
"""
import os
import inspect
from sqlalchemy.orm import sessionmaker
from database.table_logic import logic_StepEdge
from database.models import DataFile,DataFileSource,Experiment,Hardware,MetaDataSource
from database.engines import engine

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
    except:
        print('[!] %s could not be added! Rolling back!')
        session.rollback()
    finally:
        session.close()

def Get_newest(MappedClass): #FIXME this doesnt go here...
    session=Session()
    out=session.query(MappedClass).order_by(MappedClass.id.desc()).first() #FIXME dangerous hack
    session.close()
    return out

#def Get_current_experiment():

def Get_current_datafile():
    session=Session()
    out= session.query(DataFile).order_by(DataFile.creationDateTime.desc()).first()
    session.close()
    return out

def Get_newest_abf(url):
    files=os.listdir(url)
    abf_files=[file for file in files if file[-3:]=='abf']
    abf_files.sort() #FIXME make sure the filenames order correctly
    out=abf_files[-1] #get the last/newest file
    return out

###
#function decorators
def new_abf_DataFile(function): #TODO could wrap it one more time in a file type or url
    url='D:/tom_data/clampex/' #FIXME
    init_sess=Session()
    dfs=init_sess.query(DataFileSource).filter_by(name='clampex 9.2').first()
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

    def wrapped(*args,**kwargs):
        function(*args,**kwargs)
        experiment=Get_newest(Experiment)
        filename=Get_newest_abf(url)
        print(filename,'will be added to the current experiment!')
        new_df=DataFile(filename=filename,url='file:///'+url,datafilesource_id=dfs,experiment_id=experiment)
        session_add_wrapper(new_df)
    wrapped.__name__=function.__name__
    return wrapped

def _new_DF_MetaData(function):
    """ add metadata to the most recent datafile"""
    def wrapper(*args,**kwargs):
        value=function(*args,**kwargs)
        df=Get_current_datafile()
        mds=None #XXX TODO
        df.metadata_.append(df.MetaData(value,metadatasource_id=None))

def is_mds(function,prefix,units,mantissa=None,hardware_id=None):
    """ Turn a function into a metadatasource if write is on... """
    #TODO figure out how to make write switchable
    #TODO have this add the function to the gobla dataio dict!
    name=function.__name__
    if not hardware_id:
        try:
            hardware_id=function.hardware_id
        except:
            raise TypeError('You must specify a harware_id or mark the parent'
                            ' class with @hardware_interface. %s'%name)
    init_sess=Session()
    mds=init_sess.query(MetaDataSource).filter_by(name).one()
    if not mds:
        mds=MetaDataSource(name=name,prefix=prefix,units=units,
                           mantissa=mantissa,hardware_id=hardware_id)
        init_sess.add(mds)
        try:
            init_sess.commit()
        except:
            print('[!] Commit failed! Rolling back!')
        finally:
            init_sess.close()
            del(init_sess)
    def wrapper(*args,write_target=None,**kwargs): #is this really a cool way to do it?! :D
                                    #yes because we can just use '.c_datafile' in datFuncs! :D
        value=function(*args,**kwargs)
        if not write_target:
            return value
        if len(value) == 2: #TODO have functions that do abs error return a tuple!
            abs_error=value(2)
        else:
            abs_error=None
        md_kwargs={'value':value,'abs_error':abs_error}
        if type(write_target) == DataFile:
            md=write_target.MetaData(DataFile=write_target,**md_kwargs)
        else:
            wt_id=write_target.id
            md=write_target.MetaData(parent_id=wt_id,**md_kwargs)
        session_add_wrapper(md)
        return value

    wrapper.__name__=function.__name__
    wrapper.__doc__=function.__doc__+"\n This function REQUIRES a write_target, a fake one won't work"
    return wrapper


###
#class decorators

def hardware_interface(name):
    """ Make cls into a hardware interface that is recorded by the database.
        Most useful for the *Control classes eg espControl.
        Should be used in conjunction with the @is_mds decorator
    """
    def inner(cls):
        session=Session()
        hardware=session.query(Hardware).filter_by(name=name).one()
        session.close()
        cls.hardware=hardware
        for member in inspect.getmembers(cls):
            if inspect.ismethod(member) and hasattr(member,'is_mds'):
                member.hardware_id=hardware.id
        return cls
    return inner
