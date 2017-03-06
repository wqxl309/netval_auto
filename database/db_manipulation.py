
import sqlite3
import os
import xlrd

def connect_to_db(dbdir,repttype):
    """ dbdir:
        repttype: False report error if no dbdir exist
                  True create a new db if no dbdir exist """
    hasdb=os.path.exists(dbdir)
    if hasdb:
        conn=sqlite3.connect(dbdir)
        return conn
    else:
        if repttype:
            conn=sqlite3.connect(dbdir)
            return conn
        else:
            raise Exception('No such file : '.join(dbdir))


def create_table_db(dbdir,tabledir,tablename,repttype):
    """  如果table不存在则创建并写入table,若写入中途失败则删除未完成的table;若存在则不再写入
        自动识别 titile
        dbdir:
        tabledir:
        titles: provide titles used by the db,should be a list or tuple of strings
        repttype: False report error if no dbdir exist
                  True create a new db if no dbdir exist """
    conn=connect_to_db(dbdir,repttype)
    c=conn.cursor()

    data=xlrd.open_workbook(tabledir)
    table = data.sheets()[0]          #通过索引顺序获取
    #table2 = data.sheet_by_index(0) #通过索引顺序获取
    #table3 = data.sheet_by_name(u'Sheet1')#通过名称获取

    startwrite=False
    errorlines=0
    for dumi in range(table.nrows):
        if '科目代码' in table.row_values(dumi) and (not startwrite):   # 识别标题行 避免采用第二行有 科目代码 的标题
            titles=list(table.row_values(dumi))
            titlenum=len(titles)
            for dumj in range(titlenum):
                titles[dumj]=(titles[dumj]).replace('-','')
                if titles[dumj]=='':
                    titles[dumj]=titles[dumj-1]+'本币'
                    titles[dumj-1]+='原币'

            titletrans= ('%s,'*titlenum)[0:(3*titlenum-1)] % tuple(titles)
            exeline=''.join(['CREATE TABLE ',tablename,' (',titletrans,') '])
            try:
                c.execute(exeline)
                print('Table '.join([tablename,' created!']))
            except sqlite3.OperationalError as e:  # table 已经存在, 则不再更新
                if 'already exist' in str(e):
                    print('Table '+tablename+' already exists,no update')
                    return
                else:
                    raise(e)
            startwrite=True

        elif startwrite:   #开始写入表格
            try:
                exeline=''.join(['INSERT INTO ',tablename,' VALUES (',('?,'*titlenum)[0:(2*titlenum-1)],')'])
                c.execute(exeline , tuple(table.row_values(dumi)))
                conn.commit()
            except:
                print('Error writing table ### %s ### in line NO.%f' % tablename,dumi )
                errorlines+=1
        else:
            continue

    if startwrite and errorlines==0:
        print('Table '+tablename+' updated successfully!')
    elif startwrite and errorlines>0:
        print('Table '+tablename+' updated with %d lines go wrong!' %errorlines)
    else:
        print('Table '+tablename+' created but no lines updated, title NOT found!')


