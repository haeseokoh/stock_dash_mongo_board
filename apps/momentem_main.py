import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc

from app import app
from apps import trading_sink3
from libs_stock.naver_util_sise import *
from libs_stock.trading_from_db import get_tickers
from momentem_stock_rel.momentem_stock_all_in_one_today import create_momenterm_date, get_ref_date
from utils import arg_parser


def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_dic = arg_parser(arg)

    return html.Div([
        dcc.Dropdown(
            id='momentem_dropdown',
            options=[
                {'label': 'KOSPI 모멘텀', 'value': 'KOSPI_momentem'},
                {'label': 'KOSDAQ 모멘텀', 'value': 'KOSDAQ_momentem'},
            ],
            value='KOSPI_momentem'
        ),
        # dbc.Button("➕", id="stock-selector-save-button", color="light", ),
        # dbc.Button("🔄", id="stock-selector-reflash-button", color="light", ),
        # dbc.Button("🔄", id="stock-table-reflash-button", color="light", ),
        html.Div(selector('momentem-selector')),
        dcc.Loading(id="loading", children=[
            table('stock-momentem-table'),
            html.Div(id='output-loading-data-read-online')
        ], type="default"),
        html.Div(id='select-cell-momentem-data'),
        html.Div(id='sise-site-momentem-link'),
        html.Br(),
        trading_sink3.get_layout(arg),
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


momentem_dic = {}

@app.callback(
    dash.dependencies.Output('momentem-selector', 'options'),
    dash.dependencies.Output('momentem-selector', 'value'),
    dash.dependencies.Output('stock-momentem-table', 'data'),
    dash.dependencies.Output('stock-momentem-table', 'columns'),
    dash.dependencies.Output('stock-momentem-table', 'page_current'),
    dash.dependencies.Input('momentem_dropdown', 'value'),
    # dash.dependencies.Input("stock-selector-save-button", 'n_clicks'),
    # dash.dependencies.Input("stock-selector-reflash-button", 'n_clicks'),
    # dash.dependencies.Input("stock-table-reflash-button", 'n_clicks'),
    dash.dependencies.State('stock-momentem-table', 'page_current'),
    dash.dependencies.State('momentem-selector', 'value'),
)
# def update_output(value, save_button, reflash_button, table_reflash_button, page_current, selected):
def update_output(value, page_current, selected):

    print(value)
    momentem_df = pd.DataFrame()
    datalist = []
    columns = []
    selector_options = []
    selector_value = []

    ctx = dash.callback_context
    # if ctx.triggered[0]['prop_id'].split('.')[0] == 'stock-table-reflash-button':
    #     delete_record(None)

    # if value == 'KOSPI_sise_market_sum':
    #     datalist = KOSPI_sise_market_sum()
    # elif value == 'KOSDAQ_sise_market_sum':
    #     datalist = KOSDAQ_sise_market_sum()
    # elif value == 'KOSPI_sise_rise':
    #     datalist = KOSPI_sise_rise()
    # elif value == 'KOSDAQ_sise_rise':
    #     datalist = KOSDAQ_sise_rise()

    last_day, few_day, long_day = get_ref_date()

    global momentem_dic
    if len(momentem_dic) == 0:
        momentem_dic = create_momenterm_date(last_day, few_day, long_day)

    if value == 'KOSPI_momentem':
        momentem_df = momentem_dic['0']
    elif value == 'KOSDAQ_momentem':
        momentem_df = momentem_dic['1']

    datalist=momentem_df.to_dict(orient='records')

    # if ctx.triggered[0]['prop_id'].split('.')[0] == 'stock-selector-save-button':
    #     save_naver_view_config(selected, value)
    #
    if len(datalist):
        datalist_columns = list(datalist[0].keys())
        # if ctx.triggered[0]['prop_id'].split('.')[0] == 'stock-selector-reflash-button':
        #     save_naver_view_config(datalist_columns, value )
        #
        # datalist_select = update_naver_view_config(datalist_columns, value)
        # print('update_naver_view_config :', datalist_select)
        datalist_select = datalist_columns

        columns = [{'name': i, 'id': i} for i in datalist_select]

        selector_options = [{'label': x, 'value': x} for x in datalist_columns]
        selector_value = datalist_select


    print('columns', columns)

    if page_current == None:
        page_current = 0

    print('You have selected "{}"'.format(value), len(datalist), columns, page_current)
    return selector_options, selector_value, datalist, columns, page_current


@app.callback(
    dash.dependencies.Output('select-cell-momentem-data', 'children'),
    dash.dependencies.Output('sise-site-momentem-link', 'children'),
    dash.dependencies.Input('stock-momentem-table', 'data'),
    dash.dependencies.Input('stock-momentem-table', 'derived_virtual_row_ids'),
    dash.dependencies.Input('stock-momentem-table', 'active_cell'),
    dash.dependencies.State('stock-momentem-table', 'page_current'),
    dash.dependencies.State('stock-momentem-table', 'page_size'),
)
def update_select_cell(data, row_ids, active_cell, page_current, page_size):
    print('active_cell, page_current, page_size', active_cell, page_current, page_size)


    jongmok = ''
    naver_href='https://finance.naver.com/sise/'
    naver_f_href='https://finance.naver.com/sise/'
    daum_href='https://finance.daum.net/'
    nice_href='http://media.kisline.com/'
    hankyung_href = 'http://consensus.hankyung.com/apps.analysis/analysis.list'

    # try:
    if 1:
        if active_cell is not None:
            # row_id = row_ids[active_cell['row'] + page_current * page_size]
            index = active_cell['row'] + page_current * page_size
            # print(row_ids)
            print(index)
            # print(data[0])
            print(data[index])
            jongmok=data[index]['종목명']

            if len(jongmok):
                ticker = get_tickers(data[index]['종목명'])
                naver_href='https://navercomp.wisereport.co.kr/v2/company/c1050001.aspx?cmp_cd={}&cn='.format(ticker)
                naver_f_href='https://finance.naver.com/item/main.nhn?code={}'.format(ticker)
                daum_href='https://finance.daum.net/quotes/A{}#analysis/consensus'.format(ticker)
                nice_href='http://media.kisline.com/highlight/mainHighlight.nice?paper_stock={}&nav=1'.format(ticker)
                hankyung_href = 'http://consensus.hankyung.com/apps.chart/chart.view_frame?report_type=CO&business_code={}'.format(ticker)
    # except:
    #     pass

    return jongmok, html.Div([
            dcc.Link('-naver', id='naver-link', href=naver_href),
            dcc.Link('-full', id='naver-f-link', href=naver_f_href),
            dcc.Link('-daum', id='daum-link', href=daum_href),
            dcc.Link('-nice', id='nice-link', href=nice_href),
            dcc.Link('-hankyung', id='hankyung-link', href=hankyung_href),
    ])