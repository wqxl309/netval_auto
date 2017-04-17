
from output.output_setup import *

if __name__=='__main__':
        products={  u'百泉一号'     :'Yes',
                    u'百泉进取一号' :'Yes',
                    u'百泉汇瑾一号' :'Yes',
                    u'百泉二号'     :'No'}
        startdate = False # '20161230'                               # 设为 False 将以最早的日期为开始
        enddate = False                                              # 设为 False 将以最近的时期为结束
        mktidx=False                                                 # 是否输出同步指数
        freq = 'week'                                                # 净值频率 包含日度--day, 周度--week 以及 月度 -- month
        outdir=r'C:\Users\Jiapeng\Desktop' + '\\'+ freq + '.xlsx'          # 输出路径
        indicator=r'C:\Users\Jiapeng\Desktop' + '\\'+ freq + '_indicators.xlsx'
        GetNetValues(products=products,outdir=outdir,startdate=startdate,enddate=enddate,freq=freq,indicators=indicator,plots=False)