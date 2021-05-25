import pandas as pd
import numpy as np
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from libs_stock.stock_db_util import *

base_url = 'https://finance.naver.com'


def sise_group(url, type_name, fields, return_type='datafrmae'):
    data = {'menu': type_name,
            'fieldIds': fields,
            'returnUrl': url}
    # requests.get 요청대신 post 요청
    res = requests.post('https://finance.naver.com/sise/field_submit.nhn', data=data)

    page_soup = BeautifulSoup(res.text, 'lxml')
    # 크롤링할 table html 가져오기
    _table_html = page_soup.select('div.box_type_l')
    table_html = _table_html[1]

    # Column명
    header_data = [item.get_text().strip() for item in table_html.select('thead th')][0:-1]

    # 종목명 + 수치 추출 (a.title = 종목명, td.number = 기타 수치)
    inner_data = [item.get_text().strip() for item in table_html.find_all(lambda x:
                                                                          (x.name == 'td' and 'name' in x.get('class',
                                                                                                              [])) or
                                                                          (x.name == 'td' and 'number' in x.get('class',
                                                                                                                []))
                                                                          )]

    # page마다 있는 종목의 순번 가져오기
    # no_data = [item.get_text().strip() for item in table_html.select('td.no')]
    number_data = np.array(inner_data)

    # 가로 x 세로 크기에 맞게 행렬화
    number_data.resize(int(len(number_data) / len(header_data)), len(header_data))

    # 한 페이지에서 얻은 정보를 모아 DataFrame로 만들어 리턴
    df = pd.DataFrame(data=number_data, columns=header_data)

    theme_info_area = table_html.select('p.info_txt')
    if len(theme_info_area):
        # [item.get_text().strip() for item in table_html.select('div.theme_info_area')]
        df['편입사유'] = [item.get_text().strip() for item in theme_info_area]

    if return_type == 'datalist':
        return df.to_dict('records')
    else:
        return df


def get_fields(url):
    res = requests.get(url)
    page_soup = BeautifulSoup(res.text, 'lxml')

    table_html = page_soup.select('div.box_type_l')
    # 가져올 수 있는 항목명들을 추출
    ipt_html = table_html[0].select_one('table')
    fields = [item.get('value') for item in ipt_html.select('input')]
    # print(fields)
    return fields


def naver_sise_group_main_siglepage(url):
    r = requests.get(url)
    html_table = BeautifulSoup(r.text).find('table')
    r.close()
    df = pd.read_html(url, header=0, encoding='euc-kr')[0]

    # df['Link'] = [link.get('href') for link in html_table.find_all('a')]
    link_list = []
    for link in html_table.find_all('a'):
        if 'sise_group_detail' in link.get('href'):
            link_list.append(link.get('href'))
    # print(len(link_list), link_list)

    df.dropna(how='all', inplace=True)
    df.columns = list(df.iloc[0])
    df.drop(0, inplace=True)
    df.reset_index(drop=True, inplace=True)
    # print(df)
    df['Link'] = link_list
    return df


def naver_sise_group_main_multipage(url):
    table = pd.read_html(url, header=0, encoding='euc-kr')

    pages = []
    for x in list(table[1].columns):
        page = re.findall("\d+", x)
        if page:
            pages.append(page[0])

    print(pages)

    merge = pd.DataFrame()
    for x in pages:
        print(url + '?page=' + x)
        merge = merge.append(naver_sise_group_main_siglepage(url + '?page=' + x), ignore_index=True)
        # merge=merge.append(df,ignore_index=True)

    # merge.to_excel(datetime.today().strftime('%Y%m%d')+'_theme.xlsx')
    return merge


def group_main(type_name, url, page=False):
    datalist = read_datalist(type_name, collection_name=type_name)
    if datalist is not None:
        return datalist

    if page:
        merge = naver_sise_group_main_multipage(url)
    else:
        merge = naver_sise_group_main_siglepage(url)

    update_db(merge, type_name, collection_name=type_name)
    return merge.to_dict('records')


def group_sub(type_name, url, group, fields):
    datalist = read_datalist(group, collection_name=type_name)
    if datalist is not None:
        return datalist

    df = sise_group(url, type_name, fields)

    update_db(df, group, collection_name=type_name)
    return df.to_dict('records')


def crawl_sise_group(mainlist, type_name):
    group = []

    group_category = list(mainlist[0].keys())[1]
    url = base_url + mainlist[0].get('Link')
    fields = get_fields(url)

    for x in mainlist:
        # print(x.get(group_category), base_url + x.get('Link'))
        datalist = group_sub(type_name, base_url + x.get('Link'), x.get(group_category), fields)
        group.append({'key': x.get(group_category), 'value': datalist})
    return group

def upjong_sise():
    type_name = 'upjong'
    url = 'https://finance.naver.com/sise/sise_group.nhn?type=upjong'
    datalist = group_main(type_name, url, page=False)
    return datalist

def upjong_sise_sub(url, group):
    type_name = 'upjong'
    fields = get_fields(url)
    datalist = group_sub(type_name, url, group, fields)
    return datalist

def group_sise():
    type_name = 'group'
    url = 'https://finance.naver.com/sise/sise_group.nhn?type=group'
    datalist = group_main(type_name, url, page=False)
    return datalist

def group_sise_sub(url, group):
    type_name = 'group'
    fields = get_fields(url)
    datalist = group_sub(type_name, url, group, fields)
    return datalist

def theme_sise():
    type_name = 'theme'
    url = 'https://finance.naver.com/sise/theme.nhn'
    datalist = group_main(type_name, url, page=True)
    return datalist

def theme_sise_sub(url, group):
    type_name = 'theme'
    fields = get_fields(url)
    datalist = group_sub(type_name, url, group, fields)
    return datalist

if __name__ == "__main__":
    # url = 'https://finance.naver.com/sise/theme.nhn'
    # merge = naver_sise_group_main_multipage(url)
    # group = crawl_sise_group(merge, 'theme')
    #
    # url = 'https://finance.naver.com/sise/sise_group.nhn?type=upjong'
    # merge = naver_sise_group_main_siglepage(url)
    # group = crawl_sise_group(merge, 'upjong')
    #
    # url = 'https://finance.naver.com/sise/sise_group.nhn?type=group'
    # merge = naver_sise_group_main_siglepage(url)
    # group = crawl_sise_group(merge, 'group')

    type_name = 'upjong'

    url = 'https://finance.naver.com/sise/sise_group.nhn?type=upjong'
    mainlist = group_main(type_name, url, page=False)

    group_all=crawl_sise_group(mainlist, type_name)
    print(len(group_all))

    url = base_url + '/sise/sise_group_detail.nhn?type=upjong&no=162'
    group = '건축자재'
    fields = get_fields(url)
    group_sub(type_name, url, group, fields)


