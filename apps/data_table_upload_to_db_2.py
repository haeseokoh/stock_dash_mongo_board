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
from pymongo import MongoClient

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
                dbc.Col([dbc.Input(id='excel_sheet', value=arg_list.get('sheet'), placeholder="sheet(optional)", type='text')], width=2),
                dbc.Col([dbc.Input(id='unique_field', value=arg_list.get('unique'), placeholder="unique field", type='text')], width=2),
                ])
            
        ]),
        html.Div(
            upload_data_get_layout()
        ,id='upload-data-output'),
        dbc.Row(dbc.Col([
            dcc.Loading(id="loading", children=[html.Div(id='output-data-upload-2')], type="default"),
        ]))
    ],style={'margin': '35px'})

def upload_data_get_layout():
    return dbc.Row(dbc.Col([
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
    ]))

def write_df_to_mongoDB(df, database_name='test', collection_name='test_collectionname', sheet=None, server='localhost',
                        mongodb_port=27017, chunk_size=100, destroy=False, unique_field=None):
    
    client = MongoClient(server, int(mongodb_port))
    db = client[database_name]
    collection = db[collection_name]
    collection_option = db[collection_name + '_option']
    # To write
    if destroy:
        collection.delete_many({})  # Destroy the collection
    # #aux_df=aux_df.drop_duplicates(subset=None, keep='last') # To avoid repetitions
    
    _columns = []
    for x in df.columns.to_list():
        # todo: mongodb에서 .은 하위 카테고리로 분류 하게 되어 오류를 발생 시키는 듯함
        _columns.append(x.rstrip('.').replace('.', '').replace('\n', ' '))
    df.columns = _columns
    # df = df.fillna('')
    
    df2dict = df.to_dict(orient='records')  # Here's our added param..
    
    # https://stackoverflow.com/questions/37435589/insert-many-with-upsert-pymongo
    if unique_field != None:
        _db = db_init(database_name, collection_name)
        _db.db_col.create_index(unique_field, unique=True)
        db_update4(_db, df, unique_field)
    else:
        collection.insert_many(df2dict)
    
    collection_option.update_one({'value': 'columns'}, {"$set": {'value': 'columns', 'option': _columns}}, upsert=True)
    
    print('write_df_to_mongoDB Done')
    return


def parse_contents(contents, filename, date, db, collection, sheet, unique_field):
    print(db, collection, unique_field)

    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        print(os.getcwd())

        full_path = os.path.join(os.getcwd(), 'uploaded_temp')
        # https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
        Path(full_path).mkdir(parents=True, exist_ok=True)

        full_name = ''.join(random.choice(string.ascii_lowercase) for i in range(16)) + filename

        with open(full_path + '\\' + full_name, 'wb') as f:
            f.write(decoded)

        tmp_excel = os.path.join(full_path, full_name)

        if sheet:
            # df = pd.read_excel(filename, sheetname=sheet)
            xls = pd.ExcelFile(tmp_excel)
            df = pd.read_excel(tmp_excel, sheet)
        else:
            df = pd.read_excel(tmp_excel)
        # print(df)
        if os.path.exists(tmp_excel):
            os.remove(tmp_excel)

        # print(df)
        # df.reset_index(drop=True, inplace=True)
        # print(df.loc[0, :].values.tolist())
        # print(type(df.columns.to_list()))
        
        if unique_field in df.columns.to_list():
            pass
        else:
            for x in range(0,len(df)):
                # print('------- df.loc[x, :]',x)
                _columns = df.loc[x, :].values.tolist()
                if unique_field in _columns:
                    df.columns = _columns
                    df.drop([i for i in range(0,x+1)], inplace=True)
                    # df.reset_index(drop=True, inplace=True)
                    break

        df.dropna(axis='index', how='all', inplace=True)
        # df.to_pickle(full_path + '\\' +filename+'.pkl')

        #
        # print(df.columns.to_list())
        # print(df.loc[0, :].values.tolist())
        # print(df.loc[1, :].values.tolist())
        # print(df.loc[2, :].values.tolist())
        # for x in range(0,len(df)):
        #     print(df.loc[x, :].values.tolist())

        # None to ''  <- fillna('')처리를 하지 않으면 astype(str)이후 'None'으로 처리 된다
        df = df.fillna('')
        write_df_to_mongoDB(df, database_name=db, collection_name=collection, sheet=sheet, server='localhost', mongodb_port=27017, chunk_size=100, destroy=False, unique_field=unique_field)

    # *************************************************************************************************************

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


@app.callback(
    Output('upload-data-output', 'children'),
    Input('output-data-upload-2', 'children')
)
def upload_data_layout_reflash(children):
    return upload_data_get_layout()

@app.callback(
    Output('output-data-upload-2', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('upload-data', 'last_modified'),
    State('my-db', 'value'),
    State('my-collection', 'value'),
    State('excel_sheet', 'value'),
    State('unique_field', 'value'),
    )
def update_output(list_of_contents, list_of_names, list_of_dates, db, collection, sheet, unique_field):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d, db, collection, sheet, unique_field) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
