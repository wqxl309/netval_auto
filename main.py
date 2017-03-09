

from src.Baiquan1 import *

dbdirJQ=r'E:\netval_auto\database\Jinqu1.db'
filedirJQ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号'+'\\'
flistdirJQ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉进取一号\list.txt'


dbdirHJ=r'E:\netval_auto\database\Huijin1.db'
filedirHJ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号'+'\\'
flistdirHJ=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉汇瑾一号\list.txt'

dbdirBQ1=r'E:\netval_auto\database\Baiquan1.db'
filedirBQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉一号'+'\\'
flistdirBQ1=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉一号\list.txt'
netvaldirBQ1=r'E:\净值表\netvalBQ1.db'
updtlstdirBQ1=r'E:\净值表\netvalBQ1.txt'

dbdirBQ2=r'E:\netval_auto\database\Baiquan2.db'
filedirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号'+'\\'
flistdirBQ2=r'C:\Users\Jiapeng\Desktop\Net Value\估值信息 百泉二号\list.txt'


obj=Baiquan1_db(dbdirBQ1,filedirBQ1,flistdirBQ1,updtlstdirBQ1,netvaldirBQ1)
print ( obj.get_updtlst() )