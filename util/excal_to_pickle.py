import os
import random
import string
from pathlib import Path
import pandas as pd


def parse_contents(filename, writeto, sheet, unique_field):
    
    if sheet:
        # df = pd.read_excel(filename, sheetname=sheet)
        xls = pd.ExcelFile(filename)
        df = pd.read_excel(xls, sheet)
    else:
        df = pd.read_excel(filename)

    if unique_field in df.columns.to_list():
        pass
    else:
        for x in range(0 ,len(df)):
            # print('------- df.loc[x, :]',x)
            _columns = df.loc[x, :].values.tolist()
            if unique_field in _columns:
                df.columns = _columns
                df.drop([i for i in range(0 , x +1)], inplace=True)
                # df.reset_index(drop=True, inplace=True)
                break
    
    df.dropna(axis='index', how='all', inplace=True)
    df.to_pickle(writeto+'.pkl')
    print(df)
    
parse_contents(r'C:\Users\haeseok\Downloads\DEFECT_LIST_20210421_tracking+board (2).xls', 'test_data' ,None, '사례코드')
parse_contents(r'C:\Users\haeseok\Downloads\담당자분류샘플 (2).xlsx', 'test_data1', '문제점 list', '사례코드')
parse_contents(r'C:\Users\haeseok\Downloads\담당자분류샘플 (2).xlsx', 'test_data2', '담당자', '등록자 E-Mail')
parse_contents(r'C:\Users\haeseok\Downloads\담당자분류샘플 (2).xlsx', 'test_data3', '파트분류', '파트장')
parse_contents(r'C:\Users\haeseok\Downloads\담당자분류샘플 (2).xlsx', 'test_data4', 'Feature별', 'Feature명' )
