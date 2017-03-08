import sqlite3
import xlrd
import os
import time

__metaclass__ = type

class db:

    def __init__(self,dbdir,filedir,flistdir,updtlstdir,netvaldir):
        self.dbdir=dbdir
        self.filedir=filedir
        self.flistdir=flistdir
        self.updtlstdir=updtlstdir
        self.netvaldir=netvaldir

    def dbexist(self):
        # 若db不存在则不能写入table,db创建在类外实现
        return os.path.exists(self.dbdir)

    def tbexist(self,tbdir):
        # table 不存在则不能调用 write_table
        conn=sqlite3.connect(self.dbdir)
        c=conn.cursor()
        exeline='SELECT name FROM sqlite_master WHERE type=\'table\' '
        c.execute(exeline)
        alltables=c.fetchall()
        tbname=(self.get_tablename(tbdir),)
        conn.close()
        return tbname in alltables

    def get_tablename(self,tbdir):
        pass

    def get_tbtitles(self,tbdir):
        pass

    def write_table(self,tbdir):
        # 写入前数据库必须存在
        # 写入失败则删除表格
        pass

    def update_tables(self):
        # 检查是否有新文件，如有则更新,并把更新后的文件写入到 flistdir 中
        # 检测是否存在 flistdir 是否存在，不存在则建立一个
        # 检查新增加的文件
        filelist_w=open(self.flistdir,'a+')
        filelist_r=open(self.flistdir)
        try:
            files=filelist_r.readlines()
            savedtbs=set([tb.strip() for tb in files])
            currntbs=set(os.listdir(self.filedir))
            newaddtbs=sorted(list(currntbs.difference(savedtbs)))
            try:
                newaddtbs.remove('list.txt')
            except ValueError:
                pass
            # 写入新增加的文件
            sqlite3.connect(self.dbdir)
            for dumi in range(len(newaddtbs)):
                tabledir=self.filedir+newaddtbs[dumi]
                self.write_table(tabledir)
                filelist_w.write(newaddtbs[dumi]+'\n')   # 更新 list
        except ValueError:
            print('Error in updating db')
            raise
        finally:
            filelist_r.close()
            filelist_w.close()

    def get_updtlst(self):
        if not self.dbexist():
            print('Data db does NOT exist!')
            return
        conn_db=sqlite3.connect(self.dbdir)
        cd=conn_db.cursor()
        try:
            dbtbs=cd.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
        except:
            raise
        finally:
            conn_db.close()

        netfile=open(self.updtlstdir)
        try:
            nettbs=netfile.readlines()
        except:
            raise
        finally:
            netfile.close()

        dbtables=[]
        [dbtables.append(val[0]) for val in dbtbs]
        nettables=[]
        [nettables.append(val.strip()) for val in nettbs]
        difftb=sorted(list(set(dbtables).difference(set(nettables))))
        return difftb

    def update_netval(self):
        updtlst=self.get_updtlst()

        conn_netval=sqlite3.connect(self.netvaldir)
        conn_db=sqlite3.connect(self.dbdir)
        cn=conn_netval.cursor()
        cd=conn_db.cursor()

        netfile=open(self.updtlstdir,'a+')

        try:
            nettbs=cn.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
            if not ('Net_Values',) in nettbs:
                print('Net_Values table created')
                cn.execute('CREATE TABLE Net_Values (share,asstot,liatot,nettot)')
                for dumi in range(len(updtlst)):
                    tb=updtlst[dumi]
                    exeline='SELECT 科目代码,市值本币 FROM '+ tb +' WHERE 科目代码 IN (\'实收资本\',\'资产合计\',\'负债合计\',\'资产净值\')'
                    rawstaff=cd.execute(exeline).fetchall()
                    cn.execute("INSERT INTO Net_Values VALUES (?,?,?,?)" , (rawstaff[0][-1], rawstaff[1][-1],rawstaff[2][-1],rawstaff[3][-1]) )
                    conn_netval.commit()
                    netfile.write(tb+'\n')
        except:
            raise
        finally:
            conn_netval.close()
            conn_db.close()
            netfile.close()