
from src.base_class import *

class Baiquan2_db(db):
    def __init__(self,netvaldir=r'E:\netval_auto\netvalue\Netval.db'):
        dbdirBQ2=r'E:\netval_auto\database\Baiquan2.db'
        filedirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号'+'\\'
        flistdirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号\list.txt'
        super(Baiquan2_db,self).__init__(dbdirBQ2,filedirBQ2,flistdirBQ2,netvaldir)
        self.productname='BaiQuan2'
        self.mandarine=u'百泉二号'
        self.ipodate=dt.date(2016,12,30)
        self.confirmdays=2
        self.net_digits=4

    def get_tablename(self,tbdir):
        strings=tbdir.split('\\')
        tempname=strings[-1]
        tbdate=tempname.split('.')[0][-10:]
        tbdate=tbdate.replace('-','')
        return '百泉二号私募证券投资基金'+tbdate

    def get_tbtitles(self,tbdir):
        data=xlrd.open_workbook(tbdir)
        table = data.sheets()[0]          #通过索引顺序获取
        for dumi in range(table.nrows):
            if '科目代码' in table.row_values(dumi):   # 识别标题行 避免采用第二行有 科目代码 的标题
                titles=list(table.row_values(dumi))
                titlenum=len(titles)
                for dumj in range(titlenum):
                    titles[dumj]=(titles[dumj]).replace('%','')   # 删除标题中的 “ % ”
                return titles

    def update_netval_data(self,codedict=None):
        codedict={'sharenum':'实收资本','assettot':'资产类合计:','debttot':'负债类合计:','assetnet':'基金资产净值:','servfee':'2205',
                  'keepfee':'2207','mangfee':'2206','earn':'220602','buy':'120701','sell':'220301'}
        super(Baiquan2_db,self).update_netval_data(codedict)