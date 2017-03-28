from src.base_class import *

class Guodao2_db(db):
    def __init__(self,dbdir,filedir,flistdir,netvaldir):
        self.ipodate=dt.date(2016,12,1)
        super(Guodao2_db,self).__init__(dbdir,filedir,flistdir,netvaldir)

    def get_tablename(self,tbdir):
        strings=tbdir.split('\\')
        tempname=strings[-1]
        tempname2=tempname.split('.')[0]
        tempname3=tempname2.split('_')
        return tempname3[1]+tempname3[4]

    def get_tbtitles(self,tbdir):
        data=xlrd.open_workbook(tbdir)
        table = data.sheets()[0]          #通过索引顺序获取
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
        codedict={'sharenum':'实收资本','assettot':'资产合计','debttot':'负债合计','assetnet':'资产净值','servfee':'2208.02',
                  'keepfee':'2207.01','mangfee':'2206.01','earn':'2206.02','buy':'1207.01','sell':'2203.01'}
        super(Guodao2_db,self).update_netval_data(codedict)