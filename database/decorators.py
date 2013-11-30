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
        session.commit()
    def wrapped(*args,**kwargs):
        function(*args,**kwargs)
        experiment=Get_current_experiment()
        filename=Get_newest_abf(url)
        new_df=DataFile(filename=filename,url=url,datafilesource_id=dfs)
        session.add(new_df)
        session.commit()
    wrapped.__name__=function.__name__
    return wrapped


