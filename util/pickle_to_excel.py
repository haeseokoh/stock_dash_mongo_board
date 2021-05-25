import os
import random
import string
from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

location = r"D:\project\pythonProject\dash_4_google_play\data\test_data_2\\"

def pkl_to_excel(writeto, filename, sheet, unique_field):
    df = pd.read_pickle(location + filename + r'.pkl')
    print(df)
    df.to_excel(writeto, sheet_name=sheet, index=False)
    # writer = pd.ExcelWriter(writeto, engine='xlsxwriter')

def pkl_to_excel_add_sheet(writeto, filename, sheet, unique_field):
    df = pd.read_pickle(location + filename + r'.pkl')
    # print(df)
    # df.to_excel(writeto, sheet_name=sheet)
    # writer = pd.ExcelWriter(writeto, engine='xlsxwriter')
    book = load_workbook(writeto)
    writer = pd.ExcelWriter(writeto, engine='openpyxl')
    writer.book = book
    df.to_excel(writer, sheet_name=sheet, index=False)
    writer.save()
    writer.close()

    print(df)


# pkl_to_excel(r'DEFECT_LIST_20210421_tracking+board (2).xlsx', 'test_data' ,'None', '사례코드')
# pkl_to_excel_add_sheet(r'담당자분류샘플 (2).xlsx', 'test_data2', '담당자', '등록자 E-Mail')
# pkl_to_excel_add_sheet(r'담당자분류샘플 (2).xlsx', 'test_data3', '파트분류', '파트장')
# pkl_to_excel_add_sheet(r'담당자분류샘플 (2).xlsx', 'test_data4', 'Feature별', 'Feature명' )


pkl_to_excel(r'담당자분류샘플.xlsx', 'test_data2', '담당자', '등록자 E-Mail')
pkl_to_excel_add_sheet(r'담당자분류샘플.xlsx', 'test_data3', '파트별', '파트장')
pkl_to_excel_add_sheet(r'담당자분류샘플.xlsx', 'test_data4', 'Feature별', 'Feature명' )