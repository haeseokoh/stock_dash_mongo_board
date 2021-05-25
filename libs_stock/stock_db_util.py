from datetime import datetime, timedelta
from libs.mongo_api import db_init

def update_db(df, wanted, database_name = 'stock', collection_name = 'bin', unique_field = '날짜'):
    # -> dash의 selected_row_ids 를 위해sise_group
    df.reset_index(inplace=True, drop=False)
    df.rename(columns={'index': 'id'}, inplace=True)

    dict = df.to_dict('records')
    today = datetime.today().strftime('%Y%m%d')

    _db = db_init(database_name, collection_name)
    _db.db_col.create_index(unique_field, unique=True)
    # _db.db_col.insert_one({}, {unique_field:today, 'name': 'KOSDAQ_sise', 'file': dict }, upsert=True)
    doc = {unique_field: today, wanted: dict}
    myquery = {unique_field: doc[unique_field]}
    newvalues = {"$set": doc}
    _db.db_col.update_one(myquery, newvalues, upsert=True)


def read_datalist(wanted, database_name ='stock', collection_name ='bin'):
    today = datetime.today().strftime('%Y%m%d')

    _db = db_init(database_name, collection_name)

    filter = {'날짜': {'$eq': today}}
    dict = {'_id':0, wanted: 1}
    result = _db.db_col.find_one(filter, dict)

    # print('read_datalist from db')
    # print('read_df result :',result)

    if result is not None:
        # print(result[wanted])
        return result.get(wanted)
    else:
        return None


def update_naver_view_config(columns, wanted, database_name='stock', collection_name='naver_view_config'):
    selected = read_naver_view_config(wanted)

    if len(selected):
        columns = selected

    return columns

def save_naver_view_config(columns, wanted, database_name='stock', collection_name='naver_view_config'):
    _db = db_init(database_name, collection_name)
    _db.db_col.create_index('key', unique=True)
    # _db.db_col.insert_one({}, {unique_field:today, 'name': 'KOSDAQ_sise', 'file': dict }, upsert=True)

    doc = {'key': wanted, 'value': columns}
    myquery = {'key': wanted}
    newvalues = {"$set": doc}
    _db.db_col.update_one(myquery, newvalues, upsert=True)


def read_naver_view_config(wanted, database_name='stock', collection_name='naver_view_config'):
    _db = db_init(database_name, collection_name)

    filter = {'key': {'$eq': wanted}}
    dict = {'_id':0, 'value':1}
    result = _db.db_col.find_one(filter, dict)

    print('read_naver_view_config')
    print('read_df result :',result)

    if result is not None:
        print(result.get('value'))
        return result.get('value')
    else:
        return []

def delete_record(wanted , unique_field = '날짜'):
    today = datetime.today().strftime('%Y%m%d')

    database_name = 'stock'
    collection_names = ['bin', 'group', 'theme', 'upjong', 'wise_thewm']

    for collection_name in collection_names:
        _db = db_init(database_name, collection_name)
        _db.db_col.create_index(unique_field, unique=True)
        myquery = {unique_field: today}
        _db.db_col.delete_one(myquery)