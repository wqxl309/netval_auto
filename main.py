from products.Baiquan1 import *
from products.Guodao2 import *
from products.Huijin1 import *
from products.Jinqu1 import *
from products.Baiquan2 import *

if __name__=='__main__':
    obj=Baiquan1_db()
    # obj=Jinqu1_db()
    # outdir=r'C:\Users\Jiapeng\Desktop\JQ1.csv'
    # obj=Huijin1_db()
    # outdir=r'C:\Users\Jiapeng\Desktop\HJ1.csv'
    # obj=Baiquan2_db()
    # outdir=r'C:\Users\Jiapeng\Desktop\BQ2.csv'
    # obj=Guodao2_db()
    # outdir=r'C:\Users\Jiapeng\Desktop\GD2.csv'

    obj.update_tables()
    obj.update_netval_data()
    obj.generate_netvalues()
    #obj.take_netvalue(freq='day',startdate='20170101',indicators=True,plots=True,outputdir=False)
