import base64
import datetime
import os
import random
import string
import traceback

import dash
import pymongo
import pywintypes
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from pathlib import Path
import pandas as pd
import numpy as np
from dateutil.parser import parser

from libs.dash_datatable_util import try_parsing_date
from libs.mongo_api import db_init, db_update2, db_update3, db_update4, db_update5
from libs.xl2dataframe import xl2df
from utils import *

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
from app import app

def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_list=arg_parser(arg)
    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Col([dbc.Input(id='my-db', value=arg_list.get('db'), type='text', placeholder="db")], width=2),
                dbc.Col([dbc.Input(id='my-collection', value=arg_list.get('col'), placeholder="collection", type='text')], width=2),
                dbc.Col([dbc.Input(id='unique_field', value=arg_list.get('unique'), placeholder="unique field", type='text')], width=2),
                ])
            
        ]),
        dbc.Row(dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    # 'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            dcc.Loading(id="loading", children=[html.Div(id='output-data-upload')], type="default"),
            
        ]))
    ],style={'margin': '35px'})



def parse_contents(contents, filename, date, db, collection, unique_field):
    print(db, collection, unique_field)

    # content_type, content_string = contents.split(',')
    #
    # decoded = base64.b64decode(content_string)
    try:
    # if 1:
        # if 'csv' in filename:
        #     # Assume that the user uploaded a CSV file
        #     df = pd.read_csv(
        #         io.StringIO(decoded.decode('utf-8')))
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     df = pd.read_excel(io.BytesIO(decoded))
        content_type, content_string = contents.split(',')
        # print(filename, date, content_type)
        # print(content_string)
        decoded = base64.b64decode(content_string)
        # print(decoded)

        print(os.getcwd())

        full_path = os.path.join(os.getcwd(), 'uploaded_temp')
        # https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
        Path(full_path).mkdir(parents=True, exist_ok=True)

        full_name = ''.join(random.choice(string.ascii_lowercase) for i in range(16)) + filename

        with open(full_path + '\\' + full_name, 'wb') as f:
            f.write(decoded)

        tmp_excel = os.path.join(full_path, full_name)
        df = xl2df(tmp_excel)  # 담당자 파트분류, Feature별
        # print(df)
        if os.path.exists(tmp_excel):
            os.remove(tmp_excel)


        # https://stackoverflow.com/questions/42295767/how-to-correctly-use-fillna-for-a-datetime-column-in-pandas-dataframe-not-wor
        # print(df.dtypes)

        # None to ''  <- fillna('')처리를 하지 않으면 astype(str)이후 'None'으로 처리 된다
        df = df.fillna('')


        # df["at"] = df["at"].dt.tz_convert(None)
        # https://stackoverflow.com/questions/42295767/how-to-correctly-use-fillna-for-a-datetime-column-in-pandas-dataframe-not-wor
        # print(df.dtypes)
        for colname, coltype in df.dtypes.iteritems():
            print( colname, coltype)
            # if 'datetime' in coltype:
            # if np.issubdtype(df[colname].dtype, np.datetime64):
            if isinstance(df[colname].dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
                df[colname] = df[colname].dt.tz_convert(None)

        df_columns = df.columns.to_list()
        print(df_columns)
        #
        # for row in df.itertuples(index=False): # While iterrows() is a good option, sometimes itertuples() can be much faster:
        # TypeError: tuple indices must be integers or slices, not str
        for index, row in df.iterrows():
            # print(row)
            for colname in df_columns:
                # print(index, row[colname], type(row[colname]))
                # if isinstance(row[colname], pd.core.dtypes.dtypes.DatetimeTZDtype):
                #     row[colname] = row[colname].dt.tz_convert(None)
                if str(row[colname]).endswith('+00:00'): # pywintypes.datetime pywintypes.TimeType
                    # print(colname, str(row[colname]))
                    # row[colname] = str(row[colname]).rstrip("+00:00").strip()
                    value = str(row[colname]).rstrip("+00:00").strip()
                    # A value is trying to be set on a copy of a slice from a DataFrame -> df.iloc[index-1][colname] = value
                    # df.loc[index, colname] = value
                    # df['dates'] = pd.to_datetime(df['dates'], format='%Y%m%d%H%M%S')
                    # df.loc[index, colname] = value.astype('datetime64[ns]')
                    # df.loc[index, colname] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M')

                    df.loc[index, colname] = try_parsing_date(value)
                    #
                    # try:
                    #     df.loc[index, colname] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                    # except ValueError as v:
                    #     print('ValueError v:', v)
                    #     datetime_obj = parser.parse(value)
                    #     print('datetime_obj:',datetime_obj)
                    #     # https://stackoverflow.com/questions/5045210/how-to-remove-unconverted-data-from-a-python-datetime-object
                    #     # v.args[0].partition()

        # df = df.astype(str, skipna=True)
        # df = df.astype(str)
        # print(df.columns.to_list())
        # print(df.head(100))

    # *************************************************************************************************************
        # remove characters are NOT allowed in MongoDB field names
        _columns = []
        for x in df.columns.to_list():
            # todo: mongodb에서 .은 하위 카테고리로 분류 하게 되어 오류를 발생 시키는 듯함
            _columns.append(x.rstrip('.').replace('.', '').replace('\n', ' '))
        df.columns = _columns

        db_option = db_init(db, collection+'_option')
        db_option.db_col.create_index('value', unique=True)
        db_option.db_col.update_one({'value': 'columns'}, {"$set": {'value':'columns', 'option':_columns }}, upsert=True)

        db = db_init(db, collection)
        db.db_col.create_index(unique_field, unique=True)
        db_update4(db, df, unique_field)


    except Exception as e:
        print(e)
        traceback.print_exc()
        return html.Div([
            html.H5(full_name),
            'There was an error processing this file.',
        ])


    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=10,
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              State('my-db', 'value'),
              State('my-collection', 'value'),
              State('unique_field', 'value'),
              )
def update_output(list_of_contents, list_of_names, list_of_dates, db, collection, unique_field):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d, db, collection, unique_field) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
