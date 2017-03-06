#from database.db_manipulation import *
from database.database_table import *
import os
import time
import sqlite3

#dbdir='E:\\估值表数据库\\BaiquanNo1.db'
#allfiledir='C:\\Users\\Jiapeng\\Desktop\\Net Value\\估值信息 百泉一号\\'
#repttype=True
#bq1list=open('C:\\Users\\Jiapeng\\Desktop\\Net Value\\估值信息 百泉一号\\list.txt')
#list=bq1list.readlines()
#for dumi in range(len(list)):
#    start=time.time()
#    filename=(list[dumi]).strip()
#    filedir=allfiledir+filename
#    tablename=filename[5:(len(filename)-4)]
#    print(tablename)
#    create_table_db(dbdir,filedir,tablename,repttype)
#    print( ' Elasped time %f seconds' % (time.time()-start) )


dbdir=r'E:\估值表数据库\Huijin1.db'
allfiledir=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号'+'\\'
filelist=open(r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号\list.txt')

sqlite3.connect(dbdir)
list=filelist.readlines()
for dumi in range(len(list)):
    start=time.time()
    filename=(list[dumi]).strip()
    tabledir=allfiledir+filename
    temp=Huijin1_dbtb(dbdir,tabledir,allfiledir,filelist)
    temp.write_table()

    print( ' Elasped time %f seconds' % (time.time()-start) )


    def db_construct(self):
        sqlite3.connect(self.dbdir)
        filelist=open(self.flistdir)
        list=filelist.readlines()
        for dumi in range(len(list)):
            start=time.time()
            filename=(list[dumi]).strip()
            tabledir=self.filedir+filename
            temp=Huijin1_dbtb(dbdir,tabledir,allfiledir,filelist)
            temp.write_table()

            print( ' Elasped time %f seconds' % (time.time()-start) )