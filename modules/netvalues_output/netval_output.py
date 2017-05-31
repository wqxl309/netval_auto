
import datetime as dt

import pandas as pd

from remotewind import w
from modules.database_assistant.database_assistant import *

class netval_output:

    def __init__(self,netdbdir,ipodate):
        self.netdbdir = netdbdir
        self.ipodate = ipodate

    def take_netvalues(self,startdate=False,enddate=False,freq='DAY',outputdir=False):
        """
        提取指定日期内的产品净值
        如果未提供日期，则开始日期设置为ipodae，结束日期设置为 今日
        """
        w.start()
        with db_assistant(self.netdbdir) as netdb:
            conn_net = netdb.connection
            if not startdate:
                startdate = self.ipodate
            if not enddate:
                enddate = dt.datetime.today().strftime('%Y%m%d')
            # 从净值数据库提取日度数据
            data = pd.read_sql(''.join(['SELECT * FROM Net_Values WHERE date >=',startdate,' AND date<=',enddate]),conn_net)
            dates = data['Date']
            head = dates.values[0]    # 所取数据的最早日期
            tail = dates.values[-1]   # 所取数据的最晚日期
            if freq.upper()=='WEEK':
                period='W'
            elif freq.upper()=='MONTH':
                period = 'M'
            else:
                period = 'D'
            ttimes = w.tdays(head,tail,'Period='+period).Times  # head tail 所对应的日期有可能不是交易日
            tperiods = [dt.datetime.strftime(t,'%Y%m%d') for t in ttimes]
            #needextra = False
            if (tperiods[0] > head): # 使用周度、月度数据的情况下，确保第一个值为所取数据第一个 交易日
                tmptimes = w.tdays(head,tperiods[0],'Period=D').Times
                head = dt.datetime.strftime(tmptimes[0],'%Y%m%d')  # 将head设置为所提取区间的第一个交易日
            #    needextra = True
                tperiods.insert(0,head)
            trdidx = dates.isin(tperiods)
            trddata = data[trdidx]
            trddata = trddata.drop('index',axis=1)
        return trddata

    def get_configure(self,confdir):
        result = {}
        with open(confdir,'r') as conf:
            while True:
                ln = conf.readline()
                if len(ln)==0:  # 遇到空行即停止 不包括唯一含有 /n 的行
                    break
                else:
                    notepos = ln.find('#')   # 注释标号后的内容都将被忽略
                    newln = ln[0:notepos]
                    contents = newln.split('=')
                    if len(contents)>=3:
                        raise Exception('每行只能设置一个参数')
                    elif len(contents)==1:   # 一行只有一个值，没有=将被忽略
                        continue
                    title = contents[0].strip().lower()
                    if len(title)==0:
                        continue
                    cont = contents[1].strip().lower()
                    if cont in ['true','false']:
                        cont = cont=='true'
                    elif title in ['needmktidx']:   # 除了ture false 以外的答案
                        raise Exception('错误类型 ： needmktidx')
                    if (title not in result.keys()):  #同一个Key 下的参数添加到列表里面
                        result[title] = [cont]
                    else:
                        result[title].append(cont)
        return result


    def generate_output(self,products,outdir,startdate=False,enddate=False,freq='week',mktidx=False,indicators=False,plots=False):
        proddict={u'百泉一号':['NetvalBQ1.db',Baiquan1_db],
                  u'百泉进取一号':['NetvalJQ1.db',Jinqu1_db],
                  u'百泉汇瑾一号':['NetvalHJ1.db',Huijin1_db],
                  u'百泉二号':['NetvalBQ2.db',Baiquan2_db],
                  u'国道砺石二号':['NetvalGD2.db',Guodao2_db]
                  }

        needind=False
        if indicators:
            needind=True

        dbfolder='\\\JIAPENG-PC\\netvalue\\'
        inkeys=products.keys()
        output_results={}
        for k in proddict.keys():
            if k in inkeys and products[k].strip().lower() == 'yes':
                netvaldir=dbfolder+proddict[k][0]
                obj=proddict[k][1](netvaldir)
                tb=obj.take_netvalue(startdate=startdate,enddate=enddate,freq=freq,indicators=needind,mktidx=mktidx,plots=plots,outputdir='return data')
                output_results[obj.mandarine]=tb

        writer=pd.ExcelWriter(outdir)
        if needind:
            writer_ind=pd.ExcelWriter(indicators)
        for tbk in output_results.keys():
            output_results[tbk]['outdata'].to_excel(writer,sheet_name=tbk,index=False)
            if needind:
                temp=output_results[tbk]['indicators']
                title=temp.pop('ValueType')
                inddata=pd.DataFrame.from_dict(temp,orient='index')
                inddata.columns=title
                inddata.sort_index()
                inddata.to_excel(writer_ind,sheet_name=tbk,index=True)
        writer.save()
        if needind:
            writer_ind.save()


t = netval_output('',r'E:\netval_auto\configure.txt')
a = t.get_configure(r'E:\netval_auto\configure.txt')
print(a)