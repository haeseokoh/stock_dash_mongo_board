import os
import sys
from pykrx import stock

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from datetime import datetime, timedelta
# import datetime
from momentem_stock_rel.momentem_stock_db_util import get_tickers_df, get_tickers

sys.path.append(os.path.abspath('../libs'))
from libs.mongo_api import db_init, db_update4

# # df_jongmok = pd.DataFrame()
#
# # df_jongmok = pd.read_pickle(r'D:\project\pythonProject\stack_pykrx\exam\종목.pkl')
# # D:\project\pythonProject\stack_pykrx\exam\ticker.py
# df_jongmok = pd.DataFrame()
# market = []
# tickers = []
# jongmoks = []
#
# for x in ['KOSPI', 'KOSDAQ', 'KONEX']:
#     _jongmoks = []
#     _tickers = stock.get_market_ticker_list(market=x)
#     for ticker in _tickers:
#         __jongmok = stock.get_market_ticker_name(ticker)
#         # print(종목)
#         _jongmoks.append(__jongmok)
#     market.extend([x]*len(_tickers))
#     tickers.extend(_tickers)
#     jongmoks.extend(_jongmoks)
#
# df_jongmok['market'] = market
# df_jongmok['tickers'] = tickers
# df_jongmok['jongmoks'] = jongmoks
#
#
# # df_jongmok.to_excel('종목.xlsx', index=False)
# # df_jongmok.to_pickle('종목.pkl')


unique_field = '날짜'

# def get_tickers(jongmok):
#     # https://www.interviewqs.com/ddi-code-snippets/rows-cols-python
#     df_jongmok = get_tickers_df()
#
#     row = df_jongmok.loc[df_jongmok['jongmoks'] == jongmok]
#     return row['tickers'].values[0] if len(row['tickers'].values) else None

def get_max_min_from_db(_db, start, stop, name, ticker=None,):
    try:
        # jongmok = 'CJ제일제당'
        dBs=datetime.strptime(start, '%Y%m%d')
        dBe=datetime.strptime(stop, '%Y%m%d')
        min = _db.db_col.find({"$and": [
            # {unique_field: {'$lt': datetime.now(), '$gt': datetime.now() - timedelta(days=50)}},
            {unique_field: {'$gte': dBs, '$lte': dBe}},
            {name: {'$exists': True}}]}, {unique_field: 1, name: 1}).sort(unique_field,1).limit(1)
        max = _db.db_col.find({"$and": [
            # {unique_field: {'$lt': datetime.now(), '$gt': datetime.now() - timedelta(days=50)}},
            {unique_field: {'$gte': dBs, '$lte': dBe}},
            {name: {'$exists': True}}]}, {unique_field: 1, name: 1}).sort(unique_field,-1).limit(1)
        # if cursor:
        # max = cursor.sort({unique_field:-1}).limit(1)
        # min = cursor.sort({unique_field:1}).limit(1)

        return list(min)[0][unique_field], list(max)[0][unique_field]
    except:
        return None, None

def db_missing_date(_db, _s, _e, name, ticker=None):
    # _dBs = '20210306'
    # _dBe = '20210310'
    # _s = '20210311'
    # _e = '20210312'

    _dBs,_dBe = get_max_min_from_db(_db, _s, _e, name, ticker)
    print('db_missing_date :', _dBs,_dBe)

    date_list=[
        {'key':'dBs','date': _dBs},
        {'key':'dBe','date': _dBe},
        {'key':'s','date': datetime.strptime(_s, '%Y%m%d')},
        {'key':'e','date': datetime.strptime(_e, '%Y%m%d')}
    ]
    if (_dBs, _dBe) == (None, None):
        return [(date_list[2].get('date'), date_list[3].get('date')), (None, None)]

    date_list.sort(key=lambda item:item['date'])
    print('db_missing_date date_list:',date_list)
    # date_list.sort(key=lambda item:item['date'], reverse=True)
    # print(date_list)

    def find(key, date_list):
        for x in date_list:
            if key==x.get('key'):
                return x.get('date')

    prev_s = date_list[0].get('date')
    prev_e = find('dBs', date_list)
    forward_s = find('dBe', date_list)
    forward_e = date_list[3].get('date')
    prev = (None,None) if (prev_s == prev_e) else (prev_s, prev_e - timedelta(days=1))
    forward = (None,None) if (forward_s == forward_e) else (forward_s+timedelta(days=1), forward_e)

    print(prev, forward)
    return [prev, forward]


