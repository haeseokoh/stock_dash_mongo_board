import pickle
import datetime

import pandas as pd
import FinanceDataReader as fdr
from time import time
from concurrent.futures import ProcessPoolExecutor

from dateutil.relativedelta import relativedelta
from libs_stock.trading_from_db import stockDB, get_from_db_recover_missing_data

database_name = 'stock_'
def get_from_db(jongmok, start, end, ticker):
    _db_OHLCV, wanted = stockDB(database_name, 'OHLCV')
    dlist = get_from_db_recover_missing_data(_db_OHLCV, wanted, start, end, jongmok,
                                             field=['시가', '고가', '저가', '종가', '거래량'], ticker=ticker)
    df_OHLCV = pd.DataFrame(dlist)

    _db_trading, wanted = stockDB(database_name, '거래량')
    dlist = get_from_db_recover_missing_data(_db_trading, wanted, start, end, jongmok,
                                             field=['기관합계', '기타법인', '개인', '외국인합계'], ticker=ticker)
    df_trading = pd.DataFrame(dlist)

    return df_OHLCV


def getPrice(code):
    datetime_r = datetime.datetime.now()

    datetime_r_weekday = datetime_r.weekday()
    adj_date = datetime_r + relativedelta(days=-datetime_r_weekday / 5)
    adj_date_52_weekago = adj_date + relativedelta(weeks=-52)

    df_price = None
    print(code[:6], code, code[6:])
    try:
    # if True:
        if code[-1] in ['콜', '풋']:
            print('code skip : ', code)
            return
        # df_price = fdr.DataReader(code[:6], str(adj_date_52_weekago), str(adj_date)) # 주가 가져오기
        # df_price = get_from_db(code[6:], adj_date_52_weekago.strftime('%Y%m%d'), adj_date.strftime('%Y%m%d'), ticker=code[:6])  # 주가 가져오기
        df_price = get_from_db(code[6:], '20200503', '20220429', ticker=code[:6])  # 주가 가져오기
        # print(df_price)

        df_price = df_price[['종가']]
        df_price.columns = [code[6:]]
    except:
        print('code error : ', code)
        
    return df_price

def main():
    # df_krx = fdr.StockListing('KRX')
    # df_krx.to_csv('df_krx.csv',encoding='utf-8-sig')
    df_krx  = pd.read_csv('df_krx.csv',encoding='utf-8-sig')
    df_krx['SymbolName'] = df_krx['Symbol'] + df_krx['Name']
    codes = df_krx['SymbolName']
    print(codes)

    start = time()
    pool = ProcessPoolExecutor(max_workers=10)
    results = list(pool.map(getPrice, codes))
    stocks = pd.concat(results, axis=1)
    end = time()
    print(end - start)
    with open('datas.pkl', 'wb') as f:
        pickle.dump(stocks, f)
    stocks.to_excel('datas.xlsx')


def _main():
    df_krx = fdr.StockListing('KRX')
    # df_krx.to_csv('df_krx.csv',encoding='utf-8-sig')
    # df_krx  = pd.read_csv('df_krx.csv',encoding='utf-8-sig')
    df_krx['SymbolName'] = df_krx['Symbol'] + df_krx['Name']
    codes = df_krx['SymbolName']
    print(codes)

    start = time()
    results = []
    for x in codes:
        results.append(getPrice(x))
    stocks = pd.concat(results, axis=1)
    end = time()
    print(end - start)
    with open('datas.pkl', 'wb') as f:
        pickle.dump(stocks, f)
    stocks.to_excel('datas.xlsx')



if __name__ == '__main__':
    main()

    # from pykrx import stock
    # # df = stock.get_market_ohlcv_by_date("20210122")
    # df = stock.get_market_price_change("20180301", "20180320")
    # df = stock.get
    # # print(df.head(100))
    #
    # print(stock.get_market_ticker_name('005930'))


    # df = fdr.DataReader('005930', '2021')
    # print(df.head(10))
    # print(df.columns)
    # # df.index=df.index
    # date_index = []
    # for x in list(df.index):
    #     date_index.append(x.strftime('%Y%m%d'))
    # print(getPrice('005930삼성전자'))
    #
    # # get_market_trading_and_update_db : OHLCV 2022-04-30 00:00:00 2022-05-03 00:00:00 삼성전자 005930
    # # 라는 트레이스가 발생이 되면 로컬이 아닌 서비스를 통해 데이트 가져오기를 시도하므로
    # print(date_index)
    # if '20210503' in date_index:
    #     print('++++++20210503+++++++')
    # else:
    #     print('======----=======')
    #     for i, x in enumerate(date_index):
    #         if x >= '20210503':
    #             break
    #     print(i, x)
    #
    # if '20220502' in date_index:
    #     print('++++++20220502+++++++')
    # else:
    #     print('======++++=======')
    #     for i, x in enumerate(date_index):
    #         if x >= '20220502':
    #             break
    #     print(i, x)
    #
    # print('20210104'>'20220502')
    # print('20210104'<'20220502')
    # print('20210104'=='20220502')



    # import crawlerNaverFSummary
    # import momentem_stock_today
    #
    # crawlerNaverFSummary.main(crawlerNaverFSummary.KOSPI_CODE)
    # crawlerNaverFSummary.main(crawlerNaverFSummary.KOSDAK_CODE)
    # momentem_stock_today.main(momentem_stock_today.KOSPI_CODE)
    # momentem_stock_today.main(momentem_stock_today.KOSDAK_CODE)