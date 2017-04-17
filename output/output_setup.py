from src.Baiquan1 import *
from src.Jinqu1 import *
from src.Huijin1 import *
from src.Baiquan2 import *
from src.Guodao2 import *
import pandas as pd



def GetNetValues(products,outdir,startdate=False,enddate=False,freq='week',mktidx=False,indicators=False,plots=False):

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



def get_configure(confdir):
    result={}
    with open(confdir,'r') as conf:
        while True:
            ln=conf.readline()
            if len(ln)==0:
                break
            else:
                notepos=ln.find('#')
                newln=ln[0:notepos]
                contents=newln.split('=')
                if len(contents)>=3:
                    raise Exception('每行只能设置一个参数')

                title=contents[0].strip().lower()
                if len(title)==0:
                    continue

                cont=contents[1].strip().lower()
                if cont in ['true','false']:
                    cont= cont=='true'
                elif title in ['needmktidx']:   # 除了ture false 以外的答案
                    raise Exception('错误类型 ： needmktidx')

                if (title not in result.keys()):
                    result[title]=[cont]
                else:
                    result[title].append(cont)
    return result