##########################################
# market_trading
##########################################
# combine pykrx and dB
def get_from_db_recover_missing_data(_db, wanted, start, end, jongmok, field=['기관합계', '기타법인', '개인', '외국인합계'], ticker=None):
    missing_date = db_missing_date(_db, start, end, jongmok)

    if ticker == None:
        # ticker = get_tickers(jongmok)
        ticker = stock.get_market_ticker_name(jongmok)

    for x in missing_date:
        if x[0]!=None:
            # get_and_update_db(_db, wanted, x[0], x[1], jongmok, get_tickers(jongmok))
            get_and_update_db(_db, wanted, x[0], x[1], jongmok, ticker)

    dlist = get_from_db(_db, start, end, jongmok, field=field)
    return dlist

# get from pykrx update to dB
def get_and_update_db(_db, wanted, start, stop, name, ticker):
    print('get_and_update_db...............')
    ticker = get_tickers(name)
    print('get_and_update_db', 'ticker', ticker )
    print('get_market_trading_and_update_db :', wanted, start, stop, name, ticker)
    try:
        df=pd.DataFrame()
        if wanted=='거래량':
            df = stock.get_market_trading_value_by_date(start, stop, ticker)
        elif wanted=='OHLCV':
            df = stock.get_market_ohlcv_by_date(start, stop, ticker)
        elif wanted == '재무':
            df = stock.get_market_fundamental_by_date(start, stop, ticker)
        elif wanted == '시총':
            df = stock.get_market_cap_by_date(start, stop, ticker)
        elif wanted == '공매도':
            # df = stock.get_shorting_status_by_date('20210121', '20210501', '097950')
            df = stock.get_shorting_status_by_date(start.strftime('%Y%m%d'), stop.strftime('%Y%m%d'), ticker)
        else:
            return None
        print(df.head())
        # ['기관합계', '기타법인', '개인', '외국인합계']

        # 배열로 압축해서 넣음
        df[name] = df.apply(lambda row: row.tolist(), axis=1)
        df.reset_index(inplace=True)

        unique_field = '날짜'
        update_df = df[[unique_field,name]]
        db_update4(_db, update_df, unique_field)
        return update_df
    except:
        return None

# get from db
def get_from_db(_db, start, stop, name, ticker=None, field=[]):
    print('get_from_db :', start, stop, name, ticker, field)
    # jongmok = 'CJ제일제당'
    cursor = _db.db_col.find(
        {"$and": [
            {unique_field: {'$gte': datetime.strptime(start, '%Y%m%d'), '$lte': datetime.strptime(stop, '%Y%m%d')}},
            {name: {'$exists': True}}]},
        {unique_field: 1, name: 1}
    )
    data = []

    for x in cursor:
        x['_id'] = '{}'.format(x['_id'])
        # print(x)
        _extract = {unique_field: x[unique_field]}
        # 배열에서 풀어냄
        for i, val in enumerate(field):
            _extract[val] = x[name][i]
        data.append(_extract)

    return data

def stockDB(database_name, wanted):
    # collection_name = '거래량'
    _db = db_init(database_name, wanted)
    _db.db_col.create_index(unique_field, unique=True)
    return _db, wanted


if __name__ == "__main__":
    database_name = 'stock'

    # start = "20191001"
    # end = "20200220"
    start = (datetime.today() - timedelta(days=100)).strftime('%Y%m%d')
    end = datetime.today().strftime('%Y%m%d')

    jongmok = 'CJ제일제당'

    _db_trading, wanted = stockDB(database_name, '거래량')
    dlist = get_from_db_recover_missing_data( _db_trading, wanted, start, end, jongmok, field=['기관합계', '기타법인', '개인', '외국인합계'])
    for x in dlist:
        print(x)

    _db_OHLCV, wanted = stockDB(database_name, 'OHLCV')
    dlist = get_from_db_recover_missing_data( _db_OHLCV, wanted, start, end, jongmok, field=['시가', '고가', '저가', '종가', '거래량'])
    for x in dlist:
        print(x)

    _db_fundamental, wanted = stockDB(database_name, '재무')
    dlist = get_from_db_recover_missing_data( _db_fundamental, wanted, start, end, jongmok, field=['BPS','PER','PBR','EPS','DIV','DPS'])
    for x in dlist:
        print(x)

    _db_cap, wanted = stockDB(database_name, '시총')
    dlist = get_from_db_recover_missing_data( _db_cap, wanted, start, end, jongmok, field=['시가총액', '거래량', '거래대금', '상장주식수'])
    for x in dlist:
        print(x)

    _db_shorting, wanted = stockDB(database_name, '공매도')
    dlist = get_from_db_recover_missing_data( _db_shorting, wanted, start, end, jongmok, field=['거래량', '잔고수량', '거래대금', '잔고금액'])
    for x in dlist:
        print(x)
