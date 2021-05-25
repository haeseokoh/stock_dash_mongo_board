# https://stackoverflow.com/questions/53418221/read-multiple-excel-files-and-storing-data-in-dictionary-win32
# https://pythonexcels.com/python/2009/10/05/python-excel-mini-cookbook
import datetime, dateutil, pywintypes
import os
import traceback

import pymongo
import pythoncom

import win32com.client as win32
from pathlib import Path
import sys
import pandas as pd
from win32com.universal import com_error

from app_config import *
from libs.mongo_api import db_init, db_update2

win32c = win32.constants


# print(list(string.ascii_lowercase))
# print(list(string.ascii_uppercase))
# https://stackoverflow.com/questions/23861680/convert-spreadsheet-number-to-column-letter
def colnum_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

class excel_util:
    
    def __init__(self, f_path: Path, f_name: str, visible = False):
        self.filename = os.path.join(f_path,f_name)
        
        print(self.filename)

        # 서브 스레드에서 COM 객체를 사용하려면 COM 라이브러리를 초기화 해야함
        pythoncom.CoInitialize()
        
        # create excel object
        self.excel = win32.gencache.EnsureDispatch('Excel.Application')

        # excel can be visible or not
        self.excel.Visible = visible #True  # False
        
        # try except for file / path
        try:
            self.wb = self.excel.Workbooks.Open(self.filename)
        except com_error as e:
            if e.excepinfo[5] == -2146827284:
                print(f'Failed to open spreadsheet.  Invalid filename or location: {self.filename}')
            else:
                raise e
            sys.exit(1)
            
    
    def sheet_names(self) -> list:
        # get worksheet names
        sheet_names = [sheet.Name for sheet in self.wb.Sheets]
        
        return sheet_names

    def sheet_UsedRange(self, sheet):
        curr_sheet = self.wb.Worksheets(sheet)
        used = curr_sheet.UsedRange
        nrows = used.Row + used.Rows.Count - 1
        ncols = used.Column + used.Columns.Count - 1
        return nrows, ncols


    def __del__(self):
        self.wb.Close(True)
        self.excel.Quit()

        # 사용 후 uninitialize
        pythoncom.CoUninitialize()

def exceltimetype2df(dst, x):
    # https://item4.blog/2015-07-18/Some-Ambiguousness-in-Python-Tutorial-Call-by-What/
    today_year = str(datetime.datetime.today().year)

    try:
        if isinstance(dst[x], pywintypes.TimeType):
            # https://stackoverflow.com/questions/51770144/assign-array-of-datetime-type-into-panda-dataframe
            dst[x] = dateutil.parser.parse(str(dst[x])).replace(tzinfo=None)
        elif isinstance(dst[x], str):
            if '년' not in dst[x] and '월' in dst[x] and '일' in dst[x]:
                # https://stackoverflow.com/questions/57395248/attributeerror-pywintypes-datetime-object-has-no-attribute-nanosecond
                dst[x] = datetime.datetime.strptime(today_year + dst[x].replace(' ', ''), "%Y%m월%d일").replace(tzinfo=None)
            else:
                dst[x] = str(dst[x])
                print('exceltimetype2df bad format : ', dst[x])
    except:
        print('exceltimetype2df except :',dst[x])
        traceback.print_exc(file=sys.stdout)


if __name__ == "__main__":
    # file path
    f_path = Path.cwd()  # file in current working directory
    # f_path = Path(r'c:\...\Documents')  # file located somewhere else
    
    # excel file
    f_name = '시장VOC_종합현황판_Final_ver.xlsx'
    
    # function call
    myexcel = excel_util(f_path, f_name)

    sheet_names = myexcel.sheet_names()

    for x in sheet_names:
        print(x, myexcel.sheet_UsedRange(x))

    sheet_name = MAIN_SHEETNAME
    nrows, ncols = myexcel.sheet_UsedRange(sheet_name)
    # nrows, ncols
    print('nrows, ncols',nrows, ncols, colnum_string(ncols))
    
    
    worksheet = myexcel.wb.Worksheets(sheet_name)
    
    DataTemp = []
    
    print(dir(worksheet))
    #Read all data
    DataTuple_catagory = worksheet.Range("A1:{}1".format(colnum_string(ncols))).Value[0]
    print('DataTuple_catagory:',DataTuple_catagory)

    DataTuple = worksheet.Range("A2:{}{}".format(colnum_string(ncols), nrows)).Value
    DataList = [list(x) for x in DataTuple]
    for rowA in DataList:
        for x in rowA[1:10]:
            if x is not None:
                try:
                    DataTemp.append(rowA)
                except:
                    print(rowA[2],rowA[24])
                    print('except:',rowA)
                break

    for rowA in DataTemp:
        rowA[0] = int(rowA[0])
        exceltimetype2df(rowA, [2, 20, 24])
    
    for rowA in DataTemp:
        print(rowA)
    
    print(len(DataTemp))
    # df = pd.DataFrame(DataTemp, columns=DataTuple_catagory)
    
    # 표의 첫행의 경우 DB에 없데이트 할 경우의 필드 네임으로 그대로 사용할 수 없는 경우가 많아서 액셀의 행을 나타내는 A, B .. 씩으로 변환한다
    dummy_DataTuple_catagory = []
    for x in range(1, ncols + 1):
        dummy_DataTuple_catagory.append(colnum_string(x))
    df = pd.DataFrame(DataTemp, columns=dummy_DataTuple_catagory)
    # print(df)
    df.to_pickle("_pd.pkl")
    # df.to_excel("_pd.xlsx")

    db_aqi_market_issue = db_init(MONGODB_NAME, "market_issue_status")
    # https://stackoverflow.com/questions/52697153/how-to-avoid-inserting-duplicate-values-in-the-collection-using-db-insertmany
    # efining the model schema you can specify which field is unique
    # db_update(db_aqi_market_issue, df, 'A')

    # db_comment.db_col.create_index('A',unique=True)
    db_aqi_market_issue.db_col.create_index([("A", pymongo.ASCENDING)],unique=True)
    db_update2(db_aqi_market_issue, df, 'A')
