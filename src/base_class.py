import sqlite3
import xlrd
import os

__metaclass__ = type

class db:

    def __init__(self,dbdir,filedir,flistdir,updtlstdir,netvaldir):
        if not os.path.exists(flistdir):
            os.system('type null > '+filedir)

        if not os.path.exists(updtlstdir):
            os.system('type null > '+updtlstdir)

        self.dbdir=dbdir
        self.filedir=filedir
        self.flistdir=flistdir
        self.updtlstdir=updtlstdir
        self.netvaldir=netvaldir


    def dbexist(self):
        # 若db不存在则不能写入table,db创建在类外实现
        return os.path.exists(self.dbdir)

    def get_tablename(self,tbdir):
        pass

    def get_tbtitles(self,tbdir):
        pass

    def tbexist(self,tbdir):
        # table 不存在则不能调用 write_table
        conn=sqlite3.connect(self.dbdir)
        c=conn.cursor()
        exeline='SELECT name FROM sqlite_master WHERE type=\'table\' '
        c.execute(exeline)
        alltables=c.fetchall()
        tbname=(self.get_tablename(tbdir),)
        conn.close()
        return tbname in alltables

    def write_table(self,tbdir):
        # 写入前数据库必须存在
        # 写入失败则删除表格
        hasdb=self.dbexist()  # 写入前数据库必须存在，数据库的建立在方法外实现
        if not hasdb:
            print('Database does NOT exist, no update!')
            return False
        hastb=self.tbexist(tbdir)
        tbname=self.get_tablename(tbdir)
        if hastb:
            print(tbname+' already exists, no update!')
            return False
        # 寻找起始行
        data=xlrd.open_workbook(tbdir)
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
        tablename=self.get_tablename(tbdir)
        titles=self.get_tbtitles(tbdir)
        titlenum=len(titles)
        titlestr=[]
        for tl in titles:
            if tl in ('科目代码', '科目名称', '币种','科目级别'):
                titlestr.append(tl+' TEXT,')
            else:
                titlestr.append(tl+' REAL,')
        titletrans=''.join(titlestr)[:-1]
        #titletrans= ('%s,'*titlenum)[0:(3*titlenum-1)] % tuple(titles)
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


    def update_tables(self):
        # 检查是否有新文件，如有则更新,并把更新后的文件写入到 flistdir 中
        # 检查新增加的文件
        filelist_w=open(self.flistdir,'a+')
        filelist_r=open(self.flistdir)
        try:
            files=filelist_r.readlines()
            savedtbs=set([tb.strip() for tb in files])
            currntbs=set(os.listdir(self.filedir))
            newaddtbs=sorted(list(currntbs.difference(savedtbs)))
            try:
                newaddtbs.remove('list.txt')
            except ValueError:
                pass
            # 写入新增加的文件
            sqlite3.connect(self.dbdir)
            for dumi in range(len(newaddtbs)):
                tabledir=self.filedir+newaddtbs[dumi]
                self.write_table(tabledir)
                filelist_w.write(newaddtbs[dumi]+'\n')   # 更新 list
        except ValueError:
            print('Error in updating db')
            raise
        finally:
            filelist_r.close()
            filelist_w.close()


    def get_updtlst(self):   # 提取需要更新的表
        if not self.dbexist():
            print('Data db does NOT exist!')
            return
        conn_db=sqlite3.connect(self.dbdir)
        cd=conn_db.cursor()
        try:
            dbtbs=cd.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
        except:
            raise
        finally:
            conn_db.close()
        netfile=open(self.updtlstdir)
        try:
            nettbs=netfile.readlines()
        except:
            raise
        finally:
            netfile.close()
        dbtables=[]
        [dbtables.append(val[0]) for val in dbtbs]
        nettables=[]
        [nettables.append(val.strip()) for val in nettbs]
        difftb=sorted(list(set(dbtables).difference(set(nettables))))
        return difftb


    def update_netval(self):
        updtlst=self.get_updtlst()
        if len(updtlst)==0:
            print('No new tables to update !')
        conn_netval=sqlite3.connect(self.netvaldir)
        conn_db=sqlite3.connect(self.dbdir)
        conn_db.row_factory=sqlite3.Row
        cn=conn_netval.cursor()
        cd=conn_db.cursor()
        netfile=open(self.updtlstdir,'a+')
        try:
            nettbs=cn.execute(' SELECT name FROM sqlite_master WHERE type=\'table\' ').fetchall()
            if not ('Net_Values',) in nettbs:
                print('Net_Values table created')
                cn.execute('CREATE TABLE Net_Values (date,sharenum,assettot,debttot,assetnet,servfee,keepfee,mangfee,earn,buy,sell)')

            for dumi in range(len(updtlst)):
                tb=updtlst[dumi]
                cols=cd.execute('SELECT * FROM '+tb).fetchone().keys()
                if '市值本币' in cols:
                    valcol='市值本币'
                else:
                    valcol='市值'

                print(tb)

                exeline1=''.join(['SELECT ',valcol,' FROM ',tb ,' WHERE 科目代码 IN (\'实收资本\',\'资产合计\',\'负债合计\',\'资产净值\')'])
                netinfo=cd.execute(exeline1).fetchall()
                sharenum=netinfo[0][0]
                assettot=netinfo[1][0]
                debttot =netinfo[2][0]
                assetnet=netinfo[3][0]

                exeline2=''.join(['SELECT ',valcol,' FROM ',tb ,' WHERE 科目代码 IN (\'2206.14\',\'2207.01\')'])  #行政服务费，托管费
                othinfo=cd.execute(exeline2).fetchall()
                servfee=othinfo[0][0]
                keepfee=othinfo[1][0]

                exeline3=''.join(['SELECT ',valcol,' FROM ',tb ,' WHERE 科目代码 IN (\'2206.01\')'])  # 管理费, 没有则为0
                mfeinfo=cd.execute(exeline3).fetchall()
                if len(mfeinfo)==0:
                    mangfee=0
                else:
                    mangfee=mfeinfo[0][0]

                exeline4=''.join(['SELECT ',valcol,' FROM ',tb ,' WHERE 科目代码 IN (\'2206.02\')']) # 业绩报酬， 没有则为0
                earninfo=cd.execute(exeline4).fetchall()
                if len(earninfo)==0:
                    earn=0
                else:
                    earn=earninfo[0][0]

                exeline5=''.join(['SELECT ',valcol,' FROM ',tb ,' WHERE 科目代码 IN (\'1207.01\')']) # 应收申购款， 没有则为0
                buyinfo=cd.execute(exeline5).fetchall()
                if len(buyinfo)==0:
                    buy=0
                else:
                    buy=buyinfo[0][0]

                exeline6=''.join(['SELECT ',valcol,' FROM ',tb ,' WHERE 科目代码 IN (\'2203.01\')']) # 应收赎回款， 没有则为0
                sellinfo=cd.execute(exeline6).fetchall()
                if len(sellinfo)==0:
                    sell=0
                else:
                    sell=sellinfo[0][0]

                cn.execute("INSERT INTO Net_Values VALUES (?,?,?,?,?,?,?,?,?,?,?)" , (tb[-8:],sharenum,assettot,debttot,assetnet,servfee,keepfee,mangfee,earn,buy,sell) )
                conn_netval.commit()

                print(tb[-8:],sharenum,assettot,debttot,assetnet,servfee,keepfee,mangfee,earn,buy,sell)
                
                netfile.write(tb+'\n')
                print( tb+' update finished ! ' )

        except:
            raise
        finally:
            conn_netval.close()
            conn_db.close()
            netfile.close()
