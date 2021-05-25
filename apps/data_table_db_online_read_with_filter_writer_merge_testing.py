import base64
import datetime
import json
import os
import random
import re
import string
import traceback

import dash
from bson import ObjectId
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd

from libs.mongo_api import db_init, db_update2, db_update3, db_update4
from libs.xl2dataframe import xl2df

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
from app import app
from utils import Header, arg_parser

# @app.callback(Output('my-db', 'value'),
#               State('my-db', 'value')
#               )
# def set_db(value):
#     return

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['and '],
             ['or ',],
             ['contains '],
             ['datestartswith '],
             ]



def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_list=arg_parser(arg)

    return html.Div([
        html.Div([
            "db: ", dcc.Input(id='l-db', value=arg_list.get('db'), type='text', style={"margin-right": "15px"}),
            "collection: ", dcc.Input(id='l-collection', value=arg_list.get('col'), type='text', style={"margin-right": "15px"}),
            "ref collection: ", dcc.Input(id='f-collection', value=arg_list.get('f_col'), type='text', style={"margin-right": "15px"}),
            "field: ", dcc.Input(id='l-field', value=arg_list.get('field'), type='text', style={"margin-right": "15px"}),
            "ref field: ", dcc.Input(id='f-field', value=arg_list.get('f_field'), type='text', style={"margin-right": "15px"}),
            html.Button('Submit', id='button'),
        ]),
        dash_table.DataTable(
            id='output-data-view-online',
            data=[],
            
            page_current=0,
            page_action='custom',
            
            filter_action='custom',
            filter_query='',
    
            sort_action='custom',
            sort_mode='multi',
            sort_by=[],
        
            editable=True,
            # row_selectable='multi',
            # row_deletable=True
        ),
        html.Div(id='prev-select-cell-data-view', style={'display': 'none'}),
    ])


def rearrange_filter_part(filter_part):
    for x in ['and', 'or']:
        test_set = 'contains "{}'.format(x)
        if test_set in filter_part:
            name_part, value_part = filter_part.split(' contains "', 1)
            # print('rearrange_filter_part:','{} {}'.format(name_part,value_part[:-1]))
            return '{} {}'.format(name_part, value_part[:-1])
    
    return filter_part


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

def mongodb_filter_simple_build(col_name, query_string, multi_oper='$or'):

    myquery = {col_name: {multi_oper:query_string}}
    return myquery


def mongodb_filter_build(col_name, query_string, multi_oper='$or'):
    print(col_name, query_string)
    # split_order = r'[^,\s]+'
    split_order = r'[^,]+'
    search_re = r".*(?=.*{}).*"  # r"^(?=.*{}).*" missing "/nXXXXX" cass

    myquery = {multi_oper: []}
    key = col_name
    print(re.findall(split_order, query_string))
    for x in re.findall(split_order, query_string):
        regexr = search_re.format(x.strip())
        regexri = re.compile(regexr, re.IGNORECASE)
        item = {key: {"$regex": regexri}}
        myquery[multi_oper].append(item)

    return myquery

def read_contents_lookup(db, collection, f_col, field, f_field, page_view_size, offset, myquery = {}, sort = []):
    print(db, collection, f_col, field, f_field, page_view_size, offset)
    
    data = []
    columns = []
    page_count = 0

    try:
    # if 1:
        db_inst = db_init(db, collection)
        
        # myquery = {}
        # sort_t = []
        # print(myquery, sort_t)

        # # 컬럼의 정보가 저장되어 있으면 저장된 정보를 바탕으로 재정렬하여 가져온다
        # columns_order = {}
        # db_config_inst = db_init(db, collection+'_option')
        # if collection+'_option' in db_config_inst.db_name.list_collection_names():
        #     x = db_config_inst.db_col.find_one(filter={'value': 'columns'})
        #     print('------------x', x.get('option'))
        #     if x.get('option'):
        #         columns = x.get('option')
        # else:
        #     # columns = list(db_inst.find(myquery).next().keys())
        #     # query 결과가 없으면 컬럼 이름과 필터가 사라진다
        #     columns=list(db_inst.find({}).next().keys())
        #
        # for x in columns:
        #     columns_order[x] = 1
        # print('columns_order :', columns_order)

        # print(db_inst.find(myquery))

        # if len(sort):
        #     cursor = db_inst.find_select(myquery, columns_order).sort(sort)
        # else:
        #     cursor = db_inst.find_select(myquery, columns_order)
    
        cursor = db_inst.aggregate(f_col=f_col, l_field=field, f_field=f_field)
        # for x in list(cursor):
        #     print(x)

        # columns = list(cursor.next().keys())
        
        # total_size = db_inst.db_col.count_documents(myquery)
    
        for x in cursor:
            x['_id'] = '{}'.format(x['_id'])
            data.append(x)
        # data = list(cursor)

        # columns = data[0].keys()
        df = pd.DataFrame(data)
        print(df)
        columns = df.columns
        
        total_size = len(data)
        print('total_size:',total_size,'columns:',columns,)

        # if page_view_size is not None:
        #     for x in cursor.skip(page_view_size * offset).limit(page_view_size):
        #         x['_id'] = '{}'.format(x['_id'])
        #         # if x.get('duration'):
        #         #     del x['duration']
        #         data.append(x)
        # else:
        #     data = list(cursor)

        print(data[:10])

        div, mod = divmod(total_size, page_view_size)
        page_count = div + (1 if mod else 0)
        
        # return data, [{'name': i, 'id': i} for i in columns], page_view_size, page_count
    
    except Exception as e:
        print(e)
        traceback.print_exc()
        # return [], [], 0, 0

    return data[:100], [{'name': i, 'id': i} for i in columns], page_view_size, page_count

