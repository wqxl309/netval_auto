
from src.base_class import *

class Jinqu1_db(db):   # 进取和百泉1号相似较大
    def __init__(self,netvaldir=r'E:\netval_auto\netvalue\NetvalJQ1.db'):
        dbdirJQ1=r'.\database\Jinqu1.db'
        filedirJQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号'+'\\'
        flistdirJQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号\list.txt'
        super(Jinqu1_db,self).__init__(dbdirJQ1,filedirJQ1,flistdirJQ1,netvaldir)
        self.productname='JinQu1'
        self.mandarine=u'百泉进取一号'
        self.ipodate=dt.date(2016,11,3)
        self.confirmdays=2
        self.net_digits=4

    def get_tablename(self,tbdir):
        strings=tbdir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0][6:]

    def get_tbtitles(self,tbdir):
        data=xlrd.open_workbook(tbdir)
        table = data.sheets()[0]          #通过索引顺序获取
        #table2 = data.sheet_by_index(0) #通过索引顺序获取
        #table3 = data.sheet_by_name(u'Sheet1')#通过名称获取
        for dumi in range(table.nrows):
            if '科目代码' in table.row_values(dumi):   # 识别标题行 避免采用第二行有 科目代码 的标题
                titles=list(table.row_values(dumi))
                titlenum=len(titles)
                for dumj in range(titlenum):
                    titles[dumj]=(titles[dumj]).replace('-','')   # 删除标题中的 “ - ”
                    if titles[dumj]=='':   # 此时dumj-1 对应列应为 市值、估值增值 等
                        titles[dumj]=titles[dumj-1]+'本币'
                        titles[dumj-1]+='原币'
                return titles

    def update_netval_data(self,codedict=None):
        codedict={'sharenum':'实收资本','assettot':'资产合计','debttot':'负债合计','assetnet':'资产净值','servfee':'2211.01',
                  'keepfee':'2207.01','mangfee':'2206.01','earn':'2206.02','buy':'1207.01','sell':'2203.01'}
        super(Jinqu1_db,self).update_netval_data(codedict)