

from src.Baiquan1 import *
from src.Jinqu1 import *
from src.Huijin1 import *
from src.Baiquan2 import *
from src.Guodao2 import *

dbdirJQ=r'E:\netval_auto\database\Jinqu1.db'
filedirJQ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号'+'\\'
flistdirJQ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号\list.txt'
netvaldirJQ=r'E:\netval_auto\netvalue\NetvalJQ1.db'

dbdirHJ=r'E:\netval_auto\database\Huijin1.db'
filedirHJ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号'+'\\'
flistdirHJ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号\list.txt'
netvaldirHJ=r'E:\netval_auto\netvalue\NetvalHJ1.db'

dbdirBQ1=r'E:\netval_auto\database\Baiquan1.db'
filedirBQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉一号'+'\\'
flistdirBQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉一号\list.txt'
netvaldirBQ1=r'E:\netval_auto\netvalue\NetvalBQ1.db'

dbdirBQ2=r'E:\netval_auto\database\Baiquan2.db'
filedirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号'+'\\'
flistdirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号\list.txt'
netvaldirBQ2=r'E:\netval_auto\netvalue\NetvalBQ2.db'

dbdirGD2=r'E:\netval_auto\database\Guodao2.db'
filedirGD2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 国道砺石二号'+'\\'
flistdirGD2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 国道砺石二号\list.txt'
netvaldirGD2=r'E:\netval_auto\netvalue\NetvalGD2.db'

if __name__=='__main__':
    obj=Baiquan1_db(dbdirBQ1,filedirBQ1,flistdirBQ1,netvaldirBQ1)
    # obj=Jinqu1_db(dbdirJQ,filedirJQ,flistdirJQ,netvaldirJQ)
    # obj=Huijin1_db(dbdirHJ,filedirHJ,flistdirHJ,netvaldirHJ)
    # obj=Baiquan2_db(dbdirBQ2,filedirBQ2,flistdirBQ2,netvaldirBQ2)
    # obj=Guodao2_db(dbdirGD2,filedirGD2,flistdirGD2,netvaldirGD2)

    # obj.update_tables()
    # obj.update_netval_data()
    # obj.generate_netvalues()
    obj.take_netvalue(freq='week',indicators=True,mktidx=False,plots=True,outputdir=r'C:\Users\Jiapeng\Desktop\temp.csv')
