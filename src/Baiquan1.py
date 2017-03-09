
from src.base_class import *


class Baiquan1_db(db):
    def __init__(self,dbdir,filedir,flistdir,updtlstdir,netvaldir):
        super(Baiquan1_db,self).__init__(dbdir,filedir,flistdir,updtlstdir,netvaldir)

    def get_tablename(self,tbdir):
        strings=tbdir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0][5:]

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
