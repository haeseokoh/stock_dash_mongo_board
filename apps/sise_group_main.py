import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import dash_bootstrap_components as dbc

from app import app
from apps import trading_sink2
from libs_stock.never_util_group import upjong_sise, theme_sise, group_sise, upjong_sise_sub, theme_sise_sub, \
    group_sise_sub, base_url
from libs_stock.stock_db_util import save_naver_view_config, update_naver_view_config
from libs_stock.trading_from_db import get_tickers
from utils import arg_parser


def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_dic = arg_parser(arg)

    return html.Div([
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='dropdown',
                    options=[
                        {'label': '업종', 'value': 'upjong_sise'},
                        {'label': '테마', 'value': 'theme_sise'},
                        {'label': '그룹', 'value': 'group_sise'},
                    ],
                    value='upjong_sise'
                ),
                dbc.Button("➕", id="stock-group-selector-save-button", color="light", ),
                dbc.Button("🔄", id="stock-group-selector-reflash-button", color="light", ),
                html.Div(selector('stock-group-selector')),
                dcc.Loading(id="loading", children=[
                    table(id='stock-group-table'),
                    # html.Div(id='output-loading-data-read-online')
                ], type="default"),
            ],width=4),
            dbc.Col([
                html.Div(id='select-cell-stock-group'),
                dbc.Button("➕", id="stock-group-sub-selector-save-button", color="light", ),
                dbc.Button("🔄", id="stock-group-sub-selector-reflash-button", color="light", ),
                html.Div(selector('stock-group-sub-selector')),
                dcc.Loading(id="loading", children=[
                    table(id='stock-group-sub-table'),
                    # html.Div(id='output-loading-data-read-online')
                ], type="default"),
                html.Br(),
                html.Div(id='select-group-sub-cell-data'), # select-cell-data
                html.Div(id='site-link'),
            ],
            width=8),
        ],),
        trading_sink2.get_layout(arg),
    ],style={'margin': '35px'})

def selector(id):
    return dcc.Dropdown(
        id = id,
        options=[],
        value=[],
        multi=True
    )

def table(id):
    return dash_table.DataTable(
        id=id,
        # data=df.to_dict('records'),
        data=[],
        sort_action='native',
        filter_action='native',

        columns=[],
        # style_data_conditional=(
        #     # data_bars(df, 'PER') +
        #     # data_bars(df, 'ROE')
        # ),
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        # style_cell={
        #     'width': '100px',
        #     'minWidth': '100px',
        #     'maxWidth': '100px',
        #     'overflow': 'hidden',
        #     'textOverflow': 'ellipsis',
        # },
        page_size=20,
        # export_headers='display',
    )


@app.callback(
    dash.dependencies.Output('stock-group-selector', 'options'),
    dash.dependencies.Output('stock-group-selector', 'value'),
    dash.dependencies.Output('stock-group-table', 'data'),
    dash.dependencies.Output('stock-group-table', 'columns'),
    dash.dependencies.Output('stock-group-table', 'page_current'),
    dash.dependencies.Input('dropdown', 'value'),
    dash.dependencies.Input("stock-group-selector-save-button", 'n_clicks'),
    dash.dependencies.Input("stock-group-selector-reflash-button", 'n_clicks'),
    dash.dependencies.State('stock-group-table', 'page_current'),
    dash.dependencies.State('stock-group-selector', 'value'),
)
def update_output(value, save_button, reflash_button, page_current, selected):
    print(value)
    datalist = []
    columns = []
    selector_options = []
    selector_value = []

    if value == 'upjong_sise':
        datalist = upjong_sise()
    elif value == 'theme_sise':
        datalist = theme_sise()
    elif value == 'group_sise':
        datalist = group_sise()

    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'stock-group-selector-save-button':
        save_naver_view_config(selected, value)

    if len(datalist):
        datalist_columns = list(datalist[0].keys())
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'stock-group-selector-reflash-button':
            save_naver_view_config(datalist_columns, value )

        datalist_select = update_naver_view_config(datalist_columns, value)
        print('update_naver_view_config :', datalist_select)

        columns = [{'name': i, 'id': i} for i in datalist_select]

        selector_options = [{'label': x, 'value': x} for x in datalist_columns]
        selector_value = datalist_select

    if page_current == None:
        page_current = 0

    print('You have selected "{}"'.format(value), len(datalist), columns, page_current)
    return selector_options, selector_value, datalist, columns, page_current


