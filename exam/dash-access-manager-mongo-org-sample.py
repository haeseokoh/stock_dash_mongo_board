# https://github.com/evan-lh/dash-access-manager
import dash

import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

import os

import dash_access_manager as dam


# server_port = os.environ.get('PORT', 5000)
#
# database_name = os.environ.get('dash_auth')
#
# database_url = os.environ.get('mongodb://localhost:27017/')

#####
#### Initialize the dash app
#####

external_stylesheets = [dbc.themes.LITERA]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

server.secret_key = os.urandom(12)

# Initiate access manager callbacks

dam.init_access_manager(app)

app.config.suppress_callback_exceptions = True

############
########### Set up the layout
############

app.layout = html.Div(children=[dcc.Location(id='url', refresh=False),
                                html.Div(id='root'),
                                html.Div(id='container')
                                ])


def render_default_page(navbar_button=[], page_content=[html.H3("Some content")]):
    return [
               dbc.Navbar([
                              dbc.NavbarBrand("Navbar"),
                          ] + navbar_button,
                          color="primary")
           ] + page_content


############
########### Define the callbacks
############

@app.callback(Output('root', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if dam.current_user.is_authenticated:
        return render_default_page(dam.render_logout_button(), [html.H3('Logged in successfully')])
    else:
        return render_default_page(dam.render_navbar_login() + dam.render_navbar_sign_up(), [html.H3('Please log in to continue')])


if __name__ == "__main__":
    dam.connect(
        db='dash_auth',
        host='mongodb://localhost:27017/'
    )
    app.run_server(host='0.0.0.0', port=5000)