import requests
import json
import pandas as pd

# https://progr-account.tistory.com/151
def get_stock_Indices(date):  ### date type : str(),,, ex) '2010722'

    url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'

    data = {'bld': 'dbms/MDC/STAT/standard/MDCSTAT00101',
            'idxIndMidclssCd': '01',
            'trdDd': date,  ### date type : str(),,, ex) '2010722'
            'share': '2',
            'money': '3',
            'csvxls_isNo': 'false'}

    response = requests.post(url, data=data)  ### get이 아님에 유의
    stock_data = response.json()['output']  ### 불러온 정보를 json으로 추출하면 dict()구조인데 원하는 정보는 key:'output'에 있다.

    return stock_data


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

    return stock_data

if __name__ == '__main__':
    # print(get_stock_Indices('20220502'))
    print(get_stock_sise('20220502'))