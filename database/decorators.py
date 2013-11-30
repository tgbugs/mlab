""" Decorators to automatically trigger addition of information to the database go here
"""
import os
from sqlalchemy.orm import Session
from database.models import DataFile,DataFileSource,Experiment
from database.sessions import get_pg_sessionmaker

pg_sm=get_pg_sessionmaker()
session=pg_sm()

def Get_current_experiment():
    return session.query(Experiment).order_by(Experiment.id.desc()).first() #FIXME dangerous hack

def Get_current_datafile():
    return session.query(DataFile).order_by(DataFile.creationDateTime.desc()).first()

def Get_newest_abf(url):
    files=os.listdir(url)
    abf_files=[file for file in files if file[-3:]=='abf']
    abf_files.sort() #FIXME make sure the filenames order correctly
    out=abf_files[-1] #get the last/newest file
    return out

def new_abf_DataFile(function): #TODO could wrap it one more time in a file type or url
    url='D:/tom_data/clampex/' #FIXME
    dfs=session.query(DataFileSource).filter_by(name='clampex 9.2').first()
    if not dfs:
        dfs=DataFileSource(name='clampex 9.2',extension='abf',docstring='a clampex!')
        session.add(dfs)
        try:
            session.commit()
        except:
            session.rollback()
    def wrapped(*args,**kwargs):
        function(*args,**kwargs)
        experiment=Get_current_experiment()
        filename=Get_newest_abf(url)
        print(filename,'will be added to the current experiment!')
        new_df=DataFile(filename=filename,url='file:///'+url,datafilesource_id=dfs,experiment_id=experiment)
        session.add(new_df)
        try:
            session.commit()
        except:
            print('[!] Error commiting file! Rolling back!')
            session.rollback()
    wrapped.__name__=function.__name__
    return wrapped

def new_DF_MetaData(function):
    """ add metadata to the most recent datafile"""
    def wrapper(*args,**kwargs):
        value=function(*args,**kwargs)
        df=Get_current_datafile()
        mds=None #XXX TODO
        df.metadata_.append(df.MetaData(value,metadatasource_id=None))


