import numpy as np
import xlrd
import xlwt


def calc_indicators(netvals):
    """ returns order: mean,std,downstd,winrate,maxdd,maxwins,maxlosses"""
    netvals=np.array(netvals)
    size=netvals.shape
    results={}
    rets=netvals[1:,:]/netvals[:-1,:]-1
    downrets=np.zeros_like(rets,dtype=np.float)
    idx=rets<0
    downrets[idx]=rets[idx]
    results['mean']=np.mean(rets,axis=0)
    results['std']=np.std(rets,axis=0,ddof=1)
    results['downstd']=np.std(downrets,axis=0,ddof=1)
    results['winrate']=np.sum(rets>0,axis=0)/size[0]
    # 计算最大回撤，最大连续增长/下跌数量
    maxnet=np.zeros([1,size[1]])
    wins=np.ones([1,size[1]])
    loss=np.ones([1,size[1]])
    maxwin=np.ones([1,size[1]])
    maxlos=np.ones([1,size[1]])
    drawdowns=np.zeros_like(netvals,dtype=np.float)
    for dumi in range(size[0]):
        idx=netvals[dumi,:]>maxnet
        maxnet[:,idx[0]]=netvals[dumi,idx[0]]
        drawdowns[dumi,:]=netvals[dumi,:]/maxnet[:,:]-1
        if dumi>0 and dumi<size[0]-1:
            winstop=np.all([rets[dumi-1,:]>0 , rets[dumi,:]<=0],axis=0)
            losstop=np.all([rets[dumi-1,:]<0 , rets[dumi,:]>=0],axis=0)
            wins[:,winstop]=1
            loss[:,losstop]=1
            wins=wins+np.all([rets[dumi,:]>0 , rets[dumi-1,:]>0],axis=0)*1
            loss=loss+np.all([rets[dumi,:]<0 , rets[dumi-1,:]<0],axis=0)*1
            newwin=wins>maxwin
            newlos=loss>maxlos
            maxwin[:,newwin[0]]=wins[:,newwin[0]]
            maxlos[:,newlos[0]]=loss[:,newlos[0]]
    results['maxdd']=np.min(drawdowns,axis=0)
    results['maxwinsnum']=maxwin[0,:]
    results['maxlossnum']=maxlos[0,:]
    return results


def sqlite_to_excel(filedir,sheetname,overwirte=True):
    """ write sqlite3 database to excel worksheet:
        if no such file then create one
        if no such sheet then create one """
    file=xlrd.open_workbook(filedir)


if __name__=='__main__':
    outdir=r'C:\Users\Jiapeng\Desktop\BQ1.xlsx'
    data = xlrd.open_workbook('outdir')
    try:
        table = data.sheet_by_name(u'b')
    except xlrd.biffh.XLRDError as e:
        print(e)
