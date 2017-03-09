
from src.base_class import *

class Jinqu1_db(db):   # 进取和百泉1号相似较大
    def __init__(self,dbdir,filedir,flistdir,updtlstdir,netvaldir):
        super(Jinqu1_db,self).__init__(dbdir,filedir,flistdir,updtlstdir,netvaldir)

    def get_tablename(self,tbdir):
        strings=tbdir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0][6:]