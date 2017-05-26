
import numpy as np


class indicators:
    """ 根据净值 计算各种指标的类 """

    function_dict = {}  # 计算各个指标的函数的字典，key对应 indicator_list
    freq_dict = {'DAY':250,'D':250,'WEEK':52,'W':52,'MONTH':12,'M':12}

    def __init__(self,valueinfo,indicator_list,freq,rf = 0):
        self.rf = rf # 无风险利率
        self.freq = freq.upper()  # 日 周 月
        self.orders = indicator_list   # 需要计算的指标
        self.valueinfo = valueinfo
        self._netvals = np.array(valueinfo['netvals'])
        self._size = self._netvals.shape
        self._rets = self._netvals[1:,:]/self._netvals[:-1,:]-1
        # 常用指标 必须计算
        self._annret = self.calc_annret()
        self._annvol = self.calc_annvol()
        self._maxdd = self.calc_maxdd()
        # 是否需要计算 CAPM
        if ('JENSEN' in indicator_list) or ('TREYNOR' in indicator_list):
            [self.alpha,self.beta] = self.calc_CAPM()


    def take_orders(self):
        delivery = {}
        for ind in self.orders:
            if ind in ['maxdd','annret','annvol']:
                continue
            else:
                delivery[ind] = indicators.function_dict[ind]()

    def calc_annret(self):
        return np.mean(self._rets,axis=0)*indicators.freq_dict[self.freq]

    def calc_annvol(self):
        return np.std(self._rets,axis=0,ddof=1)*np.sqrt(indicators.freq_dict[self.freq])

    def calc_anndownvol(self):
        downrets=np.zeros_like(self._rets,dtype=np.float)
        idx = self._rets<0
        downrets[idx] = self._rets[idx]
        return np.std(downrets,axis=0,ddof=1)*np.sqrt(indicators.freq_dict[self.freq])

    def calc_maxdd(self):
        maxnet = np.zeros([1,self._size[1]])
        drawdowns = np.zeros_like(self._netvals,dtype=np.float)
        for dumi in range(self._size[0]):
            idx = self._netvals[dumi,:]>maxnet
            maxnet[:,idx[0]] = self._netvals[dumi,idx[0]]
            drawdowns[dumi,:] = self._netvals[dumi,:]/maxnet[:,:]-1
        return np.min(drawdowns,axis=0)

    def calc_sharpe(self):
        return (self._annret-self.rf)/self._annvol

    def calc_calmar(self):
        return (self._annret-self.rf)/self._maxdd

    def calc_sortino(self):
        return (self._annret-self.rf)/self.calc_anndownvol()

    def calc_jensen(self):
        pass

    def calc_treynor(self,benchmark):
        benchnet = np.array(self.valueinfo.get(benchmark))
        if not benchnet:
            raise Exception('No benchmark is provided, can not calc Treynor ratio !')
        benchret = benchnet[1:,:]/benchnet[:-1,:]-1
        ###　未完成　需确定beta 计算回归是否需要截距

    def calc_winloss_recorders(self):
        wins = np.ones([1,self._size[1]])
        loss = np.ones([1,self._size[1]])
        maxwin = np.ones([1,self._size[1]])
        maxlos = np.ones([1,self._size[1]])
        for dumi in range(self._size[0]):
            if dumi>0 and dumi<self._size[0]-1:
                winstop = np.all([self._rets[dumi-1,:]>0 , self._rets[dumi,:]<=0],axis=0)
                losstop = np.all([self._rets[dumi-1,:]<0 , self._rets[dumi,:]>=0],axis=0)
                wins[:,winstop] = 1  # 每次停止后需要重置为1
                loss[:,losstop] = 1  # 每次停止后需要重置为1
                wins = wins+np.all([self._rets[dumi,:]>0 , self._rets[dumi-1,:]>0],axis=0)*1
                loss = loss+np.all([self._rets[dumi,:]<0 , self._rets[dumi-1,:]<0],axis=0)*1
                newwin = wins>maxwin
                newlos = loss>maxlos
                maxwin[:,newwin[0]] = wins[:,newwin[0]]
                maxlos[:,newlos[0]] = loss[:,newlos[0]]
        return {'maxwinsnum':maxwin[0,:] , 'maxlossnum':maxlos[0,:]}

    def calc_CAPM(self):
        pass