# page_current
@app.callback(Output('output-data-view-online', 'data'),
              Output('output-data-view-online', 'columns'),
              Output('output-data-view-online', 'page_size'),
              Output('output-data-view-online', 'page_count'),
              Input('button', 'n_clicks'),
              Input('output-data-view-online', 'page_current'),
              Input('output-data-view-online', "filter_query"),
              Input('output-data-view-online', "sort_by"),
              State('l-db', 'value'),
              State('l-collection', 'value'),
              State('f-collection', 'value'),
              State('l-field', 'value'),
              State('f-field', 'value'),
              )
def update_output(n_clicks, page_current, filter_query, sort_by,  db, collection, f_col, field, f_field):
    # https://dash.plotly.com/datatable/callbacks  ... Backend Paging with Filtering and Multi-Column Sorting
    filtering_expressions = filter_query.split(' && ')
    print('filtering_expressions:',filtering_expressions, 'filter_query:',filter_query)

    myquery = {"$and": []}

    for filter_part in filtering_expressions:
        filter_part = rearrange_filter_part(filter_part)
        col_name, operator, filter_value = split_filter_part(filter_part)
        print("col_name:{}  operator:{}  filter_value:{}".format(col_name, operator, filter_value))

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            myquery_inner = mongodb_filter_simple_build(col_name, filter_value, '$'+operator)
            myquery["$and"].append(myquery_inner)
        elif operator == 'contains' or operator == 'or':
            myquery_inner = mongodb_filter_build(col_name, filter_value)
            myquery["$and"].append(myquery_inner)
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            pass
        elif operator == 'and':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            myquery_inner = mongodb_filter_build(col_name, filter_value, multi_oper='$and')
            myquery["$and"].append(myquery_inner)

    # check filtering_expressions: ['']
    if myquery["$and"]==[]:
        myquery = {}

    print('update_output myquery :', myquery)


    sort=[]
    if len(sort_by):
        print([col['column_id'] for col in sort_by], [col['direction'] for col in sort_by] )
        # [('prj_name', 1), ('model_name', -1)]
        for col in sort_by:
            if col['direction']=='asc':
                sort.append((col['column_id'], 1))
            elif col['direction']=='desc':
                sort.append((col['column_id'], -1))
                
    print('update_output sort :', sort)
    data, columns, page_size, page_count = read_contents_lookup(db, collection, f_col, field, f_field, 20, page_current, myquery=myquery, sort=sort)
    return data, columns, page_size, page_count


@app.callback(
    Output('prev-select-cell-data-view', 'children'),
    Input('output-data-view-online', 'data'),
    Input('output-data-view-online', 'columns'),
    Input('output-data-view-online', 'derived_virtual_row_ids'),
    Input('output-data-view-online', 'selected_row_ids'),
    Input('output-data-view-online', 'active_cell'),
    Input('output-data-view-online', 'start_cell'),
    Input('output-data-view-online', 'end_cell'),
    Input('output-data-view-online', 'selected_cells'),
    State('prev-select-cell-data-view', 'children'),
    State('l-db', 'value'),
    State('l-collection', 'value'),
)
def display_output(rows, columns, row_ids, selected_row_ids, active_cell, start_cell, end_cell, selected_cells, prev_cell_info_json, db, collection):
    selected_id_set = set(selected_row_ids or [])

    select_cell_info = json.dumps({})

    if rows!=None and active_cell!=None:
        if prev_cell_info_json==None:
            prev_cell_info = {}
        else:
            prev_cell_info = json.loads(prev_cell_info_json)

        if prev_cell_info.get('row') is not None:
            curret_cell_data = rows[prev_cell_info.get('row')].get(prev_cell_info.get('column_id'))
            
            if curret_cell_data != prev_cell_info.get('data'):
                print('prev_cell_data', prev_cell_info)
                print('curret_cell_data', curret_cell_data)
                print('--need to update!!')
                db = db_init(db, collection)
                doc = db.update_one(
                    {"_id" : ObjectId(prev_cell_info.get('_id'))},
                    {"$set":{prev_cell_info.get('column_id'): curret_cell_data}}
                )
                print('update_one return:', doc)

        select_cell_id = rows[active_cell['row']]['_id']
        if rows[active_cell['row']].get(active_cell['column_id']):
            select_cell_data = rows[active_cell['row']][active_cell['column_id']]
        else:
            select_cell_data = ''

        active_cell['_id']=select_cell_id
        active_cell['data']=select_cell_data
        select_cell_info = json.dumps(active_cell)

    return select_cell_info