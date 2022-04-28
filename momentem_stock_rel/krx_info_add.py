

import pandas as pd
df_finance = pd.read_excel(r'NaverFinance.xlsx') # NaverFinance - 재무정보
df_krx = pd.read_csv (r'df_krx.csv') # NaverFinance - 재무정보

# dict_krx = df_krx.to_dict()
# print(dict_krx)

df_finance['Symbol']=None
df_finance['Sector']=None
df_finance['Industry']=None

for index, row in df_finance.iterrows():
    name = row['종목명']
    print(name)
    index_arr = df_krx[df_krx['Name'] == name]
    if index_arr.values.any():
        value_arr =  index_arr.values[0]
        print(value_arr[1:6])
        # https://stackoverflow.com/questions/31569384/set-value-for-particular-cell-in-pandas-dataframe-with-iloc
        df_finance.iloc[index, df_finance.columns.get_loc('Symbol')] = '=HYPERLINK("'+'https://finance.naver.com/item/coinfo.nhn?code='+value_arr[1]+'","'+value_arr[3]+'")'
        df_finance.iloc[index, df_finance.columns.get_loc('Sector')] = value_arr[4]
        df_finance.iloc[index, df_finance.columns.get_loc('Industry')] = value_arr[5]
        # df_finance.ix[index, 'Symbol'] = value_arr[1]
        # df_finance.ix[index, 'Symbol'] = value_arr[1]
        # df_finance.ix[index, 'Symbol'] = value_arr[1]
        # df_finance.ix[index, 'Symbol'] = value_arr[1]
        # row['Symbol']=value_arr[1]
    # Symbol = df_krx[is_same_name].get_value('Symbol')
    # Sector = df_krx[is_same_name]['Sector']
    # Industry = df_krx[is_same_name]['Industry']
    # print('-----------------', Symbol, Sector, Industry)

df_finance.to_excel('NaverFinance_krx.xlsx')