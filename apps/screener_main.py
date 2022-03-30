import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

from app import app
from apps import trading_sink, screener_sink
from libs_stock.naver_util_sise import *
from libs_stock.screener_util import wise_thewm
from libs_stock.trading_from_db import get_tickers
from utils import arg_parser


def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_dic = arg_parser(arg)

    return html.Div([
        dcc.Dropdown(
            id='dropdown',
            options=[
                {'label': '분기실적호전', 'value': '1'},
                {'label': '연간실적호전', 'value': '2'},
                {'label': '이익전망치상향', 'value': '3'},
                {'label': '저PE', 'value': '4'},
                {'label': '저PB', 'value': '5'},
                {'label': '업종평균대비저PE', 'value': '10'},
                {'label': '업종평균대비저PB', 'value': '11'},
                {'label': '배당수익률상위', 'value': '8'},
                {'label': '매출고성장', 'value': '9'},
                {'label': '고ROE', 'value': '6'},
                {'label': '수익성개선', 'value': '7'},
            ],
            value='1'
        ),
        dbc.Button("➕", id="screener-save-button", color="light", ),
        dbc.Button("🔄", id="screener-reflash-button", color="light", ),
        dbc.Button("🔄", id="screener-table-reflash-button", color="light", ),
        html.Div(selector('screener-selector')),
        dcc.Loading(id="loading", children=[
            table('screener-table'),
            html.Div(id='output-loading-data-read-online')
        ], type="default"),
        html.Div(id='screener-cell-data'),
        html.Div(id='screener-site-link'),
        html.Br(),
        screener_sink.get_layout(arg),
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
    dash.dependencies.Output('screener-selector', 'options'),
    dash.dependencies.Output('screener-selector', 'value'),
    dash.dependencies.Output('screener-table', 'data'),
    dash.dependencies.Output('screener-table', 'columns'),
    dash.dependencies.Output('screener-table', 'page_current'),
    dash.dependencies.Input('dropdown', 'value'),
    dash.dependencies.Input("screener-save-button", 'n_clicks'),
    dash.dependencies.Input("screener-reflash-button", 'n_clicks'),
    dash.dependencies.Input("screener-table-reflash-button", 'n_clicks'),
    dash.dependencies.State('screener-table', 'page_current'),
    dash.dependencies.State('screener-selector', 'value'),
)
def update_output(value, save_button, reflash_button, table_reflash_button, page_current, selected):
    print(value)
    datalist = []
    columns = []
    selector_options = []
    selector_value = []

    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'screener-reflash-button':
        delete_record(None)

    datalist=wise_thewm(value)

    if ctx.triggered[0]['prop_id'].split('.')[0] == 'screener-save-button':
        # save_naver_view_config(selected, value)
        pass

    if len(datalist):
        datalist_columns = list(datalist[0].keys())
        if ctx.triggered[0]['prop_id'].split('.')[0] == 'screener-reflash-button':
            # save_naver_view_config(datalist_columns, value )
            pass

        datalist_select = update_naver_view_config(datalist_columns, value)
        # print('update_naver_view_config :', datalist_select)

        columns = [{'name': i, 'id': i} for i in datalist_select]

        selector_options = [{'label': x, 'value': x} for x in datalist_columns]
        selector_value = datalist_select


    print('columns', columns)

    if page_current == None:
        page_current = 0

    print('You have selected "{}"'.format(value), len(datalist), columns, page_current)
    return selector_options, selector_value, datalist, columns, page_current


@app.callback(
    dash.dependencies.Output('screener-cell-data', 'children'),
    dash.dependencies.Output('screener-site-link', 'children'),
    dash.dependencies.Input('screener-table', 'data'),
    dash.dependencies.Input('screener-table', 'derived_virtual_row_ids'),
    dash.dependencies.Input('screener-table', 'active_cell'),
    dash.dependencies.State('screener-table', 'page_current'),
    dash.dependencies.State('screener-table', 'page_size'),
)
def update_select_cell(data, row_ids, active_cell, page_current, page_size):
    print('active_cell, page_current, page_size', active_cell, page_current, page_size)


    jongmok = ''
    naver_href='https://finance.naver.com/sise/'
    naver_f_href='https://finance.naver.com/sise/'
    daum_href='https://finance.daum.net/'
    nice_href='http://media.kisline.com/'
    hankyung_href='http://consensus.hankyung.com/apps.analysis/analysis.list'

    try:
        if active_cell is not None:
            row_id = row_ids[active_cell['row'] + page_current * page_size]
            print(data[row_id])
            jongmok=data[row_id]['종목명']

            if len(jongmok):
                ticker = get_tickers(data[row_id]['종목명'])
                naver_href='https://navercomp.wisereport.co.kr/v2/company/c1050001.aspx?cmp_cd={}&cn='.format(ticker)
                naver_f_href='https://finance.naver.com/item/main.nhn?code={}'.format(ticker)
                daum_href='https://finance.daum.net/quotes/A{}#analysis/consensus'.format(ticker)
                nice_href='http://media.kisline.com/highlight/mainHighlight.nice?paper_stock={}&nav=1'.format(ticker)
                hankyung_href='http://consensus.hankyung.com/apps.chart/chart.view_frame?report_type=CO&business_code={}'.format(ticker)
    except:
        pass

    return jongmok, html.Div([
            dcc.Link('-naver', id='naver-link', href=naver_href),
            dcc.Link('-full', id='naver-f-link', href=naver_f_href),
            dcc.Link('-daum', id='daum-link', href=daum_href),
            dcc.Link('-nice', id='nice-link', href=nice_href),
            dcc.Link('-hankyung', id='hankyung-link', href=hankyung_href),
    ])