from src.base_class import *


class Baiquan_strategy1_db(db):
    def __init__(self,netvaldir=r'E:\netval_auto\netvalue\NetvalBQ_strategy1.db'):
        dbdir=r'.\database\Baiquan_strategy1.db'
        filedir=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉多策略一号'+'\\'
        flistdir=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉多策略一号\list.txt'
        super(Baiquan_strategy1_db,self).__init__(dbdir,filedir,flistdir,netvaldir)
        self.productname='BaiQuanStrat1'
        self.mandarine=u'百泉多策略一号'
        self.ipodate=dt.date(2017,4,7)
        self.confirmdays=2
        self.net_digits=3

    def get_tablename(self,tbdir):
        strings=tbdir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0]

    def get_tbtitles(self,tbdir):
        data=xlrd.open_workbook(tbdir)
        table = data.sheets()[0]          #通过索引顺序获取
        for dumi in range(table.nrows):
            if '科目代码' in table.row_values(dumi):   # 识别标题行 避免采用第二行有 科目代码 的标题
                titles=list(table.row_values(dumi))
                titlenum=len(titles)
                for dumj in range(titlenum):
                    titles[dumj]=(titles[dumj]).replace('-','')   # 删除标题中的 “ - ”
                    titles[dumj]=(titles[dumj]).replace('%','')   # 删除标题中的 “ % ”
                    if titles[dumj]=='':   # 此时dumj-1 对应列应为 市值、估值增值 等
                        titles[dumj]=titles[dumj-1]+'本币'
                        titles[dumj-1]+='原币'
                return titles

    def update_netval_data(self,codedict=None):
        # 需确认个字段， 以及个字段数值是否在 “成本本币” 栏目下
        codedict={'sharenum':'实收资本金额','assettot':'资产类合计:','debttot':'负债类合计:','assetnet':'基金资产净值:','servfee':'220501',
                  'keepfee':'220701','mangfee':'2206.01','earn':'2206.02','buy':'1207.01','sell':'2203.01'}
        super(Baiquan_strategy1_db,self).update_netval_data(codedict)