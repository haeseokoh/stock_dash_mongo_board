import os
import dash
import dash_access_manager as dam
import dash_bootstrap_components as dbc
from utils import get_ip

external_stylesheets = [dbc.themes.LITERA]
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
)
server = app.server
server.secret_key = os.urandom(12)

dam.init_access_manager(app)

curr_ip = get_ip()