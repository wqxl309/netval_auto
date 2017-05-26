
import os
import threading

from modules.file_to_database.file_to_database import *
from src_new.global_vars import *
from modules.netvalues_base.netvalues_base import *




# 更新估值表 至 数据库
for p in PRODUCTS_INFO:
    dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
    filedir = os.path.join(filedir_base,''.join(['估值信息 ',p['pname']]))
    processor = rawfile_process(dbdir=dbdir,filedir=filedir,pcode=p['pcode'],pname=p['pname'])
    threading.Thread(target=processor.update_database,args=(VARTYPES,)).start()