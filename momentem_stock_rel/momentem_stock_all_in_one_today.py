import requests
import json
import pandas as pd
import ssl
import FinanceDataReader as fdr
import datetime
from dateutil.relativedelta import relativedelta

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


df_krx = krx_stock_listing()
df_krx.to_csv('df_krx.csv', encoding='utf-8-sig', index=False)

KOSPI_CODE = 0
KOSDAK_CODE = 1


def get_stock_sise(date):  ### date type : str(),,, ex) '2010722'

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'

    data = {'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
            'locale': 'ko_KR',
            'mktId': 'ALL',
            'trdDd': date,  ### date type : str(),,, ex) '2010722'
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false'}

    response = requests.post(url, data=data)  ### get이 아님에 유의
    stock_data = response.json()  ### 불러온 정보를 json으로 추출하면 dict()구조인데 원하는 정보는 key:'output'에 있다.

    col_map = {'ISU_SRT_CD': '종목코드',
               'ISU_ABBRV': '종목명',
               'MKT_NM': '시장구분',
               'SECT_TP_NM': '소속부',
               'TDD_CLSPRC': '종가',
               'FLUC_TP_CD': 'FLUC_TP_CD',
               'CMPPREVDD_PRC': '대비',
               'FLUC_RT': '등락률',
               'TDD_OPNPRC': '시가',
               'TDD_HGPRC': '고가',
               'TDD_LWPRC': '저가',
               'ACC_TRDVOL': '누적거래량',
               'ACC_TRDVAL': '누적거래대금',
               'MKTCAP': '시가총액',
               'LIST_SHRS': '상장주식수',
               'MKT_ID': '시장ID'}

    df = pd.DataFrame(stock_data['OutBlock_1'])
    df = df.rename(columns=col_map)
    df.drop(['소속부', 'FLUC_TP_CD', '시장ID'], axis=1, inplace=True)

    return df


# PER/PBR/배당수익률
# https://blog.naver.com/PostView.naver?blogId=sisomimoctrl&logNo=222414542520&parentCategoryNo=&categoryNo=185&viewDate=&isShowPopularPosts=false&from=postList
def get_stock_Investment_Indicators(date):  ### date type : str(),,, ex) '2010722'

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'

    data = {
        'bld': 'dbms/MDC/STAT/standard/MDCSTAT03501',
        'searchType': '1',
        'mktId': 'ALL',
        'trdDd': date,  ### date type : str(),,, ex) '2010722'
        'share': '1',
        'csvxls_isNo': 'false'}

    response = requests.post(url, data=data)  ### get이 아님에 유의
    stock_data = response.json()  ### 불러온 정보를 json으로 추출하면 dict()구조인데 원하는 정보는 key:'output'에 있다.

    col_map = {'ISU_SRT_CD': '종목코드',
               'ISU_ABBRV': '종목명',
               'ISU_ABBRV_STR': 'ISU_ABBRV_STR',
               'TDD_CLSPRC': '현재가',  # '종가',
               'FLUC_TP_CD': 'FLUC_TP_CD',
               'CMPPREVDD_PRC': '대비',
               'FLUC_RT': '등락률',
               'EPS': 'EPS',
               'PER': 'PER',
               'FWD_EPS': 'FWD_EPS',
               'FWD_PER': 'FWD_PER',
               'BPS': 'BPS',
               'PBR': 'PBR',
               'DPS': '주당배당금',
               'DVD_YLD': '배당수익률'}

    df = pd.DataFrame(stock_data['output'])
    df = df.rename(columns=col_map)
    df.drop(['ISU_ABBRV_STR', 'FLUC_TP_CD'], axis=1, inplace=True)

    return df


def create_master(date):
    df_krx = pd.read_csv('df_krx.csv', encoding='utf-8-sig')

    df_curr = get_stock_sise(date)
    df0 = get_stock_Investment_Indicators(date)
    # ['EPS', 'PER', 'FWD_EPS', 'FWD_PER', 'BPS', 'PBR', '주당배당금', '배당수익률']
    df_master = pd.merge(df_curr, df0[['종목코드', 'EPS', 'PER', 'FWD_EPS', 'FWD_PER', 'BPS', 'PBR', '주당배당금', '배당수익률']],
                         how='left', left_on='종목코드', right_on='종목코드')
    df_master = pd.merge(df_master, df_krx[['종목코드', '섹터', '산업']], how='left', left_on='종목코드', right_on='종목코드')
    df_master['시가총액'] = df_master['시가총액'].str.replace(',', '').astype(float)
    cols = list(df_master.columns)
    cols = cols[:3] + cols[-2:] + cols[3:-2]
    df_master = df_master[cols]

    market_name = ['KOSPI', 'KOSDAQ', 'KONEX']

    df_master_0 = df_master.sort_values(by=['시가총액'], ascending=[False])[df_master['시장구분'] == market_name[0]]
    df_master_0 = df_master_0.reset_index(drop=True)

    df_master_1 = df_master.sort_values(by=['시가총액'], ascending=[False])[df_master['시장구분'] == market_name[1]]
    df_master_1 = df_master_1.reset_index(drop=True)

    return [df_master_0, df_master_1]


def get_ref_date(few=4, long=51):
    datetime_r = datetime.datetime.now() + relativedelta(days=-1)
    datetime_r_weekday = datetime_r.weekday()
    adj_date = datetime_r + relativedelta(days=-datetime_r_weekday / 5)
    _FEW_AGO = adj_date + relativedelta(weeks=-few)
    _LONG_AGO = adj_date + relativedelta(weeks=-long)

    FEW_AGO = _FEW_AGO.strftime('%Y%m%d')
    LONG_AGO = _LONG_AGO.strftime('%Y%m%d')

    df = fdr.DataReader('005930', LONG_AGO[:4])
    date_index = []
    for x in list(df.index):
        date_index.append(x.strftime('%Y%m%d'))

    if LONG_AGO in date_index:
        choice_l = LONG_AGO
    else:
        for i, x in enumerate(date_index):
            if x >= LONG_AGO:
                break
        print(i, x)
        choice_l = x

    if FEW_AGO in date_index:
        choice_f = FEW_AGO
    else:
        for i, x in enumerate(date_index):
            if x >= FEW_AGO:
                break
        print(i, x)
        choice_f = x
    return date_index[-1], choice_l, choice_f

def create_momenterm_date(last_day, few_day, long_day):

    df_long = get_stock_sise(long_day)
    df_few = get_stock_sise(few_day)

    key = list(df_long['종목코드'])
    val = list(df_long['종가'])
    dict_long = dict(zip(key, val))

    key = list(df_few['종목코드'])
    val = list(df_few['종가'])
    dict_few = dict(zip(key, val))

    return_dic = {}
    for idx, df_finance in enumerate(create_master(last_day)):
        df_finance.loc[:, 'price_few_ago'] = 0
        price_few_ago_col = df_finance.columns.get_loc('price_few_ago')
        df_finance.loc[:, 'price_long_ago'] = 0
        price_long_ago_col = df_finance.columns.get_loc('price_long_ago')
        for index, row in df_finance.iterrows():
            name_code = row['종목코드']
            df_finance.iloc[index, price_few_ago_col] = dict_long.get(name_code)  # 1달 전 주가를 구해서 새로운 COLUMN으로 추가
            df_finance.iloc[index, price_long_ago_col] = dict_few.get(name_code)  # 1년 전 주가를 구해서 새로운 COLUMN으로 추가

        df_finance = df_finance[df_finance['price_few_ago'] != 0]  # 기준의 가격이 0이 아닌 종목만(우선주 등 없는 데이터 제외)
        df_finance = df_finance[df_finance['종가'] != '-']
        df_finance = df_finance[df_finance['PER'] != '-']
        df_finance = df_finance[df_finance['PBR'] != '-']

        df_finance = df_finance.reset_index(drop=True)
        df_finance = df_finance.loc[
                     :400]  # 시총 상위 200개만 추출, df_finance의 원천인 NaverFinance.xlsx은 원래 시총순 정렬이므로 순서대로 200개 자름

        df_finance['BPR'] = 1 / df_finance['PBR'].astype(float)  # BPR = 1/PBR
        df_finance['1/PER'] = 1 / df_finance['PER'].str.replace(',', '').astype(
            float)  # Per가 1000이 넘어 1,000인 형태가 존재하므로 replace 수행 후 type 변경
        df_finance['RANK_BPR'] = df_finance['BPR'].rank(method='max', ascending=False)  # BPR의 순위
        df_finance['RANK_1/PER'] = df_finance['1/PER'].rank(method='max', ascending=False)  # 1/PER의 순위
        df_finance['RANK_VALUE'] = (df_finance['RANK_BPR'] + df_finance['RANK_1/PER']) / 2  # 순위의 평균을 구함 > 가치평가 순위

        df_finance = df_finance.sort_values(by=['RANK_VALUE'])  # 가치평가 순위로 정렬
        df_finance = df_finance.reset_index(drop=True)
        # df_finance = df_finance.loc[:75] # 가치평가로 상위 75개만 추출
        # ----- 1차 가치평가 종료 -----

        df_finance['종가'] = df_finance['종가'].str.replace(',', '').astype(float)
        df_finance['price_few_ago'] = df_finance['price_few_ago'].str.replace(',', '').astype(float)
        df_finance['price_long_ago'] = df_finance['price_long_ago'].str.replace(',', '').astype(float)

        # 1달 등락률 계산
        df_finance['momentum_month'] = df_finance['종가'] - df_finance['price_few_ago']  # 오늘주가 - 1달 전 주가
        df_finance['몇일전 등락률'] = (df_finance['종가'] - df_finance['price_few_ago']) / df_finance['종가']

        # 1년 등락률 계산
        df_finance['momentum_year'] = df_finance['종가'] - df_finance['price_long_ago']  # 오늘주가 - 1년 전 주가
        df_finance['오래전 등락률'] = (df_finance['종가'] - df_finance['price_long_ago']) / df_finance['종가']

        df_finance['FINAL_MOMENTUM'] = df_finance['오래전 등락률'] - df_finance['몇일전 등락률']  # 1년 등락률 - 1달 등락률
        df_finance['RANK_MOMENTUM'] = df_finance['FINAL_MOMENTUM'].rank(method='max', ascending=False)  # 모멘텀의 순위
        # ----- 2차 모멘텀평가 종료 -----

        df_finance['FINAL_RANK'] = (df_finance['RANK_VALUE'] + df_finance['RANK_MOMENTUM']) / 2  # 가치 순위와 모멘텀 순위의 합산
        df_finance = df_finance.sort_values(by=['FINAL_RANK'], ascending=[True])
        df_finance = df_finance.reset_index(drop=True)

        # ymd = datetime.datetime.today().strftime('%Y%m%d')

        print(df_finance.head())

        return_dic[str(idx)]=df_finance
    return return_dic


def make_hyperlink(value):
    url = "https://finance.naver.com/item/main.naver?code={}"
    return '=HYPERLINK("%s", "%s")' % (url.format(value), value)


def main(few=4, long=51):
    last_day, few_day, long_day = get_ref_date(few, long)
    print(last_day, few_day, long_day)

    dic = create_momenterm_date(last_day, few_day, long_day)
    for key, val in dic.items():
        val['종목코드'] = val['종목코드'].apply(lambda x: make_hyperlink(x))
        val.to_excel('momentum_value_{}_{}.xlsx'.format(last_day, key))  # 최종 선정된 주식들 목록


if __name__ == '__main__':
    main(1, 24)
