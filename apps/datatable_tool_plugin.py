import ast
import json
import traceback
from pprint import pprint

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dateutil
from dash.dependencies import Input, Output, State, ALL
import pandas as pd

from app import app
from libs.mongo_api import db_init
from libs.mongo_db_analyzer import db_analyzer, db_read_colums_data, db_read_analyzer_data
from libs.mongo_read_util import split_filter_part


def get_layout(intermediate_value):

    return html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='append_select'),
            ]),
            dbc.Col([
                dbc.Button("➕", id="append_button", color="light", ),
                dbc.Button("➖", id="remove_last_button", color="light", ),
            ], width=2, style={}), # style={'textAlign': 'right'}
            dbc.Col([
                dbc.Button("🔄", id="reflsh_button", color="light", )
            ], width=1, style={}),  # style={'textAlign': 'right'}
        ]),
        html.Div(id='dropdown-container', children=[]),
        html.Div(id='dropdown-select-initial-value', style={'display': 'none'}), # style={'display': 'none'}
        # html.Div(id='dropdown-selector-output'),
        html.Div(id='dropdown-select-value', style={'display': 'none'}),
        html.Div('',id='dropdown-trans-dash-datatable-filter-format', style={'display': 'none'}),
        html.Div('',id='dropdown-trans-dash-datatable-url-format'),
        html.Div(id='dropdown-anlayze-output'),
    ])


# 초기화시 db로 부터 데이터를 읽어와 초기화 해야 할 부분은 모두 이곳에 ...
@app.callback(
    Output('intermediate_value', 'children'),
    Output('append_select', 'options'),
    Output('dropdown-select-initial-value', 'children'),
    Output('dropdown-anlayze-output', 'children'),
    Input('reflsh_button', 'n_clicks'),
    Input('submit_button', 'n_clicks'), # view&writer 메뉴에서 db.col을 입력한 후 analyzer_data 가져오려면 있어야 한다
    State('my-db', 'value'),
    State('my-collection', 'value'),
    State('intermediate_value', 'children'),
)
def anlayze_db(reflsh, submit, db, col, intermediate_value):
    ctx = dash.callback_context
    print('anlayze_db ctx :', ctx.triggered, ctx)

    # if not ctx.triggered:
    #     return ""

    options = []
    dropdown_initial = None
    total_size = 0

    print('anlayze_db :', reflsh, intermediate_value)

    # if reflsh:
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'reflsh_button':
        options,total_size = db_analyzer(db, col, intermediate_value)
    else:
    # elif ctx.triggered[0]['prop_id'].split('.')[0] == 'submit_button':
        intermediate_value = db_read_colums_data(db, col, intermediate_value)
        intermediate_value = db_read_analyzer_data(db, col, intermediate_value)
        d = json.loads(intermediate_value[0])
        if d.get('anlayze_db'):
            options = d.get('anlayze_db')
        dropdown_initial = d.get('arg_dic').get('tool_Dropdown')

    return intermediate_value, options, dropdown_initial,html.Div([
        # html.Pre(json.dumps({
        # 'states': ctx.states,
        # 'triggered': ctx.triggered,
        # 'inputs': ctx.inputs
        # }, indent=2)),
        html.Div('total : {}'.format(total_size)),
        # html.Pre(json.dumps({'intermediate_value': d}, indent=2)),
    ])

@app.callback(
    Output('dropdown-container', 'children'),
    Output('append_button', 'n_clicks'),
    Output('remove_last_button', 'n_clicks'),
    Input('append_button', 'n_clicks'),
    Input('remove_last_button', 'n_clicks'),
    Input('dropdown-select-initial-value', 'children'),
    State('dropdown-container', 'children'),
    State('append_select', 'value'),
    State('intermediate_value', 'children'),
    State('current_state', 'children'),
)
def display_dropdowns(append, remove, dropdown_initial,  children, value, intermediate_value, current_state):
    print('display_dropdowns :', append, remove, dropdown_initial, value, current_state )

    if value is None and dropdown_initial is None:
        return children, 0, 0

    # http://127.0.0.1:9050/apps_forum/writer?db=test&col=back_tracking&tool_Dropdown={AP, AP/CP One(BB) Chipset} multiselect ['Qualcomm | SM8150+', 'Qualcomm | SM8150']
    # http://127.0.0.1:9050/apps_forum/writer?db=test&col=back_tracking&tool_Dropdown={과제명} multiselect ['Y2 EUR OPEN [G986B]_RR', 'C2 US VERIZON'] and {Close Option} multiselect ['수정완료']
    # col_name, operator, filter_value = [None] * 3
    dropdown_parm = [{'value':value, 'filter_value':'[]'}]
    if 'initial' in current_state[0]:
    # if value is None and dropdown_initial is not None:
        print('display_dropdowns dropdown_initial :', dropdown_initial)
        expressions = dropdown_initial.split(' and ')
        dropdown_parm = []
        for x in expressions:
            col_name, operator, filter_value = split_filter_part(x)
            print("col_name:{}  operator:{}  filter_value:{}".format(col_name, operator, filter_value))
            if col_name:
                d = json.loads(intermediate_value[0])
                if d.get('anlayze_db'):
                    for x in d.get('anlayze_db'):
                        if col_name in x.get('label'):
                            value = x.get('value')
                            dropdown_parm.append({'value': value, 'filter_value': filter_value})
        append = len(dropdown_parm)

    index = len(children)
    fields = []
    for x in children:
        fields.append(x.get('props').get('children')[0].get('props').get('children'))
    
    # if append:
    for i in range(0,append):
        if dropdown_parm[i].get('value'):
            # print(dropdown_parm[i])
            # print(dropdown_parm[i].get('value'))
            # print(json.loads(dropdown_parm[i].get('value')))
            # 현재 추가된 필드는 추가 되지 못하도록 하기 위해서 ...
    
            dropdown_parm_i_get_value = dropdown_parm[i].get('value')
            if json.loads(dropdown_parm_i_get_value).get('field') not in fields:
                children.append(new_dropdown(index, dropdown_parm_i_get_value, ast.literal_eval(dropdown_parm[i].get('filter_value'))))

    if remove:
        if index> 0:
            children.pop()
    return children, 0, 0


