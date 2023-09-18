"# start" 
"# dash_mongo_board" 

import requests
import numpy as np
import pandas as pd
import json
import re

import plotly.express as px

# 엑셀 파일 읽기 용법-세종데이타 실적 스크리닝 ###############################################
# https://bio-info.tistory.com/49 멀티인덱스 처리
ds=pd.read_excel(xlsx_file, skiprows=12,  header=[0,1]) # converters={'종목코드': str} ??
ds.columns=list(map(lambda x: x[0].replace('\n', '') if 'Unnamed' in x[1] else x[0] + ' ' + x[1], ds.columns))
ds['종목코드'] = ds['종목코드'].astype(str).str.zfill(6) # converters={'a': str} ??


# code=ds[ds['시가총액(억원) D-day']>1000]
code=ds
code_dict=dict(zip(code['종목명'],code['종목코드']))
code.to_pickle('code.pkl')

# 수출입 통계 ###############################################
# 온라인 
https://www.bandtrass.or.kr/customs/total.do?command=CUS001View&viewCode=CUS00401

r=requests.get(r"https://www.bandtrass.or.kr/customs/total.do?command=CUS00401Detail&search=Y&COL_NAME=&EXCEL_LOG=&MENU_CODE=CUS00401&MSF_MAX_YEAR=2023&UndecideMaxDate=20230910&page=1&grid_type=C&S0010001=E&UNIT=1&S0010002=H&hscd_unit=10&SelectCd=9506399000&NatnCd=GH&NATN_CODE=&pageRowCount=50",
               headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"},
               verify=r'c:\cer_gumi.crt')

trass_req=r"https://www.bandtrass.or.kr/customs/total.do?command=CUS00401Detail&search=Y&COL_NAME=&EXCEL_LOG=&MENU_CODE=CUS00401&MSF_MAX_YEAR=2023&UndecideMaxDate=20230910&page=1&grid_type=C&S0010001={}&UNIT=1&S0010002=H&hscd_unit=10&SelectCd={}&NatnCd=GH&NATN_CODE=&pageRowCount=50"
head_req={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

def trass_ds(trade='E', hscode='2841909020'):
    # trade='E' or 'I', 2841909020 = 양극재, 8529903020 카메라 부분품
    r=requests.get(trass_req.format(trade, hscode), headers = head_req, verify=r'c:\cer_gumi.crt')
    _json=json.loads(r.text)
    ds=json.loads(_json.get('gridData'))
    return ds 

def gridData2df(ds):
    df=pd.DataFrame(ds)
    # df.rename(columns={'BASE_DATE':'년월', 'AMT_OF_DLR':'금액(달러)', 'AMT_OF_WON':'금액(원화)', 'NET_WGHT':'중량(Kg)'}, inplace=True)
    # df.drop(['NUM', 'TOT_CNT'], axis=1, inplace=True)
    df[['금액(달러)','금액(원화)','중량(Kg)']] = df[['AMT_OF_DLR', 'AMT_OF_WON', 'NET_WGHT']].apply(pd.to_numeric)
    df.rename(columns={'BASE_DATE':'년월'}, inplace=True)
    df=df[['년월','금액(달러)','금액(원화)','중량(Kg)']]

    df['금액(달러)/중량']=df['금액(원화)']/df['중량(Kg)']
    
    return df


# trade='E' or 'I', 2841909020 = 양극재, 8529903020 카메라 부분품
ds=trass_ds(trade='E', hscode='8529903020') 
df=gridData2df(ds)
fig = px.line(df, x="년월", y="금액(원화)")
fig.show()



df = pd.DataFrame()
for x in ['2841909020', '8529903020', '8486204000']:
    ds=trass_ds(trade='E', hscode=x) 
    _df=gridData2df(ds)
    _df['hscode']= x
    _df['증감률']=0.0

    for row in range(1, len(_df)):
        _df['증감률'].iloc[row]=_df['금액(원화)'].iloc[row]/_df['금액(원화)'].iloc[row-1]
        
    df=pd.concat([df, _df])
    
# fig = px.line(df, x="년월", y="금액(원화)", color='hscode', line_group='hscode', hover_name='hscode')
fig = px.line(df, x="년월", y="증감률", color='hscode', line_group='hscode', hover_name='hscode')
fig.show()




# 오프라인
# 엑셀 파일 읽기 용법.ipynb



dfie=pd.read_pickle('수출입.plk')
dfie

fig = px.line(dfie, x="Unnamed: 5", y="Unnamed: 3", color='분류', line_group='분류', hover_name='분류')
fig.show()



# 엑셀 파일 읽기 용법 ###############################################
xlsx_file=r'C:\Users\haeseok\Downloads\20230911 주요품목별수출정리 9월 10일 잠정(태린이아빠).xlsx'

## pd.ExcelFile 파일 hscode 와 부가정보 가져 오기
def find_hscode_pos(ds):
    for i, x in enumerate(list(ds.columns)):
        if 'Unnamed' not in x:
            break
    return i

xl = pd.ExcelFile(xlsx_file)
# print(xl.sheet_names)
for i, x in enumerate(xl.sheet_names):
    ds=xl.parse(x)
    # print('{} sheet:{}, {}, {}'.format(i, x, ds.columns[-1], ds.iloc[0, -1]))
    loc=find_hscode_pos(ds)
    if pd.isnull(ds.iloc[1, loc]): # pd.isna(np.nan)
        comment=ds.columns[loc]
        hscode = re.sub(r'[^0-9]', '', str(ds.iloc[0, loc]))        
    else:
        hscode = re.sub(r'[^0-9]', '', str(ds.iloc[0, loc]))
        add_str = ds.iloc[1, loc]
        if len(hscode) < 10:
            hscode = re.sub(r'[^0-9]', '', str(ds.iloc[1, loc]))
            add_str = ds.iloc[0, loc]
            
        comment=str(ds.columns[loc])+' '+ str(add_str)
    
    len_hscode = len(hscode)
    if len_hscode:
        if len_hscode > 10:
            hscode = hscode[:10] + ', ' +hscode[10:]
        print('{} sheet:{}, {}, hscode:{}'.format(i, x, ds.columns[loc], hscode))
    else:
        print('**************** {} sheet:{}, {}, hscode:{}'.format(i, x, ds.columns[loc], hscode))   


## pd.ExcelFile 파일 수출입 데이터 가져오기
df_concat = pd.DataFrame()

for i, x in enumerate(xl.sheet_names):
    ds=xl.parse(x)
    if '일평균' not in ds.iloc[2][2]:    
        print(i, ds.iloc[2][2])
    else:
        _df= ds.iloc[3:,2:9]
        _df['분류']=x
        df_concat=pd.concat([df_concat, _df])
df_concat.to_pickle('수출입.plk')
