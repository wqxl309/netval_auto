import datetime as dt

dbdir_base = r'E:\netval_auto\database'
netdbdir_base = r'E:\netval_auto\netvalue'
filedir_base = r'E:\估值表'

PRODUCTS_INFO = \
    [
        {'pname':'百泉一号'      ,'pcode':'SD8964','ipodate':dt.date(2015,12,30),'confirmdays':2,'precision':3,'nickname':'Baiquan1'},
        {'pname':'百泉二号'      ,'pcode':'SR3281','ipodate':dt.date(2016,11,24),'confirmdays':2,'precision':4,'nickname':'Baiquan2'},
        {'pname':'百泉三号'      ,'pcode':'SS1391','ipodate':dt.date(2017, 5,19),'confirmdays':2,'precision':4,'nickname':'Baiquan3'},
        {'pname':'百泉进取一号'  ,'pcode':'SM7753','ipodate':dt.date(2016,11, 3),'confirmdays':2,'precision':4,'nickname':'BaiquanJQ1'},
        {'pname':'百泉汇瑾一号'  ,'pcode':'SN4286','ipodate':dt.date(2016,11,24),'confirmdays':2,'precision':3,'nickname':'BaiquanHJ1'},
        {'pname':'百泉多策略一号','pcode':'SS6021','ipodate':dt.date(2017, 4, 7),'confirmdays':2,'precision':3,'nickname':'BaiquanMS1'},

        {'pname':'国道砺石二号'  ,'pcode':'SM8060','ipodate':dt.date(2016,12,1), 'confirmdays':2,'precision':4,'nickname':'GuodaoLS2'},
        {'pname':'烜鼎鑫诚九号'  ,'pcode':'SR0165','ipodate':dt.date(2017,3,7),  'confirmdays':2,'precision':4,'nickname':'Xuanding9'},
        #{'pname':'星盈七号'       ,'pcode':'SM8060','ipodate':dt.date(2016,12,1), 'confirmdays':2,'precision':4},
        {'pname':'百泉砺石一号'  ,'pcode':'SM8060','ipodate':dt.date(2017,4,19), 'confirmdays':2,'precision':4,'nickname':'BaiquanLS1'},

    ]

extract_codes = ['sharenum','assettot','debttot','assetnet','servfee','keepfee','mangfee','earn','subscribe','redemption']
# 份额、总资产、总负债、净资产、服务费、托管费、管理费、业绩提成、认申购、赎回

fill = 'NotSeenYet'   # 目前估值表中还未出现项目的填充,等待出现后再替换为实际代码
CODEDICT=\
    {
        'Baiquan1': {'sharenum':'实收资本','assettot':'资产合计','debttot':'负债合计','assetnet':'资产净值','servfee':'2206.14',
                     'keepfee':'2207.01','mangfee':'2206.01','earn':'2206.02','subscribe':'1207.01','redemption':'2203.01','otherfee':'2241.99'},

        'Baiquan2': {'sharenum':'实收资本','assettot':'资产类合计:','debttot':'负债类合计:','assetnet':'基金资产净值:','servfee':'2205',
                     'keepfee':'2207','mangfee':'2206','earn':fill,'subscribe':fill,'redemption':fill,'otherfee':'224199'},

        'Baiquan3': {},

        'BaiquanJQ1':{'sharenum':'实收资本','assettot':'资产合计','debttot':'负债合计','assetnet':'资产净值','servfee':'2211.01',
                      'keepfee':'2207.01','mangfee':'2206.01','earn':'2206.02','subscribe':'1207.01','redemption':'2203.01','otherfee':'2241.99'},

        'BaiquanHJ1':{'sharenum':'实收资本','assettot':'资产类合计:','debttot':'负债类合计:','assetnet':'基金资产净值:','servfee':'220501',
                      'keepfee':'220701','mangfee':'220601','earn':'220602','subscribe':'120701','redemption':'220301','otherfee':'224199'},

        'BaiquanMS1':{},

        'BaiquanLS1':{},

        'GuodaoLS2':{'sharenum':'实收资本','assettot':'资产合计','debttot':'负债合计','assetnet':'资产净值','servfee':'2208.02',
                     'keepfee':'2207.01','mangfee':'2206.01','earn':'2206.02','subscribe':'1207.01','redemption':'2203.01','otherfee':'2241.99'},

        'Xuanding9':{'sharenum':'实收资本','assettot':'资产类合计:','debttot':'负债类合计:','assetnet':'基金资产净值:','servfee':'220501','keepfee':'220701','mangfee':'220601',
                     'earnT':'220602','earnAl':'220604','subscribe':'120701','redemption':'220301','secloan':'210171','secloanint':'250111','otherfee':'224199'}
    }


VARTYPES = {'TEXT':['科目代码','科目名称','币种','停牌信息','权益信息','科目级别']}