def new_dropdown(index, value, inital = []):
    src=json.loads(value)

    if src.get('type')=='select':
        print("src.get('type')=='select'")
        print(src.get('options'))
        print(inital)

        return dbc.Row([
                # dbc.Col(dbc.Button("Secondary"+'#'*index, outline=True, color="secondary",)),
                dbc.Button(src.get('field'), outline=True, color="secondary", ),
                dbc.Col(dcc.Dropdown(
                    id={
                        'type': 'filter-dropdown',
                        'index': index
                    },
                    options=src.get('options'),
                    value=inital,
                    multi=True,
                    placeholder='Select multifule items...',
                # style=dict(verticalAlign="middle") # # style=dict(width='auto', display='inline-block',verticalAlign="middle") # width='40%'
                ),style={'padding':'0'}), # style={'padding':'0'}
                dbc.Col(dbc.Button("🔄", id={'type': 'added_dropdown_reflsh_button','index': index}, color="light",), width=1,style={'padding':'0', 'textAlign':'left'}), #  style={'padding':'0', 'textAlign':'left'}
            ],)
    elif src.get('type')=='slider':
        options = src.get('options')
        return dbc.Row([
                dbc.Button(src.get('field'), outline=True, color="secondary", ),
                dbc.Col(dcc.RangeSlider(
                    id={
                        'type': 'filter-dropdown',
                        'index': index
                    },
                    min=options.get('min'),  # the first date
                    max=options.get('max'),  # the last date
                    value=options.get('value'), # options.get('value'), # default: the first
                    tooltip={'always_visible': True, 'placement':'bottom'},
                ),style={'padding':'0'}), # style={'padding':'0'}
                dbc.Col(dbc.Button("🔄", id={'type': 'added_dropdown_reflsh_button','index': index}, color="light",), width=1,style={'padding':'0', 'textAlign':'left'}), #  style={'padding':'0', 'textAlign':'left'}
            ],)
    elif src.get('type')=='date_picker':
        options = src.get('options')
        print('options', options)
        print('options', type(options.get('value')), options.get('value'))
        print('options', type(options.get('value')[0]), options.get('value')[0])
        min = dateutil.parser.isoparse(options.get('min')),  # the first date
        max = dateutil.parser.isoparse(options.get('max')),  # the last date
        print(type(min), min, type(max), max) #<class 'tuple'> (datetime.datetime(2011, 3, 4, 11, 16, 34),)
        min = min[0]
        max = max[0]
        options.get('value')
        return dbc.Row([
                dbc.Button(src.get('field'), outline=True, color="secondary", ),
                dbc.Col(dcc.DatePickerRange(
                    id={
                        'type': 'filter-dropdown',
                        'index': index
                    },
                    # start_date=min,
                    end_date=max,
                    min_date_allowed=min,  # the first date
                    max_date_allowed=max,  # the last date
                    display_format='YYYY/MM/DD'
                    # value=[min,max], # options.get('value'), # default: the first
                    # marks={numd: date.strftime('%d/%m') for numd, date in zip(numdate, df['DATE'].dt.date.unique())})
                    ),style={'padding':'0'}), # style={'padding':'0'}
                dbc.Col(dbc.Button("🔄", id={'type': 'added_dropdown_reflsh_button','index': index}, color="light",), width=1,style={'padding':'0', 'textAlign':'left'}), #  style={'padding':'0', 'textAlign':'left'}
            ],)

@app.callback(
    Output({'type': 'added_dropdown_reflsh_button', 'index': ALL}, 'n_clicks'),
    Output('dropdown-select-value', 'children'),
    Output('dropdown-trans-dash-datatable-filter-format', 'children'),
    Output('dropdown-trans-dash-datatable-url-format', 'children'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'value'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'start_date'),
    Input({'type': 'filter-dropdown', 'index': ALL}, 'end_date'),
    Input({'type': 'added_dropdown_reflsh_button', 'index': ALL}, 'n_clicks'),
    Input('dropdown-container', 'children'),
)
def display_output(filter, start, end, reflash ,container):
    print('display_output:', filter, start, end, reflash ,container)
    # print(filter, start, end, reflash)
    for (i, value) in enumerate(reflash):
        reflash[i]=0

    merge_values = []
    for i in range(0,len(filter)):
        merge=[None]
        if filter[i]:
            merge=filter[i]
        elif start[i] or end[i]:
            merge=[start[i], end[i]]
        merge_values.append(merge)
        # print(len(filter), i, merge, merge_values)

    fields=[]
    for x in container:
        fields.append(x.get('props').get('children')[0].get('props').get('children'))

    dropdown_container_output = html.Div([
        html.Div('Dropdown {} {} = {}'.format(i + 1, fields[i], value))
        for i, value in enumerate(merge_values)
    ])

    _temp = ''
    for i, values in enumerate(merge_values):
        print(i, values, len(values))
        if values[0] is not None:
            _temp = _temp + '{{{}}} multiselect {}'.format(fields[i], values) + ' && '
    dash_datatable_filter_format = _temp.rstrip(' && ')
    return reflash, dropdown_container_output, dash_datatable_filter_format, '&tool_Dropdown='+ dash_datatable_filter_format.replace(' && ', ' and ')
