
import sqlite3
import os
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mpdt
# from WindPy import *
from remotewind import w
from pandas.io import sql
from src.help_functions import *
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
        self.productname=None
        self.mandarine=None
        self.ipodate=None
        self.confirmdays=None
        self.net_digits=None
        if not os.path.exists(flistdir):
            os.system('type null > '+filedir)
        self.dbdir=dbdir
        self.filedir=filedir
        self.flistdir=flistdir
        self.netvaldir=netvaldir   # 不要再次创建 netval db if not exists

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
                elif len(tl)>0:
                    titlestr.append(tl+' REAL,')
                else:
                    titlestr.append(tl)
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
                exeline='DROP TABLE '+tablename
                conn.execute(exeline)
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
                print(tb[-8:],outdict['sharenum'],outdict['assettot'],outdict['debttot'],outdict['assetnet'],
                           outdict['servfee'],outdict['keepfee'],outdict['mangfee'],outdict['earn'],outdict['buy'],outdict['sell'])
                print( tb+' update finished ! ' )
        except:
            raise
        finally:
            conn_net.close()
            conn_db.close()


    def generate_netvalues(self):
        # 从头计算净值表，包括全部日期（包含非交易日）
        digits=self.net_digits
        confirmdays=self.confirmdays
        w.start()
        with db_connect(self.netvaldir) as conn_net:
            data=pd.read_sql('SELECT * FROM Net_Values_Base',conn_net)
            sorteddata=data.sort_values(['date'],ascending=[1])
            dates=sorteddata['date']
            # 检查缺失交易日期，如果有缺失则只生成至缺失交易日前一（交易）日； 有交易日就应该有估值表，反之不然
            firstdate=dates.values[0]
            lastdate=dates.values[-1]
            tdays=w.tdays(firstdate,lastdate).Times
            trddays=pd.DataFrame([dt.datetime.strftime(t,'%Y%m%d') for t in tdays])
            misstrd=~trddays.isin(dates.values)
            trdmiss=trddays[misstrd.values]
            if not trdmiss.empty:
                # 截止到第一个缺失交易日前的一个交易日
                cutdate=dt.datetime.strftime(w.tdaysoffset(-1,trdmiss.values[0][0]).Times[0],'%Y%m%d')
                cutpos=dates<=cutdate
                sorteddata=sorteddata[cutpos]
            dates=sorteddata['date']
            fees=-(sorteddata.loc[:,['servfee','keepfee','mangfee','earn']].diff())
            fees[fees<=0]=0
            fees.loc[0,:]=0
            paid=fees.sum(axis=1)
            comptot=sorteddata['assettot']-sorteddata['sell']  # 资产总额扣除应付赎回款
            netreal=sorteddata['assetnet']/sorteddata['sharenum'] # 真实(单位)净值

            bookearn=sorteddata['earn'].diff()
            bookearn.iloc[0]=0
            bookearn[bookearn<0]=0

            cumret=((sorteddata['assetnet'].values[1:]+bookearn.values[1:])/sorteddata['assetnet'].values[:-1])*(sorteddata['sharenum'].values[:-1]/sorteddata['sharenum'].values[1:])-1
            cumret=np.row_stack([np.zeros([1,1]),np.reshape(cumret,[dates.__len__()-1,1])])
            netcum=np.cumprod(1+cumret)*netreal[0]

            sharechg=sorteddata['sharenum'].diff()
            sharechg[0]=0
            # 和前一个数值相比, 确定 confirm date (T+C) 的位置
            idxchg_TC=sharechg!=0 # type: pd.DataFrame
            idxchg_TC[0]=False
            chgpos_TC=idxchg_TC[idxchg_TC.values].index
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
            netvals=pd.DataFrame(np.column_stack([dates.values,netreal,netcum,np.cumprod(1+rets)*netreal[0],rets,amtchg,np.cumsum(amtchg)]),
                                 columns=['Date','NetSingle','NetCumulated','NetCompensated','Returns','AmtChg','AmtCumChg'])
            sql.to_sql(netvals,name='Net_Values',con=conn_net,if_exists='replace')
            print('Netvalues updated from '+firstdate+' to '+dates.values[-1])
        w.close()


    def update_netvalues(self):
        pass


    def take_netvalue(self,startdate=False,enddate=False,freq='DAY',indicators=True,plots=True,mktidx=('000300.SH','000905.SH'),outputdir=False):
        w.start()
        with db_connect(self.netvaldir) as conn_net:
            if not startdate:
                startdate=self.ipodate.strftime('%Y%m%d')
            if not enddate:
                enddate=dt.datetime.today().strftime('%Y%m%d')
            data=pd.read_sql(''.join(['SELECT * FROM Net_Values WHERE date >=',startdate,' AND date<=',enddate]),conn_net)
            dates=data['Date']
            head=dates.values[0]
            tail=dates.values[-1]
            if freq.upper()=='WEEK':
                period='W'
            elif freq.upper()=='MONTH':
                period='M'
            else:
                period='D'
            ttimes=w.tdays(head,tail,'Period='+period).Times
            tperiods=[dt.datetime.strftime(t,'%Y%m%d') for t in ttimes]
            needextra=False   # 使用周度、月度数据的情况下，确保第一个值为索取数据第一个 交易日
            if (tperiods[0] > head):
                tmptimes=w.tdays(head,tperiods[0],'Period=D').Times
                head=dt.datetime.strftime(tmptimes[0],'%Y%m%d')
                needextra=True
                tperiods.insert(0,head)
            trdidx=dates.isin(tperiods)
            trddata=data[trdidx]

            print('Updating '+self.mandarine+ ' -- Periods from %s to %s' % (tperiods[0],tperiods[-1]))
            print()

            output_results={}

            if indicators:
                # 须确保输入的是numpy array
                raw=calc_indicators(trddata.loc[:,['NetCumulated','NetCompensated']].values)  # returns : mean,std,downstd,winrate,maxdd,maxwins,maxlosses
                multiplier=(freq.upper()=='DAY')*250+(freq.upper()=='WEEK')*52+(freq.upper()=='MONTH')*12
                indshow={}  # 年化收益率、最大回撤、年化波动率、年化下行波动率、夏普、所提诺、calmar，周期胜率，连续最大盈利周期数，连续最大亏损周期数
                indshow['AnnRet']=raw['mean']*multiplier
                indshow['AnnVol']=raw['std']*np.sqrt(multiplier)
                indshow['AnnDownVol']=raw['downstd']*np.sqrt(multiplier)
                indshow['MaxDd']=raw['maxdd']
                indshow['Sharpe']=indshow['AnnRet']/indshow['AnnVol']
                indshow['Sortino']=indshow['AnnRet']/indshow['AnnDownVol']
                indshow['Calmar']=indshow['AnnRet']/np.abs(indshow['MaxDd'])
                indshow['WinRate']=raw['winrate']
                indshow['MaxWinsPrd']=raw['maxwinsnum']
                indshow['MaxLossPrd']=raw['maxlossnum']
                #earnamt=trddata['AmtCumChg'][1:].values-trddata['AmtCumChg'][:-1].values
                #indshow['WinLossRate']=-np.sum(earnamt[earnamt>0])/np.sum(earnamt[earnamt<0])
                indshow['ValueType']=[u'费后累计净值',u'费前净值']
                print([u'费后累计净值',u'费前净值'])
                for key in sorted(indshow.keys()):
                    print(key+' : ',indshow[key] )
                print()
                print()
                output_results['indicators']=indshow

            netsig=trddata['NetCumulated'].values
            netcum=trddata['NetCompensated'].values
            netdate=trddata['Date']
            if mktidx:
                winddata=w.wsd(mktidx,'close',head,tail,'Period='+period)
                if needextra:
                    windex=w.wsd(mktidx,'close',head,head)
                    exdata=np.array(windex.Data)
                    idxdata=np.row_stack([exdata,np.array(winddata.Data).T])
                else:
                    idxdata=np.array(winddata.Data).T
                tempidx=idxdata/idxdata[0,:]
                idxdata_sig=tempidx*netsig[0]
                idxdata_cum=tempidx*netcum[0]
                maxidx=np.max(np.max(idxdata_cum))
                minidx=np.min(np.min(idxdata_sig))
                plotlimits=[np.min([minidx,np.min(netsig)])*0.8,np.max([maxidx,np.min(netcum)])*1.2]
            else:
                plotlimits=[np.min(netsig)*0.8,np.min(netcum)*1.2]

            if plots:
                fig=plt.figure(figsize=(20,15))
                showdatenum=20
                N=len(netdate)
                if N<=showdatenum:
                    showidx=[x for x in range(N)]
                else:
                    step=int(np.floor(N/showdatenum))
                    showidx=[x for x in range(0,N,step)]
                    if N-1-showidx[-1]>=step/2:
                        showidx.append(N-1)
                ax=fig.add_subplot(121)
                ax.set_ylim(plotlimits)
                ax.set_xlim([showidx[0],showidx[-1]])
                ax.plot(netsig,'r',lw=2,label=self.productname)
                colors=['g','b']
                if mktidx:
                    for dumi in range(len(mktidx)):
                        ax.plot(idxdata_sig[:,dumi],colors[dumi],label=mktidx[dumi],lw=2)
                plt.xticks(rotation=70)
                plt.xticks(showidx,netdate.iloc[showidx])
                plt.legend(loc='upper left')
                #ax.xaxis.set_major_formatter(mpdt.DateFormatter('%Y-%m-%d'))
                #plt.xticks(pd.date_range(trddata['NetSingle'].index[0],trddata['NetSingle'].index[-1],freq='1min'))
                ax2=fig.add_subplot(122)
                ax2.set_ylim(plotlimits)
                ax2.set_xlim([showidx[0],showidx[-1]])
                ax2.plot(netcum,'r',lw=2,label=self.productname)
                colors2=['b','gray']
                if mktidx:
                    for dumi in range(len(mktidx)):
                        ax2.plot(idxdata_cum[:,dumi],colors2[dumi],label=mktidx[dumi],lw=2)
                plt.xticks(rotation=70)
                plt.xticks(showidx,netdate.iloc[showidx])
                plt.legend(loc='upper left')
                plt.show()

            if outputdir:
                if mktidx:
                    trdselect=trddata.loc[:,['Date','NetSingle','NetCumulated','NetCompensated']]
                    trdselect.columns = ['日期','单位净值','累计净值','补回净值']
                    mktidxdata=pd.DataFrame(idxdata,columns=mktidx,index=trdselect.index)
                    output=pd.concat([trdselect,mktidxdata],axis=1)
                else:
                    output=trddata.loc[:,['Date','NetSingle','NetCumulated','NetCompensated']]
                    output.columns = ['日期','单位净值','累计净值','补回净值']
                if outputdir=='return data':
                    output_results['outdata']=output
                else:
                    #output.to_csv(outputdir,index=False)
                    writer=pd.ExcelWriter(outputdir)
                    output.to_excel(writer,sheet_name=self.mandarine,index=False)

        return output_results
