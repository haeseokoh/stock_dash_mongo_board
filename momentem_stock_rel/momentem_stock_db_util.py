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

    # print('read_datalist from db')
    # print('read_df result :',result)

    if result is not None:
        # print(result[wanted])
        return result.get(wanted)
    else:
        return None


def ticker_save():
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


    # df_jongmok.to_excel('종목.xlsx', index=False)
    # df_jongmok.to_pickle('종목.pkl')
    update_db(df_jongmok, 'ticker', database_name = 'stock_')

def get_tickers_df():
    jongmok_dic_list = read_datalist('ticker', database_name='stock_', )
    # print(jongmok_dic_list)
    df_jongmok = pd.DataFrame(jongmok_dic_list)
    del df_jongmok['id']
    return df_jongmok

def get_tickers(jongmok):
    df_jongmok=get_tickers_df()
    # https://www.interviewqs.com/ddi-code-snippets/rows-cols-python
    row = df_jongmok.loc[df_jongmok['jongmoks'] == jongmok]
    return row['tickers'].values[0] if len(row['tickers'].values) else None

if __name__ == '__main__':
    # ticker_save()
    print(get_tickers('삼성전자')) # {'id': 428, 'market': 'KOSPI', 'tickers': '005930', 'jongmoks': '삼성전자'}