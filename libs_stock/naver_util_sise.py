import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

from libs_stock.stock_db_util import *

KOSPI_CODE = 0
KOSDAK_CODE = 1
START_PAGE = 1



def naver_finance_simple(wanted, urls):
    datalist = read_datalist(wanted)
    if datalist is not None:
        return datalist

    print('{} ----'.format(wanted))


    merge = pd.DataFrame()
    for x in urls:
        table = pd.read_html(x, header=0, encoding='euc-kr')
        table[1].dropna(how='all', inplace=True)
        merge = merge.append(table[1], ignore_index=True)

    merge.drop('N', axis=1, inplace=True)
    if '등락률' in list(merge.columns):
        merge['등락률'] = merge.apply(lambda x: float(x['등락률'].replace('%', '')), axis=1)

    if 'sise_rise' in wanted:
        merge.sort_values(by=['등락률'], axis=0, ascending=False, inplace=True)


    print('merge.head():\n',merge.head())
    update_db(merge, wanted)
    return merge.to_dict('records')


def KOSPI_sise_market_sum_simple():
    urls = ['https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0&page={}'.format(x) for x in range(1,21) ]
    return naver_finance_simple('KOSPI_sise_market_sum', urls)

def KOSDAQ_sise_market_sum_simple():
    urls = ['https://finance.naver.com/sise/sise_market_sum.nhn?sosok=1&page={}'.format(x) for x in range(1,21) ]
    return naver_finance_simple('KOSDAQ_sise_market_sum', urls)


def KOSPI_sise_rise_simple():
    urls = ['https://finance.naver.com/sise/sise_rise.nhn?sosok=0',
            'https://finance.naver.com/sise/sise_steady.nhn?sosok=0',
            'https://finance.naver.com/sise/sise_fall.nhn?sosok=0'
            ]
    return naver_finance_simple('KOSPI_sise_rise', urls)

def KOSDAQ_sise_rise_simple():
    urls = ['https://finance.naver.com/sise/sise_rise.nhn?sosok=1',
            'https://finance.naver.com/sise/sise_steady.nhn?sosok=1',
            'https://finance.naver.com/sise/sise_fall.nhn?sosok=1'
            ]
    return naver_finance_simple('KOSDAQ_sise_rise', urls)




def crawl(fields, code, BASE_URL='', page=-1, url='', menu=''):
    if len(BASE_URL):
        url = BASE_URL + str(code) + "&page=" + str(page)

    data = {'menu': menu,
            'fieldIds':  fields,
            'returnUrl': url}
    # requests.get 요청대신 post 요청
    res = requests.post('https://finance.naver.com/sise/field_submit.nhn', data=data)

    page_soup = BeautifulSoup(res.text, 'lxml')
    # 크롤링할 table html 가져오기
    table_html = page_soup.select_one('div.box_type_l')

    # Column명
    if len(BASE_URL):
        header_data  = [item.get_text().strip() for item in table_html.select('thead th')][1:-1]
    else:
        header_data  = [item.get_text().strip() for item in table_html.select('th')][1:]

    # 종목명 + 수치 추출 (a.title = 종목명, td.number = 기타 수치)
    inner_data = [item.get_text().strip() for item in table_html.find_all(lambda x:
                                                                           (x.name == 'a' and
                                                                            'tltle' in x.get('class', [])) or
                                                                           (x.name == 'td' and
                                                                            'number' in x.get('class', []))
                                                                           )]

    # page마다 있는 종목의 순번 가져오기
    no_data = [item.get_text().strip() for item in table_html.select('td.no')]
    number_data = np.array(inner_data)

    # 가로 x 세로 크기에 맞게 행렬화
    number_data.resize(len(no_data), len(header_data ))

    # 한 페이지에서 얻은 정보를 모아 DataFrame로 만들어 리턴
    df = pd.DataFrame(data=number_data, columns=header_data )
    return df


def naver_finance(code, wanted, BASE_URL='', multi_page_start=-1, urls=None, menus=None):
    datalist = read_datalist(wanted)
    if datalist is not None:
        return datalist


    if len(BASE_URL):
        # total_page을 가져오기 위한 requests
        res = requests.get(BASE_URL + str(code) + "&page=" + str(multi_page_start))
        page_soup = BeautifulSoup(res.text, 'lxml')

        # total_page 가져오기
        total_page_num = page_soup.select_one('td.pgRR > a')
        total_page_num = int(total_page_num.get('href').split('=')[-1])

        #가져올 수 있는 항목명들을 추출
        ipt_html = page_soup.select_one('div.subcnt_sise_item_top')
        fields = [item.get('value') for item in ipt_html.select('input')]

        # page마다 정보를 긁어오게끔 하여 result에 저장
        result = [crawl(fields, code, BASE_URL=BASE_URL, page=str(page), menu='market_sum') for page in range(1,total_page_num+1)]
    else:
        # total_page을 가져오기 위한 requests
        res = requests.get(urls[0])
        page_soup = BeautifulSoup(res.text, 'lxml')

        # 가져올 수 있는 항목명들을 추출
        ipt_html = page_soup.select_one('div.subcnt_sise_item_top')
        fields = [item.get('value') for item in ipt_html.select('input')]
        print('else:fields :', fields)

        # page마다 정보를 긁어오게끔 하여 result에 저장
        result = [crawl(fields, code, url=urls[x], menu=menus[x]) for x in range(0, len(urls))]


    # page마다 가져온 정보를 df에 하나로 합침
    df = pd.concat(result, axis=0,ignore_index=True)


    # # 엑셀로 내보내기
    # df.to_excel('NaverFinance.xlsx')
    # df.to_pickle('NaverFinance.pkl')
    if '등락률' in list(df.columns):
        df['등락률'] = df.apply(lambda x: float(x['등락률'].replace('%', '')), axis=1)

        if 'sise_rise' in wanted:
            df.sort_values(by=['등락률'], axis=0, ascending=False, inplace=True)


    print('merge.head():\n',df.head())
    update_db(df, wanted)
    return df.to_dict('records')



def KOSPI_sise_market_sum():
    BASE_URL = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='
    datalist = naver_finance(KOSPI_CODE, 'KOSPI_sise_market_sum', BASE_URL=BASE_URL, multi_page_start=START_PAGE)
    return datalist

def KOSDAQ_sise_market_sum():
    BASE_URL = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok='
    datalist = naver_finance(KOSDAK_CODE, 'KOSDAQ_sise_market_sum', BASE_URL=BASE_URL, multi_page_start=START_PAGE)
    return datalist


def KOSPI_sise_rise():
    urls = ['https://finance.naver.com/sise/sise_rise.nhn?sosok=0',
            'https://finance.naver.com/sise/sise_steady.nhn?sosok=0',
            'https://finance.naver.com/sise/sise_fall.nhn?sosok=0'
            ]
    menus = ['rise', 'steady', 'fall']
    datalist = naver_finance(KOSPI_CODE, 'KOSPI_sise_rise', urls=urls, menus=menus)
    return datalist

def KOSDAQ_sise_rise():
    urls = ['https://finance.naver.com/sise/sise_rise.nhn?sosok=1',
            'https://finance.naver.com/sise/sise_steady.nhn?sosok=1',
            'https://finance.naver.com/sise/sise_fall.nhn?sosok=1'
            ]
    menus = ['rise', 'steady', 'fall']
    datalist = naver_finance(KOSDAK_CODE, 'KOSDAQ_sise_rise', urls=urls, menus=menus)
    return datalist
