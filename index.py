from collections import OrderedDict

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_access_manager as dam
import dash_bootstrap_components as dbc

from app import app
from app_config import HOSTPORT
from momentem_stock_rel.momentem_stock_db_util import ticker_save
from utils import Header, auth_display_page
from apps import (
    overview,
    data_table_db_online_read_with_filter_writer,
    data_table_upload_to_db,
    data_table_link,
    data_table_db_online_read_with_filter_writer_merge_testing,
    plugin_test,
    data_table_upload_to_db_2,
    sise_rise_main,
    sise_group_main,
    screener_main)

server = app.server

menu_dic = OrderedDict({
    '/dash-financial-report/overview':{'menu':'Overview', 'module':overview },
    '/apps_forum/sise_rise_main':{'menu':'sise rise', 'module':sise_rise_main },
    '/apps_forum/sise_group_main':{'menu':'sise group', 'module':sise_group_main },
    '/apps_forum/screener_main':{'menu':'screener', 'module':screener_main },
    '/apps_forum/writer':{'menu':'Viewer&Writer', 'module':data_table_db_online_read_with_filter_writer },
    '/apps_forum/upload':{'menu':'Data Upload', 'module': data_table_upload_to_db},
    '/apps_forum/link':{'menu':'Link', 'module': data_table_link},
    '/apps_forum/test':{'menu':'Test', 'module': data_table_db_online_read_with_filter_writer_merge_testing},
    # '/apps_forum/plugin_test':{'menu':'plugin test', 'module': plugin_test},
    '/apps_forum/data_table_upload_to_db_2':{'menu':'Data Upload II', 'module': data_table_upload_to_db_2},
    '/apps_forum/full-view':{'menu':'full-view', 'module': (overview,data_table_link,data_table_db_online_read_with_filter_writer,data_table_upload_to_db)},
})

menu = dbc.Nav([ dbc.NavItem(dbc.NavLink(v['menu'], href=k )) for k, v in menu_dic.items()])


def menu_link_layout(pathname, search):
    layout = None
    if pathname in menu_dic:
        print(menu_dic.get(pathname))
        module = menu_dic[pathname]['module']
        if isinstance(module, tuple):
            layout = html.Div([x.get_layout(search) for x in module])
        else:
            layout = menu_dic[pathname]['module'].get_layout(search)

    else:
        layout=menu_dic['/dash-financial-report/overview']['module'].get_layout(search)

    return layout

app.layout = html.Div([
    html.Link(href='/assets/dash_adjustment.css', rel='stylesheet'),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-head'),
    html.Div(id='page-content-view')
])

@app.callback(Output('page-head', 'children'),
              Output('page-content-view', 'children'),
              Input('url', 'pathname'),
              Input('url', 'search'))
def display_page(pathname, search):
    print('pathname:{}, search:{}'.format(pathname, search))
    # page_content = [html.H3('Please log in to continue')]
    page_content = [dbc.Row([html.H1("Please log in to continue")], justify="center", align="center")]
    # # if dam.current_user.is_authenticated:
    if True:
        page_content=menu_link_layout(pathname, search)
        
    return [Header(app, menu, auth_display_page(dam))], page_content
    # return [], page_content

if __name__ == '__main__':
    ticker_save()
    dam.connect(
        db='dash_auth',
        host='mongodb://localhost:27017/'
    )
    app.run_server(port=HOSTPORT, debug=True)