import datetime as dt

import numpy as np
import pandas as pd
from pandas.io import sql
from remotewind import w

from modules.database_assistant.database_assistant import *

class netvalues_calculation:
    def __init__(self,pname,netdbdir,confirmdays,precision):
        self.pname = pname
        self.netdbdir = netdbdir
        self.confirmdays = confirmdays
        self.precision = precision

    def generate_netvalues(self):
        """ 从头计算净值表，包括全部日期（包含非交易日） 暂时未考虑融券情况 """
        digits = self.precision
        confirmdays = self.confirmdays
        w.start()
        with db_assistant(self.netdbdir) as netdb:
            conn_net = netdb.connection
            basedata = pd.read_sql('SELECT * FROM Net_Values_Base',conn_net)  #提取基础数据
            sorteddata = basedata.sort_values(['date'],ascending=[1])     # 将数据根据日期排序，防止有些估值表发送较晚，更新靠后的情况
            # 检查缺失交易日期，如果有缺失则只生成至缺失交易日前一（交易）日； 有交易日就应该有估值表，反之不然
            alldates = sorteddata['date']
            firstdate = alldates.values[0]   # 基础数据起始日 须确保基础数据中没有重复项
            lastdate = alldates.values[-1]   # 基础数据结束日
            tdays = w.tdays(firstdate,lastdate).Times  # 期间交易日
            trddays = pd.DataFrame([dt.datetime.strftime(t,'%Y%m%d') for t in tdays])
            #misstrd=~trddays.isin(dates.values)
            #misstrd=~trddays.isin(alldates)
            #trdmiss=trddays[misstrd.values]
            trdmiss = trddays[~trddays.isin(alldates)]  # 期间缺失的交易日
            if not trdmiss.empty:
                # 截止到第一个缺失交易日前的一个交易日
                #cutdate=dt.datetime.strftime(w.tdaysoffset(-1,trdmiss.values[0][0]).Times[0],'%Y%m%d')
                cutdate = dt.datetime.strftime(w.tdaysoffset(-1,trdmiss[0]).Times[0],'%Y%m%d')
                cutpos = alldates<=cutdate    # 需要提取的日期的位置
                sorteddata = sorteddata[cutpos]
            dates = sorteddata['date']
            datenum = dates.__len__()
            # 计算实际付费 出入金 -- 费用为每日计提，累计显示，因而是逐渐增加的，如果一次减小说明当日支付上一付费季度的费用
            fees = -(sorteddata.loc[:,['servfee','keepfee','mangfee','otherfee','earn']].diff())  #正常日计提 作差为正数，实际支付 作差为负数，取反则可以找到实际支付
            fees[fees<=0] = 0   # 将正常每日费用计提设为0
            fees.loc[0,:] = 0   # diff 导致第一行为NaN 需要填补为0
            paid=fees.sum(axis=1)  # 将每日各项费用加总，计算每日（账面）支付金额
            # bookearn=sorteddata['earn'].diff()
            # bookearn.iloc[0]=0
            # bookearn[bookearn<0]=0
            netreal=sorteddata['assetnet']/sorteddata['sharenum'] # 计算真实(单位)净值
            # 计算将业绩提成补回后的（累计）净值收益率
            bookearn = fees['earn']  # 账面业绩提成，实际支付时间可能有区别
            #cumret=((sorteddata['assetnet'].values[1:]+bookearn.values[1:])/sorteddata['assetnet'].values[:-1])*(sorteddata['sharenum'].values[:-1]/sorteddata['sharenum'].values[1:])-1
            net_addearn = (sorteddata['assetnet']+bookearn)/sorteddata['sharenum']
            cumret = net_addearn.values[1:]/netreal.values[:-1]
            cumret = np.row_stack([np.zeros([1,1]),np.reshape(cumret,[datenum-1,1])])
            netcum = np.cumprod(1+cumret)*netreal[0]  # 计算补回业绩提成后的（累计）单位净值,并确保初始值与单位净值初始值对齐

            # 在有申购赎回的时候需要采取平滑处理
            sharechg = sorteddata['sharenum'].diff() # 计算份额变动差异 >0 为由申购， <0 为有赎回，有可能申赎数量相同，但不影响金额
            sharechg[0] = 0
            # 和前一个数值相比, 确定 confirm date 交易确认日 (T+C) 的位置
            idxchg_TC = sharechg!=0 # type: pd.DataFrame
            #chgpos_TC=idxchg_TC[idxchg_TC.values].index
            chgpos_TC = idxchg_TC[idxchg_TC].index  # 变动位置的序号
            chgdate = dates[chgpos_TC] # 变动位置的对应的日期
            #opendt = [w.tdaysoffset(-confirmdays,c).Times[0] for c in chgdate] # 变动日向前confirmdays个交易日即为 开放日 in wind format
            #opendate=[dt.datetime.strftime(t,'%Y%m%d') for t in opendt]  # 开放日, T
            opendate = [w.tdaysoffset(-confirmdays,c).Times[0].strftime('%Y%m%d') for c in chgdate.values]
            openidx = dates.isin(opendate)  # 开放日位置
            inout = np.zeros_like(netreal)
            #inout[chgpos_TC] = np.round(netreal[openidx.values].values,digits)*sharechg[chgpos_TC].values
            inout[chgpos_TC] = np.round(netreal[openidx].values,digits)*sharechg[chgpos_TC].values  # 将单位净值round到指定位置，乘以分额变动计算出在开放日申购赎回的金额
            # 提取 开放日 到 确认日 期间的日期（TCm1）对应的位置，并在相应位置对应上申购赎回的金额
            inout2 = np.zeros_like(netreal)
            idxchg_TCm1 = np.zeros_like(netreal)
            opennum = 0
            opentot = opendate.__len__()
            for dumi in range(datenum):  # 将日期一个个与开放日比对
                if opennum>=opentot:      # 已经找到的开放日数量超过了所有 开放日数量，说明已经完成，可以退出了
                    break
                mydt = dates.values[dumi]
                if mydt>opendate[opennum] and mydt<chgdate[opennum]:
                    inout2[dumi] = inout[chgpos_TC[opennum]]
                    idxchg_TCm1[dumi] = 1
                elif mydt>=chgdate[opennum]:
                    opennum += 1
            # 计算平滑后的收益率
            rets = np.zeros_like(netreal)
            amtchg = np.zeros_like(netreal)
            comptot = sorteddata['assettot']-sorteddata['sell']  # 资产总额扣除应付赎回款，总资产不包含已经支付的费用，需要加回
            #numerator = (comptot.values+paid.values+idxchg_TCm1*inout2)[1:]  # 分子与确认日对齐
            #denominator = comptot.values[:-1]+(idxchg_TCm1*inout2+idxchg_TC.values*inout)[1:]
            numerator = (comptot.values + paid.values + inout2)[1:]  # 分子与确认日对齐
            denominator = comptot.values[:-1]+(inout2+inout)[1:]
            rets[1:] = numerator/denominator-1
            amtchg[1:] = comptot.values[1:]-comptot.values[:-1]+paid.values[1:]-inout[1:]  # 每日资金变动金额，补回费用，剔除申购赎回

            netvals = pd.DataFrame(np.column_stack([dates.values,netreal,netcum,np.cumprod(1+rets)*netreal[0],rets,amtchg,np.cumsum(amtchg)]),
                                 columns=['Date','NetSingle','NetCumulated','NetCompensated','Returns','AmtChg','AmtCumChg'])

            sql.to_sql(netvals,name='Net_Values',con=conn_net,if_exists='replace')
            print(' '.join(['%s : Netvalues updated from' %self.pname,firstdate,'to',dates.values[-1]]))
        w.close()


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
