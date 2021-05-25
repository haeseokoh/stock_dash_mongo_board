import os

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from app_config import HOSTPORT
from utils import *

import pandas as pd
import pathlib

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()
from app import app, curr_ip

# df_fund_facts = pd.read_csv(DATA_PATH.joinpath("df_fund_facts.csv"))
# print('http://{}:{}/apps_forum/writer{}'.format(curr_ip, int(os.environ.get('PORT', HOSTPORT)),'?db=prj&col=prj_progress'))
data = [
    ['viewer and writer 검증허브 DashboardList', dcc.Link("link",href="/apps_forum/writer?db=prj&col=prj_progress"),],
    ['upload 검증허브 DashboardList excel file', dcc.Link("link",href="/apps_forum/upload?db=prj&col=prj_progress&unique=개발모델명,검증단계"),],
    ['viewer and writer google devices', dcc.Link("link", href="/apps_forum/writer?db=google_play&col=devices"), ],
    ['merge test',
     dcc.Link("link", href="/apps_forum/test?db=prj&col=prj_progress&f_col=plm_prj_code&field=개발모델명&f_field=model_name"), ],

]
df_link = pd.DataFrame(data)
df_link.columns = ['Disc', 'Link']

def get_layout(search):
    # Page layouts
    return html.Div([
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H5("데이타 베이스 링크"),
                        html.Br(),
                        html.P(
                            "\
                        데이타베이스 조회와 업데이트를 지원합니다. \
                        별도의 API를 통하지 않고 범용적으로 사용이 가능합니다. \
                        viewer, edit, excel을 통한 업데이트가 가능합니다.",
                        ),
                    ],
                )
            )
        ),
        dbc.Row(
            dbc.Col([
                html.Div([
                    html.H6("Link"),
                    make_dash_table(df_link),
                    ]
                ),
                # html.Div([
                #     html.H6("Link2"),
                #     make_dash_table_with_head(df_link),
                # ])
            ],width=6,),
        ),
    ],style={'margin': '35px'})