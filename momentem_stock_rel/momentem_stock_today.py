# https://jsp-dev.tistory.com/entry/Python%EC%9C%BC%EB%A1%9C-%EB%AA%A8%EB%A9%98%ED%85%80%EA%B0%80%EC%B9%98-%ED%8F%89%EA%B0%80-%EC%A3%BC%EC%8B%9D-%EC%84%A0%EC%A0%95-%EC%A2%85%EB%AA%A9-%EC%84%A0%EC%A0%95%ED%95%98%EA%B8%B0?category=808569

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

BASE_URL='https://finance.naver.com/sise/sise_market_sum.nhn?sosok='

KOSPI_CODE = 0
KOSDAK_CODE = 1
START_PAGE = 1
fields = []

#준비물1 가격정보 datas.xlsx
#준비물2 재무정보 NaverFinance.xlsx
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def main(code):
    df_finance = pd.read_excel(r'NaverFinance_{}.xlsx'.format(code)) # NaverFinance - 재무정보
    df_price = pd.read_excel(r'datas.xlsx',index_col=0) # datas - 가격정보 with 날짜정보 그대로

    # print(df_price)
    df_price_index = df_price.index.tolist()

    # # MONTH_AGO = '2020-03-09' # 1달전 주가구하기, 그냥 오늘 날로 하려면 datetime.today() + relativedelta(months=-1)
    # # # MONTH_AGO = MONTH_AGO.strftime('%Y-%m-%d')
    # #
    # # YEAR_AGO =  '2019-04-10' # 1년전 주가구하기, 그냥 오늘 날로 하려면 datetime.today()+relativedelta(years=-1)
    # # # YEAR_AGO = YEAR_AGO.strftime('%Y-%m-%d')
    # datetime_r = datetime.now() + relativedelta(days=-1)
    #
    # datetime_r_weekday = datetime_r.weekday()
    # adj_date = datetime_r + relativedelta(days=-datetime_r_weekday / 5)
    # _MONTH_AGO = adj_date + relativedelta(weeks=-4)
    # # _LONG_AGO = adj_date + relativedelta(weeks=-51)
    # _LONG_AGO = adj_date + relativedelta(weeks=-13)
    #
    # MONTH_AGO = _MONTH_AGO.strftime('%Y-%m-%d')
    # print('MONTH_AGO',MONTH_AGO)
    # LONG_AGO = _LONG_AGO.strftime('%Y-%m-%d')
    # print('LONG_AGO',LONG_AGO)
    MONTH_AGO = df_price.index.tolist()[-1+-5*4]
    LONG_AGO = df_price.index.tolist()[-1+-5*4*12]

    price_month_ago =[]
    price_year_ago =[]

    for index, row in df_finance.iterrows():
        name = row['종목명']
        if name in df_price.columns:
            price_month_ago.append(df_price.loc[MONTH_AGO, name] ) # 준비물인 datas에서 1달 전 주가 구하기
            price_year_ago.append(df_price.loc[LONG_AGO, name]) # 준비물인 datas에서 1년 전 주가 구하기
        else :
            # datas에서 종목이 존재하지 않는 경우(우선주, ETF 등은 없음)가 있으므로 제외
            price_month_ago.append(0)
            price_year_ago.append(0)

    df_finance['price_month_ago'] = price_month_ago # 1달 전 주가를 구해서 새로운 COLUMN으로 추가
    df_finance['price_year_ago'] = price_year_ago # 1년 전 주가를 구해서 새로운 COLUMN으로 추가

    df_finance =df_finance[df_finance['price_month_ago']!= 0] # 기준의 가격이 0이 아닌 종목만(우선주 등 없는 데이터 제외)

    df_finance = df_finance.reset_index(drop=True)
    df_finance = df_finance.loc[:400] # 시총 상위 200개만 추출, df_finance의 원천인 NaverFinance.xlsx은 원래 시총순 정렬이므로 순서대로 200개 자름

    df_finance['BPR'] = 1/df_finance['PBR'].astype(float) # BPR = 1/PBR
    df_finance['1/PER'] = 1/df_finance['PER'].str.replace(',', '').astype(float) # Per가 1000이 넘어 1,000인 형태가 존재하므로 replace 수행 후 type 변경
    df_finance['RANK_BPR']  = df_finance['BPR'].rank(method='max', ascending=False) # BPR의 순위
    df_finance['RANK_1/PER']  = df_finance['1/PER'].rank(method='max', ascending=False) # 1/PER의 순위
    df_finance['RANK_VALUE']  = (df_finance['RANK_BPR'] + df_finance['RANK_1/PER'])/ 2 # 순위의 평균을 구함 > 가치평가 순위

    df_finance = df_finance.sort_values(by=['RANK_VALUE']) # 가치평가 순위로 정렬
    df_finance = df_finance.reset_index(drop=True)
    # df_finance = df_finance.loc[:75] # 가치평가로 상위 75개만 추출
    # ----- 1차 가치평가 종료 -----

    df_finance['현재가'] = df_finance['현재가'].str.replace(',', '').astype(float)

    #1달 등락률 계산
    df_finance['momentum_month'] = df_finance['현재가'] - df_finance['price_month_ago'] #오늘주가 - 1달 전 주가
    df_finance['1달 등락률'] = (df_finance['현재가'] - df_finance['price_month_ago']) /  df_finance['현재가']

    #1년 등락률 계산
    df_finance['momentum_year'] = df_finance['현재가'] - df_finance['price_year_ago'] #오늘주가 - 1년 전 주가
    df_finance['1년 등락률'] = (df_finance['현재가'] - df_finance['price_year_ago']) /  df_finance['현재가']

    df_finance['FINAL_MOMENTUM'] = df_finance['1년 등락률'] - df_finance['1달 등락률'] # 1년 등락률 - 1달 등락률
    df_finance['RANK_MOMENTUM'] = df_finance['FINAL_MOMENTUM'].rank(method='max', ascending=False) # 모멘텀의 순위
    # ----- 2차 모멘텀평가 종료 -----

    df_finance['FINAL_RANK'] = (df_finance['RANK_VALUE']  + df_finance['RANK_MOMENTUM'])/2 # 가치 순위와 모멘텀 순위의 합산
    df_finance = df_finance.sort_values(by=['FINAL_RANK'], ascending=[True])
    df_finance = df_finance.reset_index(drop=True)

    df_finance.to_excel('momentum_value_{}.xlsx'.format(code)) # 최종 선정된 주식들 목록
    print(df_finance.head())
    df_finance.to_csv('momentum_value_{}.csv'.format(code))

if __name__ == '__main__':
    main(KOSPI_CODE)
    main(KOSDAK_CODE)