import pandas
import pythoncom
import win32com.client


class UsedArea:
    def __init__(self, used_row_start, used_row_end, used_column_start, used_column_end):
        self.used_row_start = used_row_start
        self.used_row_end = used_row_end
        self.used_column_start = used_column_start
        self.used_column_end = used_column_end


class Excel2Pydata:
    def __init__(self):
        # https://wikidocs.net/72208
        # 서브 스레드에서 COM 객체를 사용하려면 COM 라이브러리를 초기화 해야함
        pythoncom.CoInitialize()
        
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.excel.Visible = False
    
    def __del__(self):
        self.wb.Close(True)
        self.excel.Quit()
    
    def read_xl(self, workbook, sheet=None):
        
        # wb = excel.Workbooks.Open(r'F:\PycharmProjects\excel_in_nasca\181101_G975F(RJB)_G965F(RH7)_FAIL_Sluggish_sample.xlsm')
        self.wb = self.excel.Workbooks.Open(workbook)
        sheet_names = [sheet.Name for sheet in self.wb.Sheets]
        print('sheet names :', sheet_names)
        if sheet is None:
            sheetname = sheet_names[0]
        else:
            sheetname = sheet
        ws = self.wb.Worksheets(sheetname)
        # print(ws.Cells(1,1).Value)
        return ws
    
    def ws_used_top_range_trim(self, ws, top_cut_off=2):
        
        used = ws.UsedRange
        nrows = used.Row + used.Rows.Count - 1
        ncols = used.Column + used.Columns.Count - 1
        # print(type(used))
        # print(used)
        
        # for x in used:
        #     print(x)
        
        print('UsedRange', used.Row, used.Rows.Count, used.Column, used.Columns.Count)
        # print(nrows, ncols)
        # https://stackoverflow.com/questions/49501830/python-3x-win32com-copying-used-cells-from-worksheets-in-workbook
        # print(ws.UsedRange.SpecialCells(11))
        
        used_row_start = used.Row
        used_row_end = nrows
        used_column_start = used.Column
        used_column_end = ncols
        
        for i in range(used.Row, used.Row + used.Rows.Count + 1):
            column_used_count = 0
            for j in range(used.Column, used.Column + used.Columns.Count + 1):
                val = ws.Cells(i, j).Value
                if val is not None:
                    column_used_count += 1
            # print(' column_used_count', column_used_count, ncols/2, (column_used_count > ncols/2))
            # if column_used_count < ncols/2:
            if column_used_count >= top_cut_off:
                used_row_start = i
                break
        
        print('trim range', used_row_start, used_row_end, used_column_start, used_column_end)
        used_area = UsedArea(used_row_start, used_row_end, used_column_start, used_column_end)
        
        return used_area
    
    def ws_build_pattern(self, ws, used_area: UsedArea, refer_lines=0):
        
        pattern_base = []
        
        print('ws_build_pattern trim range', used_area.used_row_start, used_area.used_row_end,
              used_area.used_column_start, used_area.used_column_end)
        
        cal_rol_count = (used_area.used_row_end + 1) - used_area.used_row_start
        rol_count = min(cal_rol_count, refer_lines) + used_area.used_row_start
        # print(cal_rol_count, rol_count)
        # for i in range (used_area.used_row_start , used_area.used_row_end + 1):
        for i in range(used_area.used_row_start, rol_count):
            line = ''
            tmp = ''
            for j in range(used_area.used_column_start, used_area.used_column_end + 1):
                val = ws.Cells(i, j).Value
                if val is not None:
                    # print(j, type(val),',',end="")
                    if issubclass(type(val),
                                  str):  # https://stackoverflow.com/questions/152580/whats-the-canonical-way-to-check-for-type-in-python
                        # line = line + "{};".format(val.replace("\n", "")) #rstrip(os.linesep))
                        line = line + "{};".format(val)
                    else:
                        line = line + "{};".format(val)
                    tmp = tmp + '1'
                else:
                    # print(j,',',end="")
                    line = line + ";"
                    tmp = tmp + '0'
            # print()
            # print(line)
            pattern_base.append(tmp)
        
        return pattern_base
    
    def colum_range_trim_pattern_mask(self, pattern_base, refer_lines=0):
        base_boolean = pattern_base
        
        # print(base_boolean)
        
        line_mask = base_boolean[0]
        for x in base_boolean:
            valid = int(x)
            if valid:
                # print(valid, ' ', end='')
                for y in range(0, len(line_mask)):
                    # print(line_mask)
                    # print(x[y], end='')
                    new = str(int(line_mask[y]) or int(x[y]))
                    # print(x[y], line_mask[y], new)
                    # print(line_mask[:y] , new , line_mask[y+1:])
                    line_mask = line_mask[:y] + new + line_mask[y + 1:]
                    # print(line_mask)
            
            # print()
        
        line_mask_start = line_mask.find('1')
        mask = line_mask[line_mask_start:].rstrip('0')
        mask_len = len(mask)
        line_mask_end = line_mask_start + mask_len
        
        # print('line_mask:',line_mask)
        print('mask colum start(offset) :', line_mask_start)
        # print('mask :',mask)
        print('mask colum len :', mask_len)
        
        # for x in base_boolean:
        #     valid = int(x)
        #     if valid:
        #         print(x[line_mask_start:line_mask_end]) #, '', end='')
        #         # print(int(x[line_mask_start:line_mask_end], 2), '', end='')
        #     else:
        #         print()
        
        return (line_mask_start, mask_len)


def xl2df(xldoc, xlsheet=None):
    print(xldoc)
    excel2pydata = Excel2Pydata()
    ws = excel2pydata.read_xl(xldoc, sheet=xlsheet)
    usedarea = excel2pydata.ws_used_top_range_trim(ws, top_cut_off=2)
    pattern = excel2pydata.ws_build_pattern(ws, usedarea, refer_lines=10)
    # print(pattern)
    
    mask = excel2pydata.colum_range_trim_pattern_mask(pattern)
    # print(usedarea.used_column_start, usedarea.used_row_start, usedarea.used_column_end, usedarea.used_row_end, mask)
    StartRow, StartCol, EndRow, EndCol = (
        usedarea.used_row_start, usedarea.used_column_start + mask[0], usedarea.used_row_end,
        usedarea.used_column_start + mask[1] - 1)
    print(StartRow, StartCol, EndRow, EndCol)
    
    # https://stackoverflow.com/questions/31328861/python-pandas-replacing-header-with-top-row
    # Get the content in the rectangular selection region
    # content is a tuple of tuples
    content = ws.Range(ws.Cells(StartRow, StartCol), ws.Cells(EndRow, EndCol)).Value
    
    # Transfer content to pandas dataframe
    df = pandas.DataFrame(list(content))
    
    # new_header = df.iloc[0]  # grab the first row for the header
    # df = df[1:]  # take the data less the header row
    # df.columns = new_header  # set the header row as the df header
    
    # df.columns = df.iloc[0]
    # df = df[1:]
    
    df.rename(columns=df.iloc[0], inplace=True)
    df.drop([0], inplace=True)
    
    # https://stackoverflow.com/questions/49188960/how-to-show-all-of-columns-name-on-pandas-dataframe
    # pandas.set_option('display.max_columns', None)
    # pandas.set_option('display.max_rows', None)
    
    # print(df)
    return df
