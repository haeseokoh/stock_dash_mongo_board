import dash
import dash_html_components as html
import dash_core_components as dcc


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    # html.Div(id="my-multi-dropdown"),
    dcc.Dropdown(
        id="my-multi-dropdown",
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value=['MTL', 'NYC'],
        multi=True
    ),
    ])


if __name__ == "__main__":
    app.run_server(debug=True)