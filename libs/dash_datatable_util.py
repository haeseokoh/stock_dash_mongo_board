import datetime

import dash_table

from libs.mongo_read_util import rearrange_filter_part, split_filter_part, mongodb_filter_simple_build, \
    mongodb_filter_build, mongodb_filter_build_none_re


def datatable_rw_layout(editable):
    return dash_table.DataTable(
                id='output-data-read-online',
                data=[],
                columns=[],
                # style_as_list_view=True,
                style_cell={'textAlign': 'left',
                            'textOverflow': 'ellipsis',
                            'maxWidth': '240px',
                            },
                tooltip_data=[],

                page_current=0,
                page_size = 20,
                page_action='custom',

                filter_action='custom',
                filter_query='',

                sort_action='custom',
                sort_mode='multi',
                sort_by=[],

                editable=editable,

                export_format='xlsx',
                export_headers='display',
                style_table={'overflowX': 'scroll'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                css=[
                    {'selector': '.dash-spreadsheet-menu', 'rule':'position:absolute; bottom:-30px'},  # move below table
                    {'selector': '.export', 'rule':'position:absolute; bottom: -0px; border-radius:5px; border-width:1px; border-color:#6c757d'}, # move below table
                    {'selector': '.show-hide', 'rule': 'border-radius:5px; border-width:1px; border-color:#6c757d'}, # move below table
                ]
            )


# https://stackoverflow.com/questions/23581128/how-to-format-date-string-via-multiple-formats-in-python
def try_parsing_date(text):
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d',):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')
