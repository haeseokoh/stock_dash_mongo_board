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


def get_layout(intermediate_value):

    return html.Div([
        dbc.Row([
        ]),
        html.Div(id='dropdown-env-anlayze-output'),
    ])
@app.callback(
    Output('dropdown-env-anlayze-output', 'children'),
    Input('env_button', 'n_clicks'),
    State('intermediate_value', 'children'),
)
def anlayze_db(clicks, intermediate_value):
    d=json.loads(intermediate_value[0])
    return html.Div([
        # html.Pre(json.dumps({'intermediate_value': d}, indent=2 )), # ensure_ascii=False).encode('utf8')
        html.Pre(json.dumps(d, ensure_ascii=False, indent=2)),  # ensure_ascii=False).encode('utf8')
    ])
