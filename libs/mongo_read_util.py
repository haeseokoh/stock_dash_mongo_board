import ast
import re
import traceback

from libs.mongo_api import db_init
from libs.mongo_db_analyzer import db_read_colums_data_form_option

operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['and '],
             ['or ', ],
             ['contains '],
             ['datestartswith '],
             ['multiselect ', ],
             ]


def rearrange_filter_part(filter_part):
    for x in ['and', 'or']:
        test_set = 'contains "{}'.format(x)
        if test_set in filter_part:
            name_part, value_part = filter_part.split(' contains "', 1)
            # print('rearrange_filter_part:','{} {}'.format(name_part,value_part[:-1]))
            return '{} {}'.format(name_part, value_part[:-1])
    
    return filter_part


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]
                
                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part
                
                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value
    
    return [None] * 3


def mongodb_filter_simple_build(col_name, query_string, oper='$or'):
    myquery = {col_name: {oper: query_string}}
    return myquery

def mongodb_filter_build_none_re(col_name, query_string, multi_oper='$or'):
    # https://stackoverflow.com/questions/23474628/pymongo-find-by-multiple-values
    myquery = {col_name: {'$in': ast.literal_eval(query_string)}}
    
    return myquery


def mongodb_filter_build(col_name, query_string, multi_oper='$or'):
    print(col_name, query_string)
    # split_order = r'[^,\s]+'
    split_order = r'[^,]+'
    search_re = r".*(?=.*{}).*"  # r"^(?=.*{}).*" missing "/nXXXXX" cass
    
    myquery = {multi_oper: []}
    key = col_name
    print(re.findall(split_order, query_string))
    for x in re.findall(split_order, query_string):
        regexr = search_re.format(x.strip())
        regexri = re.compile(regexr, re.IGNORECASE)
        item = {key: {"$regex": regexri}}
        myquery[multi_oper].append(item)
    
    return myquery


def filter_parser_2_mongodb(filter_query, sort_by, editable_table):
    # https://dash.plotly.com/datatable/callbacks  ... Backend Paging with Filtering and Multi-Column Sorting
    filtering_expressions = filter_query.split(' && ')
    print('filtering_expressions:', filtering_expressions, 'filter_query:', filter_query, 'editable:', editable_table,
          any(editable_table))
    
    myquery = {"$and": []}
    
    for filter_part in filtering_expressions:
        filter_part = rearrange_filter_part(filter_part)
        col_name, operator, filter_value = split_filter_part(filter_part)
        print("col_name:{}  operator:{}  filter_value:{}".format(col_name, operator, filter_value))
        
        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            myquery_inner = mongodb_filter_simple_build(col_name, filter_value, '$' + operator)
            myquery["$and"].append(myquery_inner)
        elif operator == 'contains' or operator == 'or':
            myquery_inner = mongodb_filter_build(col_name, filter_value)
            myquery["$and"].append(myquery_inner)
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            pass
        elif operator == 'multiselect':
            myquery_inner = mongodb_filter_build_none_re(col_name, filter_value, '$or')
            myquery["$and"].append(myquery_inner)
        elif operator == 'and':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            myquery_inner = mongodb_filter_build(col_name, filter_value, multi_oper='$and')
            myquery["$and"].append(myquery_inner)
    
    # check filtering_expressions: ['']
    if myquery["$and"] == []:
        myquery = {}
    
    print('update_output myquery :', myquery)
    
    sort = []
    if len(sort_by):
        print([col['column_id'] for col in sort_by], [col['direction'] for col in sort_by])
        # [('prj_name', 1), ('model_name', -1)]
        for col in sort_by:
            if col['direction'] == 'asc':
                sort.append((col['column_id'], 1))
            elif col['direction'] == 'desc':
                sort.append((col['column_id'], -1))
    
    print('update_output sort :', sort)
    
    return myquery, sort

def read_contents(db, collection, page_view_size, offset, myquery={}, sort=[], full=False, link_field=[]):
    # print(db, collection)
    
    data = []
    columns = []
    page_count = 0
    
    try:
        db_inst = db_init(db, collection)
        columns_order = {}

        columns, collection_option = db_read_colums_data_form_option(db, collection)
        
        for x in columns:
            columns_order[x] = 1
        print('columns_order :', columns_order)
        
        if len(sort):
            cursor = db_inst.find_select(myquery, columns_order).sort(sort)
        else:
            cursor = db_inst.find_select(myquery, columns_order)
            
        total_size = db_inst.db_col.count_documents(myquery)
        print('total_size:', total_size, 'columns:', columns, )
        
        if page_view_size is not None:
            if not full:
                for x in cursor.skip(page_view_size * offset).limit(page_view_size):
                    x['_id'] = '{}'.format(x['_id'])
                    # if x.get('duration'):
                    #     del x['duration']
                    data.append(x)
            else:
                for x in cursor:
                    x['_id'] = '{}'.format(x['_id'])
                    data.append(x)
        else:
            # data = list(cursor)
            for x in cursor:
                x['_id'] = '{}'.format(x['_id'])
                data.append(x)

        # print(data)
        print('len(data) :', full, len(data))

        div, mod = divmod(total_size, page_view_size)
        page_count = div + (1 if mod else 0)

        columns = [{'name': i, 'id': i, "hideable": "last", } for i in columns]
    except Exception as e:
        print(e)
        traceback.print_exc()
    

    
    tooltip_data = [
        {
            column: {'value': str(value), 'type': 'markdown'} if (len(str(value)) > 20) & (
                False if column in link_field else True) else None
            for column, value in row.items()
        } for row in data
    ]
    
    return data, columns, tooltip_data, page_view_size, page_count