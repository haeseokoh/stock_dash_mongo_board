import pandas as pd
# import FinanceDataReader as fdr

from libs.mongo_api import db_init, db_update4

# df_krx = fdr.StockListing('KRX')
# df_krx.to_csv('df_krx.csv',encoding='utf-8-sig')
# df_krx  = pd.read_csv('df_krx.csv',encoding='utf-8-sig')
# df_krx['SymbolName'] = df_krx['Symbol'] + df_krx['Name']

df_krx = pd.read_csv (r'df_krx.csv') # NaverFinance - 재무정보
df = pd.read_excel(r'datas.xlsx',index_col=0) # datas - 가격정보 with 날짜정보 그대로
# df.rename(columns={'index': 'id'}, inplace=True)

name2sumbol = {}
for i, row in df_krx.iterrows():
    name2sumbol[row['Name']] = row['Symbol']

Symbols = []
for x in list(df.columns):
    try:
        Symbols.append(name2sumbol[x])
    except:
        Symbols.append(x)
        print(x)

df.columns = Symbols

df.reset_index(inplace=True, drop=False)

print(df.head())

database_name = 'stock'
wanted = 'daily_price'

# unique_field = '날짜'
unique_field = 'Date'
_db = db_init(database_name, wanted)
_db.db_col.create_index(unique_field, unique=True)
db_update4(_db, df, unique_field)