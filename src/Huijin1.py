
from src.Baiquan1 import *

class Huijin1_db(Baiquan1_db):
    def __init__(self,dbdir,filedir,flistdir,updtlstdir,netvaldir):
        super(Baiquan1_db,self).__init__(dbdir,filedir,flistdir,updtlstdir,netvaldir)

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
