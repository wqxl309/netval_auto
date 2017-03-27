import sqlite3
import xlrd
import os
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from WindPy import *
from pandas.io import sql
import time

__metaclass__ = type


class db_connect:
    def __init__(self,dbdir):
        self.dbdir=dbdir
    def __enter__(self):
        self.connection=sqlite3.connect(self.dbdir)
        return self.connection
    def __exit__(self,exc_type,exc_instantce,traceback):
        self.connection.close()
        return False  # pop up errors


class db:

    def __init__(self,dbdir,filedir,flistdir,netvaldir):
        if not os.path.exists(flistdir):
            os.system('type null > '+filedir)
        self.dbdir=dbdir
        self.filedir=filedir
        self.flistdir=flistdir
        self.netvaldir=netvaldir

    def dbexist(self):
        # 若db不存在则不能写入table,创建db在updatetable 中实现
        return os.path.exists(self.dbdir)

    def get_tablename(self,tbdir):
        raise Exception('Derived classes have to realize this method')

    def get_tbtitles(self,tbdir):
        raise Exception('Derived classes have to realize this method')

    def tbindb(self,tbdir):
        # 检测数据库中是否已存在某一个表
        # table 不存在则不能调用 write_table
        with db_connect(self.dbdir) as conn:
            c=conn.cursor()
            exeline='SELECT name FROM sqlite_master WHERE type=\'table\' '
            c.execute(exeline)
            alltables=c.fetchall()
            tbname=(self.get_tablename(tbdir),)
        return tbname in alltables

    def write_table(self,tbdir):
        # 写入前数据库必须存在
        # 写入失败则删除表格
        hasdb=os.path.exists(self.dbdir)  # 写入前数据库必须存在，数据库的建立在方法外实现
        if not hasdb:
            print('Database does NOT exist, no update!')
            return False
        tbname=self.get_tablename(tbdir)
        hastb=self.tbindb(tbdir)
        if hastb:
            print(tbname+' already exists, no update!')
            return False
        # 寻找起始行
        data=xlrd.open_workbook(tbdir)
        table = data.sheets()[0]
        startline=0
        for dumi in range(table.nrows):
            try:
                # 检查首个元素类型，如果能转换为数值则为应该记录的行的起始行
                int(table.row_values(dumi)[0])
            except ValueError:
                if table.row_values(dumi)[0]=='1级科目':
                    startline=dumi
                    break
                else:
                    continue
            else:
                startline=dumi
                break
        # 开始写入table
        #conn=sqlite3.connect(self.dbdir)
        with db_connect(self.dbdir) as conn:
            c=conn.cursor()
            tablename=self.get_tablename(tbdir)
            titles=self.get_tbtitles(tbdir)
            titlenum=len(titles)
            titlestr=[]
            for tl in titles:
                if tl in ('科目代码', '科目名称', '币种','科目级别'):
                    titlestr.append(tl+' TEXT,')
                else:
                    titlestr.append(tl+' REAL,')
            titletrans=''.join(titlestr)[:-1]
            exeline=''.join(['CREATE TABLE ',tablename,' (',titletrans,') '])
            c.execute(exeline)
            print('Table '.join([tablename,' created!']))
            try:
                for dumi in range(startline,table.nrows):
                    exeline=''.join(['INSERT INTO ',tablename,' VALUES (',('?,'*titlenum)[0:(2*titlenum-1)],')'])
                    c.execute(exeline , tuple(table.row_values(dumi)))
                    conn.commit()
            except:   # 无论任何原因导致写入table失败，则都要删除未写完的table
                print('Writing table failed ! ')
                conn.execute('DROP TABLE '.join(tablename))
                raise
            else:
                print('Table '.join([tablename,' updated !']))


    def update_tables(self):
        # 检查是否有新文件，如有则更新,并把更新后的文件写入到 flistdir 中
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
            if len(newaddtbs)==0:
                print('No new tables to update !')
                return
            if not os.path.exists(self.dbdir):
                print('Database for this product does NOT exist, gonna create one')
                conn=sqlite3.connect(self.dbdir)  #创建新的 db 如果不存在的话
                conn.close()  # 创建完成后关闭连接
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

    ########################################################################################

    def get_updtlst(self):   # 提取需要更新的表
        # 提取数据库中存在的 所有表的列表
        if not os.path.exists(self.dbdir):
            print('Data db does NOT exist!')
            return False
        #conn_db=sqlite3.connect(self.dbdir)
        # 提取数据库中已经存储的估值表列表
        with db_connect(self.dbdir) as conn_db:
            cd=conn_db.cursor()
            dbtbs=cd.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
        # 提取当前已储存过的表的table(统一命名为 Processed_Tables),存储于netval数据库（在调用该函数的时候默认其已经存在，否侧报错），如果netval数据库存在则该表必须存在，否则报错
        if not os.path.exists(self.netvaldir):
            raise Exception('Netval db does NOT exist!')
        #conn_net=sqlite3.connect(self.netvaldir)
        processed=[]
        with db_connect(self.netvaldir) as conn_net:
            cn=conn_net.cursor()
            nettbs=cn.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
            if not ('Processed_Tables',) in nettbs:
                raise Exception('No Processed_Tables in the netdb!')
            processed=cn.execute('SELECT * FROM Processed_Tables').fetchall()
        dbtables=[val[0] for val in dbtbs]
        processed_tbs=[val[0] for val in processed]
        difftb=sorted(list(set(dbtables).difference(set(processed_tbs))))
        return difftb


    def update_netval_data(self,codedict):
        # 更新净值表，如果存储净值表的数据库（包含记录已更新的标的 table）不存在的话则创建一个
        if not os.path.exists(self.dbdir):
            print('No dbexist, cannot update netval !')
            return False
        conn_db=sqlite3.connect(self.dbdir)
        conn_db.row_factory=sqlite3.Row
        cd=conn_db.cursor()
        if not os.path.exists(self.netvaldir):
            conn_net=sqlite3.connect(self.netvaldir)
            cn=conn_net.cursor()
            print('Netval db created !')
            try:
                cn.execute('CREATE TABLE Net_Values_Base (date,sharenum,assettot,debttot,assetnet,servfee,keepfee,mangfee,earn,buy,sell)')
                print('Net_Values_Base table created !')
                cn.execute('CREATE TABLE Processed_Tables (tablename TEXT)')
                print('Processed_Tables table created !')
            except:
                conn_net.close()
                conn_db.close()
                raise
        else:
            conn_net=sqlite3.connect(self.netvaldir)
            cn=conn_net.cursor()
            nettbs=cn.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
            if not (('Net_Values_Base',) in nettbs and ('Processed_Tables',) in nettbs):
                print('Netval db may be modified illgeally, please check !')
                return False

        updtlst=self.get_updtlst()
        if len(updtlst)==0:
            print('No new nettable to update !')
            return False

        try:  #更新净值表
            for dumi in range(len(updtlst)):
                tb=updtlst[dumi]
                cols=cd.execute('SELECT * FROM '+tb).fetchone().keys()  #提取所有列的标题
                if '市值本币' in cols:
                    valcol='市值本币'
                else:
                    valcol='市值'

                print(tb)

                temp=cd.execute('SELECT 科目代码 FROM '+tb).fetchall()
                codes=[t[0].strip() for t in temp]
                select=['\''+codedict[c]+'\',' for c in codedict if codedict[c] in codes]
                selectlst='('+''.join(select)[:-1]+')'
                exeline=''.join(['SELECT 科目代码,',valcol,' FROM ',tb ,' WHERE 科目代码 IN ',selectlst])
                valinfo=cd.execute(exeline).fetchall()
                valdict={}
                for v in valinfo:
                    valdict[v[0]]=v[1]

                valkey=valdict.keys()
                outdict={}
                for k in codedict:
                    if codedict[k] in valkey:
                        outdict[k]=valdict[codedict[k]]
                    else:
                        outdict[k]=0

                cn.execute("INSERT INTO Net_Values_Base VALUES (?,?,?,?,?,?,?,?,?,?,?)" ,
                           (tb[-8:],outdict['sharenum'],outdict['assettot'],outdict['debttot'],outdict['assetnet'],
                           outdict['servfee'],outdict['keepfee'],outdict['mangfee'],outdict['earn'],outdict['buy'],outdict['sell']) )
                cn.execute("INSERT INTO Processed_Tables VALUES (?)" , (tb,) )
                conn_net.commit()
                print(tb[-8:],tb[-8:],outdict['sharenum'],outdict['assettot'],outdict['debttot'],outdict['assetnet'],
                           outdict['servfee'],outdict['keepfee'],outdict['mangfee'],outdict['earn'],outdict['buy'],outdict['sell'])
                print( tb+' update finished ! ' )
        except:
            raise
        finally:
            conn_net.close()
            conn_db.close()


    def generate_netvalue(self,digits,confirmdays):
        # 从头计算净值表，包括全部日期（包含非交易日）
        start=time.time()
        w.start()
        print(time.time()-start)
        with db_connect(self.netvaldir) as conn_net:
            data=pd.read_sql('SELECT * FROM Net_Values_Base',conn_net)
            sorteddata=data.sort_values(['date'],ascending=[1])

            # diff1=-sorteddata['servfee'].diff()
            # diff1[diff1<=0]=0
            # diff1[0]=0
            # diff2=-sorteddata['mangfee'].diff()
            # diff2[diff2<=0]=0
            # diff2[0]=0
            # diff3=-sorteddata['earn'].diff()
            # diff3[diff3<=0]=0
            # diff3[0]=0
            # fees=pd.concat([diff1,diff2,diff3],axis=1)  # type: pd.DataFrame

            fees=-(sorteddata.loc[:,['servfee','keepfee','mangfee','earn']].diff())
            fees[fees<=0]=0
            fees.loc[0,:]=0
            paid=fees.sum(axis=1)

            dates=sorteddata['date']
            comptot=sorteddata['assettot']-sorteddata['sell']  # 资产总额扣除应付赎回款
            netreal=sorteddata['assetnet']/sorteddata['sharenum'] # 真实净值
            sharechg=sorteddata['sharenum'].diff()
            sharechg[0]=0

            # 和前一个数值相比, 确定 confirm date (T+C) 的位置
            idxchg_TC=sharechg!=0 # type: pd.DataFrame
            idxchg_TC[0]=False
            chgpos_TC=idxchg_TC[idxchg_TC.values].index

            # 和后一个数值相比，很确定 confirm date-1 (T+C-1) 的位置
            #idxchg_TCm1=pd.concat([idxchg_TC[1:] , pd.DataFrame([False])],ignore_index=True)  # type: pd.DataFrame
            #chgpos_TCm1=idxchg_TCm1[idxchg_TCm1.values].index

            chgdate=dates[chgpos_TC].values
            opendt=[w.tdaysoffset(-confirmdays,c).Times[0] for c in chgdate] # 开放日 in wind format
            opendate=[dt.datetime.strftime(t,'%Y%m%d') for t in opendt]  # 开放日, T
            openidx=dates.isin(opendate)  # 开放日位置

            inout=np.zeros_like(netreal)
            inout2=np.zeros_like(netreal)
            inout[chgpos_TC] =np.round(netreal[openidx.values].values,digits)*sharechg[chgpos_TC].values
            idxchg_TCm1=np.zeros_like(netreal)
            opennum=0
            opentot=opendate.__len__()
            for dumi in range(dates.__len__()):
                if opennum>=opentot:
                    break
                mydt=dates.values[dumi]
                if mydt>opendate[opennum] and mydt<chgdate[opennum]:
                    inout2[dumi]=inout[chgpos_TC[opennum]]
                    idxchg_TCm1[dumi]=1
                elif mydt>=chgdate[opennum]:
                    opennum+=1

            # 分子，与确认日对齐
            rets=np.zeros_like(netreal)
            amtchg=np.zeros_like(netreal)
            numerator=(comptot.values+paid.values+idxchg_TCm1*inout2)[1:]
            denominator=comptot.values[:-1]+(idxchg_TCm1*inout2+idxchg_TC.values*inout)[1:]
            rets[1:]=numerator/denominator-1
            amtchg[1:]=comptot.values[1:]-comptot.values[:-1]+paid.values[1:]-inout[1:]
            netvals=pd.DataFrame(np.column_stack([dates.values,paid,netreal,np.cumprod(1+rets),rets,amtchg,np.cumsum(amtchg)]),
                                 columns=['Date','Paid','NetSingle','NetCumulated','Returns','AmtChg','AmtCumChg'])
            # sql.to_sql(pd.concat([sorteddata,netvals],axis=1),name='Net_Values',con=conn_net,if_exists='replace')
            sql.to_sql(netvals,name='Net_Values',con=conn_net,if_exists='replace')
            # plt.figure()
            # plt.plot(netvals['NetCumulated'].values-netvals['NetSingle'].values)
            # plt.show()

        #w.close()





    def take_netvalue(self,startdate,enddate):
        pass

if __name__=='__main__':
    #w.start()
    # print (w.tdays('20161230','20171230','Days=Trading'))
    # w.close()
    pass