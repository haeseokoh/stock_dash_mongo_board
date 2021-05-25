import ast
import json
import traceback

import dash
from bson import ObjectId
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table

import pandas as pd

from apps import datatable_tool_plugin, datatable_env_plugin
from libs.dash_datatable_util import datatable_rw_layout
from libs.mongo_api import db_init, DB
from libs.mongo_db_analyzer import db_read_colums_data, db_read_analyzer_data
from libs.mongo_read_util import read_contents, filter_parser_2_mongodb

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
from app import app
from utils import Header, arg_parser

def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_dic=arg_parser(arg)

    r = json.dumps({'db': arg_dic.get('db'), 'col': arg_dic.get('col'), 'state':'initial', 'arg_dic':arg_dic})
    state = json.dumps({'state': 'initial'})
    editable = (True if arg_dic.get('editable') == '1' else False)
    full = (True if arg_dic.get('full') == '1' else False)

    intermediate_value = 'intermediate_value'

    return html.Div([
        html.Div([r], id=intermediate_value, style={'display': 'none'}),
        html.Div([state], id='current_state', style={'display': 'none'}),
        html.Div([
            dbc.Row([
                dbc.Col([dbc.Input(id='my-db', value=arg_dic.get('db'), type='text', placeholder="db")], width=2),
                dbc.Col([dbc.Input(id='my-collection', value=arg_dic.get('col'), placeholder="collection", type='text')], width=2),
                dbc.Col([dbc.Button('Submit', id='submit_button')],width=1),
                dbc.Col([dbc.Checklist(options=[{'label': 'editable', 'value': True}], value=[editable], id='editable_table', inline=True, switch=True, style={'textAlign': 'center'})], width=1, align='center'),
                dbc.Col([dbc.Checklist(options=[{'label': 'full', 'value': True}], value=[full], id='full_table', inline=True, switch=True, style={'textAlign': 'center'})], width=1, align='center'),
                dbc.Col([dbc.Button("🛠", id="tool_button", color="light",),
                         dbc.Button("⚙", id="env_button", color="light", )
                         ], width=5,  style={'textAlign': 'right'}),
            ]) #,no_gutters=True)
        ]),
        html.Div([
            dbc.Collapse(dbc.Card([
                dbc.CardBody([
                    datatable_tool_plugin.get_layout(intermediate_value),
                    ])
            ]),id="tool_collapse",),
        ]),
        html.Div([
            dbc.Collapse(dbc.Card([
                dbc.CardBody([
                    datatable_env_plugin.get_layout(intermediate_value),
                    ])
            ]), id="env_collapse", ),
        ]),
        dbc.Row(dbc.Col(
            dcc.Loading(id="loading", children=[
                datatable_rw_layout(editable),
                # html.Div(id='output-loading-data-read-online')
            ], type="default"),

            )
        ),
        html.Div(id='prev-select-cell-data', style={'display': 'none'}),
    ],style={'margin': '35px'})


@app.callback(
    Output("tool_collapse", "is_open"),
    Input("tool_button", "n_clicks"),
    Input("tool_collapse", "is_open"),
)
def toggle_collapse(tool_n, tool_is_open):
    return (not tool_is_open) if tool_n else tool_is_open


@app.callback(
    Output("env_collapse", "is_open"),
    Input("env_button", "n_clicks"),
    State("env_collapse", "is_open"),
)
def toggle_collapse(env_n, env_is_open):
    return (not env_is_open) if env_n else env_is_open


# page_current
@app.callback(Output('output-data-read-online', 'data'),
              Output('output-data-read-online', 'tooltip_data'),
              Output('output-data-read-online', 'columns'),
              Output('output-data-read-online', 'page_action'),
              Output('output-data-read-online', 'page_current'),
              Output('output-data-read-online', 'page_size'),
              Output('output-data-read-online', 'page_count'),
              Output('output-data-read-online', 'editable'),
              Output('current_state', 'children'),
              Input('submit_button', 'n_clicks'),
              Input('output-data-read-online', 'page_action'),
              Input('output-data-read-online', 'page_current'),
              Input('output-data-read-online', "filter_query"), # https://stackoverflow.com/questions/56259327/dash-datatable-conditional-cell-formatting-isnt-working # presetting도 가능 할 듯
              Input('output-data-read-online', "sort_by"),
              Input('editable_table', 'value'),
              Input('full_table', 'value'),
              Input('dropdown-trans-dash-datatable-filter-format', 'children'),
              State('my-db', 'value'),
              State('my-collection', 'value'),
              State('intermediate_value', 'children'),
              State('current_state', 'children'),
              )
def update_output(n_clicks, page_action, page_current, filter_query, sort_by, editable_table, full_table, dropdown_filter, db, collection, intermediate_value, current_state):
    print('update_output parm: n_clicks:{}, page_action:{} page_current{}, filter_query:{}, sort_by:{}, editable_table:{}, full_table:{}, dropdown_filter:{}, db:{}, collection:{}, current_state:{}'.format(n_clicks, page_action, page_current, filter_query, sort_by, editable_table, full_table, dropdown_filter, db, collection, current_state))
    joined_filter= dropdown_filter + ' && ' + filter_query

    full_table=True if 'True' in str(full_table) else False
    print("full_table, 'True' in full_table", full_table)
    # full_table=False
    
    d = json.loads(intermediate_value[0])

    if 'initial' in current_state[0]:
        dropdown_filter_split = dropdown_filter.split(' && ')
        arg_dic_tool_Dropdown = d.get('arg_dic').get('tool_Dropdown').split(' and ') if d.get('arg_dic').get('tool_Dropdown') else []
        # print('----------- initial :', dropdown_filter_split, arg_dic_tool_Dropdown)
        if dropdown_filter_split[:len(arg_dic_tool_Dropdown)] == arg_dic_tool_Dropdown:
            # print('----------- initial complete!!!')
            current_state=[json.dumps({'state': 'prepared'})]
        else:
            return None, None, None, 'custom', 0, 0, 0, None, current_state
            
    myquery, sort = filter_parser_2_mongodb(joined_filter, sort_by, editable_table)

    # https://stackoverflow.com/questions/61607713/how-can-i-implement-the-dash-callback-context-function-in-django-ploty-dash-envi
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'submit_button':
        page_current = 0
        
    data, columns, tooltip_data, page_size, page_count = read_contents(db, collection, 20, page_current, myquery=myquery, sort=sort, full=full_table)
    
    if page_current > page_count:
        page_current = 0
        if not full_table:
            data, columns, tooltip_data, page_size, page_count = read_contents(db, collection, 20, page_current, myquery=myquery, sort=sort, full=full_table)

    page_action = 'native' if full_table else 'custom'
    print('data len:{}, tooltip_data len:{}, page_size:{}, page_count:{}, page_action:{}'.format(len(data), len(tooltip_data), page_size, page_count, page_action))
    return data, tooltip_data, columns, page_action, page_current, page_size, page_count, any(editable_table), current_state


@app.callback(
    Output('prev-select-cell-data', 'children'),
    Input('output-data-read-online', 'data'),
    Input('output-data-read-online', 'selected_row_ids'),
    Input('output-data-read-online', 'active_cell'),
    State('prev-select-cell-data', 'children'),
    State('my-db', 'value'),
    State('my-collection', 'value'),
)
def write_table(rows, selected_row_ids, active_cell, prev_cell_info_json, db, collection):
    
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
                if hasattr(db, 'db_col'):
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