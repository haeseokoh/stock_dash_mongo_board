import ast
import json

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import dateutil
from dash.dependencies import Input, Output, State, ALL
import pandas as pd
from datetime import datetime, timedelta

from app import app
from libs.mongo_api import db_init
from libs_stock.trading_from_db import stockDB, get_from_db_recover_missing_data
from utils import arg_parser


def get_layout(arg):
    arg_dic=arg_parser(arg)

    return html.Div([
        html.Div([
            dbc.Row([
                # html.Div(id='plm_report_style_2'),
            ]),
            dbc.Row([
                dcc.Graph(id='OHLCV-fig-screener'),
            ]),
            dbc.Row([
                dcc.Graph(id='trading-fig-screener'),
            ]),
        ], # style={'margin': '35px'}
        ),
    ])

def OHLCV_fig(df):
    fig = go.Figure()
    try:
        # return go.Figure(data=[go.Candlestick(x=df['날짜'],
        #                                      open=df['시가'],
        #                                      high=df['고가'],
        #                                      low=df['저가'],
        #                                      close=df['종가'],
        #                                      increasing_line_color='red', decreasing_line_color='blue')])
        fig = go.Figure(go.Candlestick(
                x=df['날짜'],
                open=df['시가'],
                high=df['고가'],
                low=df['저가'],
                close=df['종가'],
                increasing_line_color='red',
                decreasing_line_color='blue'))
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="LightSteelBlue",
        )
    except:
        pass
    return fig

def trading_fig(df):
    # Plot
    fig = go.Figure()

    try:
        # for x in ['외국인합계']:
        for x in ['기관합계', '기타법인', '개인', '외국인합계']:
            fig.add_trace(go.Scatter(x=df['날짜'], y=df[x].cumsum(), mode='lines', name=x))
        fig.update_xaxes(rangeslider_visible=True)
        # https://plotly.com/python/legend/
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="LightSteelBlue",
        )
    except:
        pass

    return fig


@app.callback(
    dash.dependencies.Output('OHLCV-fig-screener', 'figure'),
    dash.dependencies.Output('trading-fig-screener', 'figure'),
    Input('screener-cell-data', 'children'),
)
def plm_report_sink_main(select_cell_data):

    print('plm_report_sink_main :',select_cell_data)
    database_name = 'stock'

    start = (datetime.today() - timedelta(days=300)).strftime('%Y%m%d')
    end = datetime.today().strftime('%Y%m%d')

    jongmok = select_cell_data #'CJ제일제당'

    if jongmok is not None:
        _db_OHLCV, wanted = stockDB(database_name, 'OHLCV')
        dlist = get_from_db_recover_missing_data(_db_OHLCV, wanted, start, end, jongmok,
                                                 field=['시가', '고가', '저가', '종가', '거래량'])
        df_OHLCV = pd.DataFrame(dlist)
        OHLCV_chart = OHLCV_fig(df_OHLCV)

        _db_trading, wanted = stockDB(database_name, '거래량')
        dlist = get_from_db_recover_missing_data(_db_trading, wanted, start, end, jongmok,
                                                 field=['기관합계', '기타법인', '개인', '외국인합계'])
        df_trading = pd.DataFrame(dlist)
        trading_chart = trading_fig(df_trading)

        return OHLCV_chart, trading_chart
    else:
        return go.Figure(), go.Figure()