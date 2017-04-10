
from src.base_class import *

class Huijin1_db(db):
    def __init__(self,netvaldir=r'E:\netval_auto\netvalue\NetvalHJ1.db'):
        dbdirHJ1=r'E:\netval_auto\database\Huijin1.db'
        filedirHJ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号'+'\\'
        flistdirHJ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号\list.txt'
        super(Huijin1_db,self).__init__(dbdirHJ1,filedirHJ1,flistdirHJ1,netvaldir)
        self.productname='HuiJin1'
        self.mandarine=u'百泉汇瑾一号'
        self.ipodate=dt.date(2016,11,24)
        self.confirmdays=2
        self.net_digits=3

    def get_tablename(self,tbdir):
        strings=tbdir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0][7:]

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
        codedict={'sharenum':'实收资本','assettot':'资产类合计:','debttot':'负债类合计:','assetnet':'基金资产净值:','servfee':'220501',
                  'keepfee':'220701','mangfee':'220601','earn':'220602','buy':'120701','sell':'220301'}
        super(Huijin1_db,self).update_netval_data(codedict)