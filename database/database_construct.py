
from src.Baiquan1 import *
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


dbdirJQ=r'E:\估值表数据库\Jinqu1.db'
filedirJQ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号'+'\\'
flistdirJQ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号\list.txt'


dbdirHJ=r'E:\估值表数据库\Huijin1.db'
filedirHJ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号'+'\\'
flistdirHJ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号\list.txt'

dbdirBQ1=r'E:\估值表数据库\Baiquan1.db'
filedirBQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉一号'+'\\'
flistdirBQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉一号\list.txt'
netvaldirBQ1=r'E:\净值表\netvalBQ1.db'
updtlstdirBQ1=r'E:\净值表\netvalBQ1.txt'

dbdirBQ2=r'E:\估值表数据库\Baiquan2.db'
filedirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号'+'\\'
flistdirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号\list.txt'


obj=Baiquan1_db(dbdirBQ1,filedirBQ1,flistdirBQ1,updtlstdirBQ1,netvaldirBQ1)
print ( obj.get_updtlst() )

