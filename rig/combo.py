import re
import datetime
import inspect as ins
from sys import stdout,stdin
from time import sleep
from debug import TDB,ploc
from rig.ipython import embed
from sqlalchemy.orm import object_session #FIXME vs database.imports?
#from database.decorators import Get_newest_id, datafile_maker, new_abf_DataFile, hardware_interface, is_mds, new_DataFile
from database.standards import Get_newest_file
from threading import RLock
from rig.gui import takeScreenCap
from rig.functions import kCtrlObj

class allFuncs(kCtrlObj):
    def __init__(self,modestate,esp,mcc,clx):
        super().__init__(modestate)
        del(self.ctrl)

        self.session=self.modestate.Session() #THIS is the proper scope for this

        #the controllers, get from all funcs
        #replace self.ctrl with relevant option here
        self.esp=esp
        self.mcc=mcc
        self.clx=clx

    @static_method
    def getRepoDFS(extension,dfs_name='clampex 9.2',url=None): #FIXME make this persistent on init??
        if not url:
            hostname,fpath=get_local_extension_path(extension)
            url='file://%s/%s'%(hostname,fpath)
        init_sess=self.modestate.Session()
        repo=init_sess.query(Repository).filter_by(url=url).first() #FIXME try/except?
        dfs=init_sess.query(DataFileSource).filter_by(name=dfs_name).first()
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
        return repo,dfs

    def add_com_sess(self,obj_to_add):
        self.session.add(obj_to_add)
        try:
            self.session.commit()
        except:
            print('[!] %s could not be added! Rolling back!'%obj_to_add)
            session.rollback()
            raise

    def newDataFile(self,extension,experiment,subjects=[]): #FIXME need other selectors eg: repository >_<
        repo,dfs=getRepoDFS(extension)
        #experiment=Get_newest_id(Experiment) #FIXME unfinished?
        filename=Get_newest_file(fpath,extension) #FIXME this can be faster than the snapshot!
        print(filename,'will be added to the current experiment!')
        new_df=DataFile(filename=filename,url=url,datafilesource_id=dfs.id,
                            experiment_id=experiment.id,Subjects=subjects)

        self.add_com_sess(new_df)
        return new_df


    def do_som



    
