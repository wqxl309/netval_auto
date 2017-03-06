

import sqlite3
import xlrd
import os
import time

__metaclass__ = type

class db:

    def __init__(self,dbdir,tabledir):
        self.dbdir=dbdir
        self.tabledir=tabledir

    def dbexist(self):
        # 若db不存在则不能写入table,db创建在类外实现
        return os.path.exists(self.dbdir)

    def tbexist(self):
        # table 不存在则不能调用 write_table
        conn=sqlite3.connect(self.dbdir)
        c=conn.cursor()
        exeline='SELECT name FROM sqlite_master WHERE type=\'table\' '
        c.execute(exeline)
        alltables=c.fetchall()
        tbname=(self.get_tablename(),)
        conn.close()
        return tbname in alltables

    def get_tablename(self):
        pass

    def get_tbtitles(self):
        pass

    def write_table(self):
        # 写入前数据库必须存在
        # 写入失败则删除表格
        pass



class Baiquan1_db(db):
    def __init__(self,dbdir,tabledir):
        super(Baiquan1_db,self).__init__(dbdir,tabledir)

    def get_tablename(self):
        strings=self.tabledir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0][5:]

    def get_tbtitles(self):
        data=xlrd.open_workbook(self.tabledir)
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

    def write_table(self):
        hasdb=self.dbexist()  # 写入前数据库必须存在，数据库的建立在方法外实现
        if not hasdb:
            print('Database does NOT exist, no update!')
            return False
        hastb=self.tbexist()
        if hastb:
            print('Table already exists, no update!')
            return False
        # 寻找起始行
        data=xlrd.open_workbook(self.tabledir)
        table = data.sheets()[0]
        startline=0
        for dumi in range(table.nrows):
            try:
                # 检查首个元素类型，如果能转换为数值则为应该记录的行的起始行
                int(table.row_values(dumi)[0])
            except ValueError:
                if table.row_values(dumi)[0]=='1级科目':
                    startline=dumi
                    break
                else:
                    continue
            else:
                startline=dumi
                break
        # 开始写入table
        conn=sqlite3.connect(self.dbdir)
        c=conn.cursor()
        tablename=self.get_tablename()
        titles=self.get_tbtitles()
        titlenum=len(titles)
        titletrans= ('%s,'*titlenum)[0:(3*titlenum-1)] % tuple(titles)
        exeline=''.join(['CREATE TABLE ',tablename,' (',titletrans,') '])
        c.execute(exeline)
        print('Table '.join([tablename,' created!']))

        try:
            for dumi in range(startline,table.nrows):
                exeline=''.join(['INSERT INTO ',tablename,' VALUES (',('?,'*titlenum)[0:(2*titlenum-1)],')'])
                c.execute(exeline , tuple(table.row_values(dumi)))
                conn.commit()
        except:   # 无论任何原因导致写入table失败，则都要删除未写完的table
            print('Writing table failed ! ')
            conn.execute('DROP TABLE '.join(tablename))
            raise
        else:
            print('Table '.join([tablename,' updated !']))
        finally:
            conn.close()



class Jinqu1_db(Baiquan1_db):   # 进取和百泉1号相似较大
    def __init__(self,dbdir,tabledir,filedir,flistdir):
        super(Jinqu1_db,self).__init__(dbdir,tabledir)

    def get_tablename(self):
        strings=self.tabledir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0][6:]


class Huijin1_db(Baiquan1_db):
    def __init__(self,dbdir,tabledir,filedir,flistdir):
        super(Baiquan1_db,self).__init__(dbdir,tabledir)

    def get_tablename(self):
        strings=self.tabledir.split('\\')
        tempname=strings[-1]
        return tempname.split('.')[0][7:]

    def get_tbtitles(self):
        data=xlrd.open_workbook(self.tabledir)
        table = data.sheets()[0]          #通过索引顺序获取
        for dumi in range(table.nrows):
            if '科目代码' in table.row_values(dumi):   # 识别标题行 避免采用第二行有 科目代码 的标题
                titles=list(table.row_values(dumi))
                titlenum=len(titles)
                for dumj in range(titlenum):
                    titles[dumj]=(titles[dumj]).replace('%','')   # 删除标题中的 “ % ”
                return titles
