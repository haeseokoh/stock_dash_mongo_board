import ast
import json

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dateutil
from dash.dependencies import Input, Output, State, ALL
import pandas as pd

from app import app
from apps import data_table_db_online_read_with_filter_writer, plugin_test_sink
from libs.mongo_api import db_init
from utils import arg_parser


def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_dic=arg_parser(arg)
    
    return html.Div([
        html.Div([
            data_table_db_online_read_with_filter_writer.get_layout(arg),
            # ],style={}), # style={'display': 'none'}
            ],),  # style={'display': 'none'}
        html.Div([
                dbc.Row([
                    dbc.Alert("This is a primary alert", color="primary"),
                    dbc.Button("Click me", id="plugin_test_mondule_button", className="mr-2"),
                ]),
                dbc.Row([
                    html.Div(id='plugin_test_mondule'),
                ]),
            ],style={'margin': '35px'}),
            plugin_test_sink.get_layout(arg),
    ])


@app.callback(
    Output('plugin_test_mondule', 'children'),
    Input('plugin_test_mondule_button', 'n_clicks'),
    State('intermediate_value', 'children'),
)
def anlayze_db(clicks, intermediate_value):
    d=json.loads(intermediate_value[0])
    return html.Div([
        # html.Pre(json.dumps({'intermediate_value': d}, indent=2 )), # ensure_ascii=False).encode('utf8')
        html.Pre(json.dumps(d, ensure_ascii=False, indent=2)),  # ensure_ascii=False).encode('utf8')
    ])
