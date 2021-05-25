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
from libs.mongo_api import db_init
from utils import arg_parser


def get_layout(arg):
    # ?db=prj&col=prj_progress
    arg_dic=arg_parser(arg)

    return html.Div([
        dbc.Row([
        ]),
        html.Div(id='sample-output'),
    ])


@app.callback(
    Output('sample-output', 'children'),
    Input('sample_button', 'n_clicks'),
    State('intermediate_value', 'children'),
)
def anlayze_db(clicks, intermediate_value):
    d=json.loads(intermediate_value[0])
    return html.Div([
        # html.Pre(json.dumps({'intermediate_value': d}, indent=2 )), # ensure_ascii=False).encode('utf8')
        html.Pre(json.dumps(d, ensure_ascii=False, indent=2)),  # ensure_ascii=False).encode('utf8')
    ])
