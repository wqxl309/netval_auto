
from output.output_setup import *

if __name__=='__main__':

    configure=get_configure('./configure.txt')
    confkeys=configure.keys()

    products={}
    prodlist=configure['productadd']
    for p in prodlist:
        products[p]='Yes'

    if 'startdate' in confkeys:
        startdate = configure['startdate'][0]                        # 设为 False 将以最早的日期为开始
    else:
        startdate= False
    if 'enddate' in confkeys:
        enddate =  configure['enddate'][0]                                  # 设为 False 将以最近的时期为结束
    else:
        enddate = False

    if 'needmktidx' in confkeys and configure['needmktidx'][0]:
        if 'mktidxadd' not in confkeys:
            raise Exception(u'未指定所需指数代码')
        mktidx = configure['mktidxadd']                                  # 是否输出同步指数
    else:
        mktidx=False

    if 'frequency' in confkeys:
        freq =  configure['frequency'][0]                          # 净值频率 包含日度--day, 周度--week 以及 月度 -- month
        filename=freq
    else:
        raise Exception(u'未设定数据频率')

    outdir=r'.\输出结果' + '\\'+ filename + '.xlsx'              # 输出路径
    indicator=r'.\输出结果' + '\\'+ filename + '_指标.xlsx'

    GetNetValues(products=products,outdir=outdir,startdate=startdate,enddate=enddate,freq=freq,mktidx=mktidx,indicators=indicator,plots=False)
