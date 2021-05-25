import ast
import json

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import dateutil
from dash.dependencies import Input, Output, State, ALL
import pandas as pd

from app import app
from libs.mongo_api import db_init
from utils import arg_parser


def get_layout(arg):
    arg_dic=arg_parser(arg)

    return html.Div([
        html.Div([
            dbc.Row([
                dbc.Alert("This is a secondary alert", color="secondary"),
                dbc.Button("Click me", id="plm_report_style_I_button", className="mr-2"),
            ]),
            dbc.Row([
                html.Div(id='plm_report_style_I'),
            ]),
            dbc.Row([
                dcc.Graph(id='rangeslider_sample'),
            ]),
        ], style={'margin': '35px'}),
    ])


def rangeslider_sample():
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
    fig = px.line(df, x='Date', y='AAPL.High', height=200)
    fig.update_xaxes(rangeslider_visible=True)
    # fig.update_layout(xaxis_rangeslider_visible=True)
    # fig.show()
    return fig

@app.callback(
    dash.dependencies.Output('rangeslider_sample', 'figure'),
    Input('plm_report_style_I_button', 'n_clicks'),
)
def update_y_timeseries(n_clicks):
    return rangeslider_sample()

@app.callback(
    Output('plm_report_style_I', 'children'),
    Input('current_state', 'children'),
    Input('plm_report_style_I_button', 'n_clicks'),
    State('intermediate_value', 'children'),
    State('output-data-read-online', 'data'),
)
def plm_report_sink_main(current_state, clicks, intermediate_value, data):
    d=json.loads(intermediate_value[0])
    if 'prepared' in current_state[0]:
        pass
        # print('plm_report_sink_main :',data)
    return html.Div([
        # html.Pre(json.dumps({'intermediate_value': d}, indent=2 )), # ensure_ascii=False).encode('utf8')
        # html.Pre(json.dumps(d, ensure_ascii=False, indent=2)),  # ensure_ascii=False).encode('utf8')
    ])
