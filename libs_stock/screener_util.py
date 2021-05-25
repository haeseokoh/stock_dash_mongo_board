import pandas as pd
import requests
from bs4 import BeautifulSoup

from libs_stock.stock_db_util import update_db, read_datalist


def wise_thewm(searchtype, collection_name = 'wise_thewm'):
    datalist = read_datalist(searchtype, collection_name = collection_name)
    if datalist is not None:
        return datalist

    page = 1
    # lastpage = 1

    url = 'http://wise.thewm.co.kr/ASP/Screener/data/Screener2_Tabledata.asp?SearchType={}&I_CURPAGE={}&I_PERPAGE=10&I_mkt=0&I_Size=0&I_ksc=G0&kw1=&kw2=&kw3=&sqlTerm=1'.format(
        searchtype, page)
    r = requests.get(url)
    r_text = r.text
    r.close()

    # html_table = BeautifulSoup(r_text).find('table')
    page_navi = BeautifulSoup(r_text).find_all('a')
    page_str = page_navi[-1].get('onclick')
    lastpage = int(''.join(filter(str.isdigit, page_str)))

    # print(lastpage)

    merge = pd.DataFrame()
    while page < lastpage+1:
        url = 'http://wise.thewm.co.kr/ASP/Screener/data/Screener2_Tabledata.asp?SearchType={}&I_CURPAGE={}&I_PERPAGE=10&I_mkt=0&I_Size=0&I_ksc=G0&kw1=&kw2=&kw3=&sqlTerm=1'.format(
            searchtype, page)
        r = requests.get(url)
        r_text = r.text
        r.close()

        html_table = BeautifulSoup(r_text).find('table')
        # page_navi = BeautifulSoup(r_text).find_all('a')

        data_frame = pd.read_html(str(html_table))[0]
        data_frame.dropna(axis=1, how='all', inplace=True)
        merge = merge.append(data_frame, ignore_index=True)
        page += 1

    update_db(merge, searchtype, collection_name = collection_name)

    return merge.to_dict('records')