import socket
from urllib.parse import unquote

import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

def Header(app, menu, auth = []):
    return html.Div([get_header(app, menu, auth)])


def get_header(app,menu, auth):
    header = html.Div(
        [
            dbc.Navbar(
                [
                    dbc.NavbarBrand("Forum"),
                    html.Div(
                        menu,
                    ),
                    html.Div(
                        [
                            html.Div(
                                auth,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
    return header


def auth_display_page(dam):
    # print('auth_display_page dam.current_user:',dam.current_user)
    auth_interface = []
    if dam.current_user != None:
        if dam.current_user.is_authenticated:
            auth_interface = dam.render_logout_button()
        else:
            auth_interface =  dam.render_navbar_login()

    return auth_interface

def make_dash_table(df, max_rows=26):
    return html.Table(
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )

def _make_dash_table_with_head(df, max_rows=26):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in df.columns]) ] +
        # Body
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))]
    )

def make_dash_table_with_head(df, max_rows=26, style_set=None, scroll_body=False):
    _style = {'border': '1px solid #ccc'}
    th_style = {'background': 'lightblue', 'border': '1px solid #ccc'}
    tr_style = {'border': '1px solid #ccc'}
    thead_style = {'text-align': 'center', 'width': '100%', }
    tbody_style = {'text-align': 'center', 'width': '100%', }
    table_style={'margin': '0px', 'padding': '0px', 'text-align':'center', 'width':'100%'}
    # https://melkia.dev/ko/questions/17067294
    # https://heropy.blog/2018/11/24/css-flexible-box/
    if scroll_body==True:
        _style = {'border': '1px solid #ccc',} # 'text-overflow': 'ellipsis'
        th_style = {'border': '1px solid #ccc', 'background': 'lightblue',}
        tr_style = { 'width':'100%', 'display':'table', 'table-layout':'fixed', 'border': '1px solid #ccc'}
        thead_style = {'width':'100%', 'flex': '1 1 auto', 'display':'block', 'overflow-y':'scroll', }
        tbody_style = {'width':'100%', 'flex': '1 1 auto', 'display':'block', 'max-height': '200px', 'overflow-y':'scroll',}
        table_style= {'display':'flex','flex-flow':'column','flex': '1 1 auto', 'margin': '0px', 'padding': '0px', 'text-align':'center', 'width':'100%'}
    # Header                                             # Body
    table_data = [
        html.Thead([
            html.Tr([
                html.Th(col, style=th_style) for index, col in enumerate(df.columns)], style=tr_style)
            ], style=thead_style)
        ] + [
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col], style=_style) for col in df.columns], style=tr_style) for i in range(min(len(df), max_rows))
            ], style = tbody_style)
        ]
    if style_set=='dbc_table':
        return dbc.Table(
            table_data,
            bordered=True,
            # https://css-tricks.com/complete-guide-table-element/
            style = table_style
        )
    elif style_set=='???':
        return dbc.Table(
            table_data,
        )
    else:
        return html.Table(
            table_data,
            style= table_style#'overflow':'scroll'
        )

def arg_parser(url):
    arg = unquote(url)
    print('arg_parser:',arg)
    # ?db=prj&col=prj_progress
    arg_dic = {}

    if len(arg)>0:
        arg = arg[1:]
        for x in arg.split('&'):
            x_split = (x.split('='))
            arg_dic[x_split[0]] = x_split[1]

    print('arg_parser arg_dic:', arg_dic)
    return arg_dic

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

