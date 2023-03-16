"# start" 
"# dash_mongo_board" 


import re
import requests
import numpy as np
import pandas as pd

import ssl
import json
import FinanceDataReader as fdr

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



def key_value_Crawling(ticker):
    url='https://m.comp.fnguide.com/m2/company_01_chosunbiz.asp?gicode=A{}'.format(ticker)
    r=requests.get(url)
    df=pd.read_html(r.text)

    market_value_string=df[2].iloc[3, 1]
    market_value=int(re.sub(r'[^0-9]', '', market_value_string))


    url='https://m.comp.fnguide.com/m2/company_03_chosunbiz.asp?gicode=A{}'.format(ticker)
    r=requests.get(url)
    df=pd.read_html(r.text)
    
    index_2020=df[1].columns.tolist().index("2020/12")
    
    base_df = None
    
    if pd.isnull(df[1].iloc[0, index_2020+2]):
        # per=df[1].iloc[13, 1:7].tolist() # per 
        op=df[5].iloc[2, index_2020:7].tolist() # operating profit 영업이익1
        ni=df[5].iloc[4, index_2020:7].tolist() # Net Income 당기순이익
        eps=df[5].iloc[10, index_2020:7].tolist() # eps
        per=[market_value/x for x in ni[2:]] #2020 0 -> 2 -> 2022
        base_df = df[5] 
    else:
        # per=df[1].iloc[13, 1:7].tolist() # per 
        op=df[1].iloc[2, index_2020:7].tolist() # operating profit 영업이익1
        ni=df[1].iloc[4, index_2020:7].tolist() # Net Income 당기순이익
        eps=df[1].iloc[10, index_2020:7].tolist() # eps
        per=[market_value/x for x in ni[2:]] #2020 0 -> 2 -> 2022
        base_df = df[1] 

    return market_value, per, op, ni, eps, base_df

def cal_cagr_peg(market_value, per, op, ni, eps, estimation=2):
    # 연평균성장률 (CAGR) (%) , 향후 3개년 (추정) (2022-2024)
    # EPS 기준	당기순이익 기준	영업이익 기준
    base = 2
    CAGR = [((eps[estimation+base]/eps[base])**(1/2)-1)*100, ((ni[estimation+base]/ni[base])**(1/2)-1)*100, ((op[estimation+base]/op[base])**(1/2)-1)*100]

    # PEG (2022년 PER 기준), 향후 3개년 (추정) (2022-2024)
    # EPS 기준	당기순이익 기준	영업이익 기준
    PEG=[per[0]/x for x in CAGR]

    # PEG (12개월 선행 PER 기준), 향후 3개년 (추정) (2022-2024)
    # EPS 기준	당기순이익 기준	영업이익 기준
    PEG_F=[per[1]/x for x in CAGR]
    
    return CAGR, PEG, PEG_F
    
    
df = pd.DataFrame()
ticker=[
    ('삼성전자','005930'),
    ('에코프로','086520'),
    ('에코프로비엠','247540'),
    ('에코프로에이치엔','383310'),
    ('POSCO홀딩스','005490'),
    ('포스코케미칼','003670'),
    ('코스모신소재','005070'),
    ('디엔에프','092070'),
    ('하이비젼시스템','126700'),
]

for x in ticker:
    print(x)
    market_value, per, op, ni, eps, base_df = key_value_Crawling(x[1])
    CAGR, PEG, PEG_F = cal_cagr_peg(market_value, per, op, ni, eps)
    # print(market_value, 'per:',per, 'op:',op, 'ni:',ni, 'eps:',eps, 'CAGR:',CAGR, 'PEG:',PEG, 'PEG_F:',PEG_F)
    
    df = df.append({'name':x[0], 'ticker':x[1], 'market value':market_value, 
                    'per(2022)':per[0], 'per(2023)':per[1], 'per(2024)':per[2],
                    'PEG(EPS 3y)':PEG[0], 'PEG(ni 3y)':PEG[1], 'PEG(op 3y)':PEG[2],
                    'PEG F(EPS 3y)':PEG_F[0], 'PEG F(ni 3y)':PEG_F[1], 'PEG F(op 3y)':PEG_F[2],
                   }, ignore_index=True)    
                   
                   
def review_PEG(ticker):
    market_value, per, op, ni, eps, base_df = key_value_Crawling(ticker)
    CAGR, PEG, PEG_F = cal_cagr_peg(market_value, per, op, ni, eps)
    # print(market_value, 'per:',per, 'op:',op, 'ni:',ni, 'eps:',eps, 'CAGR:',CAGR, 'PEG:',PEG, 'PEG_F:',PEG_F)

    df = pd.DataFrame()
    df = df.append({ 'ticker':x[1], 'market value':market_value, 
                    'per(2022)':per[0], 'per(2023)':per[1], 'per(2024)':per[2],
                    'PEG(EPS 3y)':PEG[0], 'PEG(ni 3y)':PEG[1], 'PEG(op 3y)':PEG[2],
                    'PEG F(EPS 3y)':PEG_F[0], 'PEG F(ni 3y)':PEG_F[1], 'PEG F(op 3y)':PEG_F[2],
                   }, ignore_index=True)
    return base_df, df                   

df_krx=krx_stock_listing()
