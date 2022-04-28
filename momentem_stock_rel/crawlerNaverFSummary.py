# https://jsp-dev.tistory.com/89

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

BASE_URL='https://finance.naver.com/sise/sise_market_sum.nhn?sosok='

KOSPI_CODE = 0
KOSDAK_CODE = 1
START_PAGE = 1
fields = []

def main(code):
    # total_page을 가져오기 위한 requests
    res = requests.get(BASE_URL + str(code) + "&page=" + str(START_PAGE))
    page_soup = BeautifulSoup(res.text, 'lxml')

    # total_page 가져오기
    total_page_num = page_soup.select_one('td.pgRR > a')
    total_page_num = int(total_page_num.get('href').split('=')[-1])

    #가져올 수 있는 항목명들을 추출
    ipt_html = page_soup.select_one('div.subcnt_sise_item_top')
    global fields
    fields = [item.get('value') for item in ipt_html.select('input')]

    # page마다 정보를 긁어오게끔 하여 result에 저장
    result = [crawl(code,str(page)) for page in range(1,total_page_num+1)]

    # page마다 가져온 정보를 df에 하나로 합침
    df = pd.concat(result, axis=0,ignore_index=True)

    # 엑셀로 내보내기
    df.to_excel('NaverFinance_{}.xlsx'.format(code))
    df.to_pickle('NaverFinance_{}.pkl'.format(code))


def crawl(code, page):
    global fields
    data = {'menu': 'market_sum',
            'fieldIds':  fields,
            'returnUrl': BASE_URL + str(code) + "&page=" + str(page)}
    # requests.get 요청대신 post 요청
    res = requests.post('https://finance.naver.com/sise/field_submit.nhn', data=data)

    page_soup = BeautifulSoup(res.text, 'lxml')
    # 크롤링할 table html 가져오기
    table_html = page_soup.select_one('div.box_type_l')

    # Column명
    header_data  = [item.get_text().strip() for item in table_html.select('thead th')][1:-1]

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

if __name__ == '__main__':
    main(KOSPI_CODE)
    main(KOSDAK_CODE)