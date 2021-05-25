import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash_pivottable

data_0 = [["Total Bill", "Tip", "Payer Gender", "Payer Smoker", "Day of Week", "Meal", "Party Size"],
   [16.99, 1.01, "Female", "Non-Smoker", "Sunday", "Dinner", 2],
   [10.34, 1.66, "Male", "Non-Smoker", "Monday", "Dinner", 3],
   [21.01, 3.5, "Male", "Non-Smoker", "Saturday", "Dinner", 3],
   [23.68, 3.31, "Male", "Non-Smoker", "Sunday", "Dinner", 2],
]

data_1 = [["animal", "is_good_boy", "kg_of_food"],
        ["dog", "yes", 100],
        ["cat", "no", 12],
        ["bird", "no", 4],
]

data_2 = [["book", "pages", "liked_it"],
        ["dogs are cool", 400, 1],
        ["cats are bad", 350, 0],
        ["birds fly", 20, 0],
]

data_3 = [['Name', 'Country', 'Sex', 'Height', 'Weight'],
        ['John', 'US', 'M', 180, 70],
        ['Paul', 'US', 'M', 200, 65],
        ['Peter', 'Canada', 'M', 160, 60],
        ['Mark', 'Canada', 'M', 190, 80],
        ['Mary', 'Canada', 'F', 190, 50],
        ['Jane', 'Canada', 'F', 160, 70],
        ['Susan', 'US', 'F', 170, 70],
        ['Mandy', 'US', 'F', 150, 90],
]

data_dict = {
    "data_0": data_0,
    "data_1": data_1,
    "data_2": data_2,
    "data_3": data_3
}

app = dash.Dash(__name__)
app.title = 'My Dash example'

app.layout = html.Div([
   dcc.Dropdown(
       id='data_selection_dropdown',
       options=[{"label": e, "value": e} for e in data_dict],
       value=list(data_dict.keys())[0]
   ),
   html.Div(id="pivot_table_container"),
])


@app.callback(Output("pivot_table_container", "children"),
             [Input("data_selection_dropdown", "value")])
def select_data(selected_data):
   return make_pivot_table(data_dict[selected_data], f"{selected_data}_pivot")


def make_pivot_table(data, component_id):
   component = dash_pivottable.PivotTable(
       id=component_id,
       data=data,
       colOrder="key_a_to_z",
       rowOrder="key_a_to_z",
       rendererName="Table",
       aggregatorName="Count",
   )
   return component


if __name__ == '__main__':
   app.run_server(debug=True)