@app.callback(
    dash.dependencies.Output('select-cell-stock-group', 'children'),
    dash.dependencies.Input('stock-group-table', 'data'),
    dash.dependencies.Input('stock-group-table', 'derived_virtual_row_ids'),
    dash.dependencies.Input('stock-group-table', 'active_cell'),
    dash.dependencies.State('stock-group-table', 'page_current'),
    dash.dependencies.State('stock-group-table', 'page_size'),
)
def update_select_cell(data, row_ids, active_cell, page_current, page_size):
    print('active_cell, page_current, page_size', active_cell, page_current, page_size)

    try:
        if active_cell is not None:
            row_id = row_ids[active_cell['row'] + page_current * page_size]
            print(data[row_id])
            row_keys= list(data[row_id].keys())
            print(row_keys)
            print(data[row_id][row_keys[1]] + '&&&' + data[row_id]['Link'])
            return data[row_id][row_keys[1]] + '&&&' + data[row_id]['Link']
    except:
        return ''



@app.callback(
    dash.dependencies.Output('stock-group-sub-selector', 'options'),
    dash.dependencies.Output('stock-group-sub-selector', 'value'),
    dash.dependencies.Output('stock-group-sub-table', 'data'),
    dash.dependencies.Output('stock-group-sub-table', 'columns'),
    dash.dependencies.Output('stock-group-sub-table', 'page_current'),
    dash.dependencies.Input('select-cell-stock-group', 'children'),
    dash.dependencies.Input("stock-group-sub-selector-save-button", 'n_clicks'),
    dash.dependencies.Input("stock-group-sub-selector-reflash-button", 'n_clicks'),
    dash.dependencies.State('dropdown', 'value'),
    dash.dependencies.State('stock-group-sub-table', 'page_size'),
    dash.dependencies.State('stock-group-sub-table', 'page_current'),
    dash.dependencies.State('stock-group-sub-selector', 'value'),
)
def update_output(children, save_button, reflash_button, value, page_size, page_current, selected):
    datalist = []
    columns = []
    selector_options = []
    selector_value = []

    try:
        group = ''
        link = ''
        if children is not None:
            select_cel=children.split('&&&')
            print(select_cel)
            group=select_cel[0]
            link=select_cel[1]

        url=base_url+link
        print('base_url+link:',url)


        if value == 'upjong_sise':
            datalist = upjong_sise_sub(url, group)
        elif value == 'theme_sise':
            datalist = theme_sise_sub(url, group)
        elif value == 'group_sise':
            datalist = group_sise_sub(url, group)

        ctx = dash.callback_context
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'stock-group-sub-selector-save-button':
            save_naver_view_config(selected, value + '_sub')

        if len(datalist):
            datalist_columns = list(datalist[0].keys())
            if ctx.triggered[0]['prop_id'].split('.')[0] == 'stock-group-sub-selector-reflash-button':
                save_naver_view_config(datalist_columns, value + '_sub' )

            datalist_select = update_naver_view_config(datalist_columns, value + '_sub')
            print('update_naver_view_config :', datalist_select)

            columns = [{'name': i, 'id': i} for i in datalist_select]

            selector_options = [{'label': x, 'value': x} for x in datalist_columns]
            selector_value = datalist_select

    except:
        pass

    if page_current == None:
        page_current = 0

    if (page_current+1)*page_size > len(datalist):
        page_current = 0

    print(len(datalist), columns, page_current)
    return selector_options, selector_value, datalist, columns, page_current


@app.callback(
    dash.dependencies.Output('select-group-sub-cell-data', 'children'),
    dash.dependencies.Output('site-link', 'children'),
    dash.dependencies.Input('stock-group-sub-table', 'data'),
    dash.dependencies.Input('stock-group-sub-table', 'derived_virtual_row_ids'),
    dash.dependencies.Input('stock-group-sub-table', 'active_cell'),
    dash.dependencies.State('stock-group-sub-table', 'page_current'),
    dash.dependencies.State('stock-group-sub-table', 'page_size'),
)
def update_select_cell(data, row_ids, active_cell, page_current, page_size):
    print('active_cell, page_current, page_size', active_cell, page_current, page_size)

    jongmok = ''
    naver_href='https://finance.naver.com/sise/'
    daum_href='https://finance.daum.net/'
    nice_href='http://media.kisline.com/'

    try:
        if active_cell is not None:
            row_id = row_ids[active_cell['row'] + page_current * page_size]
            print(data[row_id])
            row_keys= list(data[row_id].keys())
            print(row_keys)
            jongmok=data[row_id][row_keys[1]].split(' *')[0]

            if len(jongmok):
                ticker = get_tickers(data[row_id][row_keys[1]].split(' *')[0])
                naver_href='https://navercomp.wisereport.co.kr/v2/company/c1050001.aspx?cmp_cd={}&cn='.format(ticker)
                daum_href='https://finance.daum.net/quotes/A{}#analysis/consensus'.format(ticker)
                nice_href='http://media.kisline.com/highlight/mainHighlight.nice?paper_stock={}&nav=1'.format(ticker)

    except:
        pass

    return jongmok, html.Div([
            dcc.Link('-naver', id='naver-link', href=naver_href),
            dcc.Link('-daum', id='daum-link', href=daum_href),
            dcc.Link('-nice', id='nice-link', href=nice_href),
    ])