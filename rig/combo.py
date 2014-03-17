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
from rig.functions import espFuncs,clxFuncs,mccFuncs


class allFuncs(espFuncs,clxFuncs,mccFuncs):
    def __init__(self,modestate,esp,mcc,clx):
        super().__init__(modestate,esp=esp,mcc=mcc,clx=clx)


    def do_som(self):
        self.



    
