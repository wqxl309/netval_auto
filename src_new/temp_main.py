
import os
import threading

from modules.file_to_database.file_to_database import *
from src_new.global_vars import *
from modules.netvalues_base.netvalues_base import *
from modules.netvalues_calculation.netval_calculation import *




for p in PRODUCTS_INFO:
    if p['nickname']=='BaiquanMS1':
        # 更新估值表 至 数据库
        dbdir = os.path.join(dbdir_base,''.join(['rawdb_',p['nickname'],'.db']))
        filedir = os.path.join(filedir_base,''.join(['估值信息 ',p['pname']]))
        #processor = rawfile_process(dbdir=dbdir,filedir=filedir,pcode=p['pcode'],pname=p['pname'])
        #processor.update_database(VARTYPES)
        # threading.Thread(target=processor.update_database,args=(VARTYPES,)).start()
        # 提取估值表基础元素
        netdbdir = os.path.join(netdbdir_base,''.join(['netdb_',p['nickname'],'.db']))
        elements_extracter = netvalues_base(dbdir,netdbdir)
        elements_extracter.update_netdb(codedict=CODEDICT[p['nickname']],indexmark='科目代码',valcols=('市值','市值本币'))
        # 计算净值
        calculator = netvalues_calculation(pname=p['pname'],netdbdir=netdbdir,confirmdays=p['confirmdays'],precision=p['precision'])
        calculator.generate_netvalues()