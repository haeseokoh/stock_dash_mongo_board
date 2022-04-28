import pickle
import datetime

import pandas as pd
import FinanceDataReader as fdr
from time import time
from concurrent.futures import ProcessPoolExecutor

from dateutil.relativedelta import relativedelta

df_krx = fdr.StockListing('KRX')
df_krx.to_csv('df_krx.csv',encoding='utf-8-sig')
# df_krx  = pd.read_csv('df_krx.csv',encoding='utf-8-sig')
df_krx['SymbolName'] = df_krx['Symbol'] + df_krx['Name']
codes = df_krx['SymbolName']

def getPrice(code):
    datetime_r = datetime.datetime.now()

    datetime_r_weekday = datetime_r.weekday()
    adj_date = datetime_r + relativedelta(days=-datetime_r_weekday / 5)
    adj_date_52_weekago = adj_date + relativedelta(weeks=-52)

    df_price = None
    try:
        if code[-1] in ['콜', '풋']:
            print('code skip : ', code)
            return
        df_price = fdr.DataReader(code[:6], str(adj_date_52_weekago), str(adj_date)) # 주가 가져오기
        df_price = df_price[['Close']]
        df_price.columns = [code[6:]]
    except:
        print('code error : ', code)
        
    return df_price

def main():
    start = time()
    pool = ProcessPoolExecutor(max_workers=10)
    results = list(pool.map(getPrice, codes))
    stocks = pd.concat(results, axis=1)
    end = time()
    print(end - start)
    with open('datas.pkl', 'wb') as f:
        pickle.dump(stocks, f)
    stocks.to_excel('datas.xlsx')


if __name__ == '__main__':
    main()

    import crawlerNaverFSummary
    import momentem_stock_today

    crawlerNaverFSummary.main(crawlerNaverFSummary.KOSPI_CODE)
    crawlerNaverFSummary.main(crawlerNaverFSummary.KOSDAK_CODE)
    momentem_stock_today.main(momentem_stock_today.KOSPI_CODE)
    momentem_stock_today.main(momentem_stock_today.KOSDAK_CODE)