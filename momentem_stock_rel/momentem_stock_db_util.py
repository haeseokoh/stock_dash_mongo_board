import pandas as pd

from pykrx import stock
from datetime import datetime, timedelta
from libs.mongo_api import db_init


def update_db(df, wanted, database_name = 'stock', collection_name = 'bin', unique_field = '날짜'):
    # -> dash의 selected_row_ids 를 위해sise_group
    df.reset_index(inplace=True, drop=False)
    df.rename(columns={'index': 'id'}, inplace=True)

    dict = df.to_dict('records')
    today = datetime.today().strftime('%Y%m%d')

    _db = db_init(database_name, collection_name)
    _db.db_col.create_index(unique_field, unique=True)
    # _db.db_col.insert_one({}, {unique_field:today, 'name': 'KOSDAQ_sise', 'file': dict }, upsert=True)
    doc = {unique_field: today, wanted: dict}
    myquery = {unique_field: doc[unique_field]}
    newvalues = {"$set": doc}
    _db.db_col.update_one(myquery, newvalues, upsert=True)


def read_datalist(wanted, database_name ='stock', collection_name ='bin'):
    today = datetime.today().strftime('%Y%m%d')

    _db = db_init(database_name, collection_name)

    filter = {'날짜': {'$eq': today}}
    dict = {'_id':0, wanted: 1}
    result = _db.db_col.find_one(filter, dict)

    print('read_datalist from db')
    # print('read_df result :',result)

    if result is not None:
        # print(result[wanted])
        return result.get(wanted)
    else:
        return None


def ticker_save_old():
    # df_jongmok = pd.DataFrame()

    # df_jongmok = pd.read_pickle(r'D:\project\pythonProject\stack_pykrx\exam\종목.pkl')
    # D:\project\pythonProject\stack_pykrx\exam\ticker.py
    df_jongmok = pd.DataFrame()
    market = []
    tickers = []
    jongmoks = []

    for x in ['KOSPI', 'KOSDAQ', 'KONEX']:
        _jongmoks = []
        _tickers = stock.get_market_ticker_list(market=x)
        for ticker in _tickers:
            __jongmok = stock.get_market_ticker_name(ticker)
            # print(종목)
            _jongmoks.append(__jongmok)
        market.extend([x]*len(_tickers))
        tickers.extend(_tickers)
        jongmoks.extend(_jongmoks)

    df_jongmok['market'] = market
    df_jongmok['tickers'] = tickers
    df_jongmok['jongmoks'] = jongmoks


    df_jongmok.to_excel('종목.xlsx', index=False)
    # df_jongmok.to_pickle('종목.pkl')
    update_db(df_jongmok, 'ticker', database_name = 'stock_')

def get_tickers_df_old():
    jongmok_dic_list = read_datalist('ticker', database_name='stock_', )
    # print(jongmok_dic_list)
    df_jongmok = pd.DataFrame(jongmok_dic_list)
    del df_jongmok['id']
    return df_jongmok

def get_tickers_old(jongmok):
    df_jongmok=get_tickers_df_old()
    # https://www.interviewqs.com/ddi-code-snippets/rows-cols-python
    row = df_jongmok.loc[df_jongmok['jongmoks'] == jongmok]
    return row['tickers'].values[0] if len(row['tickers'].values) else None

#########################################################################################
# new api
import ssl
import requests
import json
try:
    from pandas import json_normalize
except ImportError:
    from pandas.io.json import json_normalize

def krx_stock_listing():
    # KRX 상장회사목록
    # For mac, SSL CERTIFICATION VERIFICATION ERROR
    ssl._create_default_https_context = ssl._create_unverified_context

    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    df_listing = pd.read_html(url, header=0)[0]
    cols_ren = {'회사명': 'Name', '종목코드': 'Symbol', '업종': 'Sector', '주요제품': 'Industry',
                '상장일': 'ListingDate', '결산월': 'SettleMonth', '대표자명': 'Representative',
                '홈페이지': 'HomePage', '지역': 'Region', }
    df_listing = df_listing.rename(columns=cols_ren)
    df_listing['Symbol'] = df_listing['Symbol'].apply(lambda x: '{:06d}'.format(x))
    df_listing['ListingDate'] = pd.to_datetime(df_listing['ListingDate'])

    # KRX 주식종목검색
    data = {'bld': 'dbms/comm/finder/finder_stkisu', }
    r = requests.post('http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd', data=data)

    jo = json.loads(r.text)
    df_finder = json_normalize(jo, 'block1')

    # full_code, short_code, codeName, marketCode, marketName, marketEngName, ord1, ord2
    df_finder.columns = ['FullCode', 'Symbol', 'Name', 'MarketCode', 'MarketName', 'Market', 'Ord1', 'Ord2']

    # 상장회사목록, 주식종목검색 병합
    df_left = df_finder[['Symbol', 'Market', 'Name']]
    df_right = df_listing[
        ['Symbol', 'Sector', 'Industry', 'ListingDate', 'SettleMonth', 'Representative', 'HomePage', 'Region']]

    df_master = pd.merge(df_left, df_right, how='left', left_on='Symbol', right_on='Symbol')

    col_map = {'Symbol': '종목코드',
               'Market': '시장구분',
               'Name': '종목명',
               'Sector': '섹터',
               'Industry': '산업',
               'ListingDate': '상장일',
               'SettleMonth': '결산일',
               'Representative': '대표',
               'HomePage': 'HomePage',
               'Region': '지역'}

    df_master = df_master.rename(columns=col_map)
    # if self.market in ['KONEX', 'KOSDAQ', 'KOSPI']:
    #     return df_master[df_master['Market'] == self.market]
    return df_master

def ticker_save():
    df_krx = krx_stock_listing()
    df_krx.fillna("",inplace=True)
    update_db(df_krx, 'ticker', database_name = 'stock_')

df_jongmok = pd.DataFrame()
def get_tickers_df():
    global df_jongmok
    if df_jongmok.empty:
        jongmok_dic_list = read_datalist('ticker', database_name='stock_', )
        # print(jongmok_dic_list)
        df_jongmok = pd.DataFrame(jongmok_dic_list)  # index=False로 저장 되었어야 하나???
        del df_jongmok['id']
        print(df_jongmok)
    return df_jongmok

def get_tickers(jongmok):
    df_jongmok=get_tickers_df()
    # https://www.interviewqs.com/ddi-code-snippets/rows-cols-python
    row = df_jongmok.loc[df_jongmok['종목명'] == jongmok]
    return row['종목코드'].values[0] if len(row['종목코드'].values) else None

if __name__ == '__main__':
    # ticker_save()
    print(get_tickers('삼성전자')) # {'id': 428, 'market': 'KOSPI', 'tickers': '005930', 'jongmoks': '삼성전자'}
    print(get_tickers('삼성전자'))