

import pandas as pd
from pymongo import MongoClient

# https://stackoverflow.com/questions/20167194/insert-a-pandas-dataframe-into-mongodb-using-pymongo/49127811
from pymongo.errors import BulkWriteError

from libs.mongo_api import db_update4, db_init


def write_df_to_mongoDB(  df,database_name='test', collection_name='test_collectionname', server='localhost',  mongodb_port=27017, chunk_size=100, destroy=False, unique_field=None ):
    #"""
    #This function take a list and create a collection in MongoDB (you should
    #provide the database name, collection, port to connect to the remoete database,
    #server of the remote database, local port to tunnel to the other machine)
    #
    #---------------------------------------------------------------------------
    #Parameters / Input
    #    my_list: the list to send to MongoDB
    #    database_name:  database name
    #
    #    collection_name: collection name (to create)
    #    server: the server of where the MongoDB database is hosted
    #        Example: server = 'XXX.XXX.XX.XX'
    #    this_machine_port: local machine port.
    #        For example: this_machine_port = '27017'
    #    remote_port: the port where the database is operating
    #        For example: remote_port = '27017'
    #    chunk_size: The number of items of the list that will be send at the
    #        some time to the database. Default is 100.
    #
    #Output
    #    When finished will print "Done"
    #----------------------------------------------------------------------------
    #FUTURE modifications.
    #1. Write to SQL
    #2. Write to csv
    #----------------------------------------------------------------------------
    #30/11/2017: Rafael Valero-Fernandez. Documentation
    #"""



    #To connect
    # import os
    # import pandas as pd
    # import pymongo
    # from pymongo import MongoClient

    client = MongoClient(server,int(mongodb_port))
    db = client[database_name]
    collection = db[collection_name]
    collection_option = db[collection_name +'_option']
    # To write
    if destroy:
        collection.delete_many({})  # Destroy the collection
    # #aux_df=aux_df.drop_duplicates(subset=None, keep='last') # To avoid repetitions
    # my_list = my_df.to_dict('records')
    # l =  len(my_list)
    # ran = range(l)
    # steps=ran[chunk_size::chunk_size]
    # steps.extend([l])
    #
    # # Inser chunks of the dataframe
    # i = 0
    # for j in steps:
    #     print(j)
    #     collection.insert_many(my_list[i:j]) # fill de collection
    #     i = j

    _columns = []
    for x in df.columns.to_list():
        # todo: mongodb에서 .은 하위 카테고리로 분류 하게 되어 오류를 발생 시키는 듯함
        _columns.append(x.rstrip('.').replace('.', '').replace('\n', ' '))
    df.columns = _columns
    df = df.fillna('')

    df2dict = df.to_dict(orient='records')  # Here's our added param..

    # if unique_field!=None:
    #     if len(unique_field.split(','))==2:
    #         df[unique_field]=df[unique_field.split(',')[0]]+df[unique_field.split(',')[1]]
    #     collection.create_index(unique_field, unique=True)
        
    # https://stackoverflow.com/questions/37435589/insert-many-with-upsert-pymongo
    # Todo : 업데이트는 안된다, BulkWriteError로 skip
    # try:
    #     collection.insert_many(df2dict, ordered=False)
    # except BulkWriteError:
    #     pass
    if unique_field != None:
        _db = db_init(database_name, collection_name)
        _db.db_col.create_index(unique_field, unique=True)
        db_update4(_db, df, unique_field)
    else:
        collection.insert_many(df2dict)
        
    collection_option.update_one({'value': 'columns'}, {"$set": {'value': 'columns', 'option': _columns}}, upsert=True)

    print('Done')
    return


data = pd.read_excel(r'C:\Users\haeseok\Downloads\간단SVC_S21 한국향 간단SVC 이슈 분석현황_test.xlsx')
print(data)
write_df_to_mongoDB(data, collection_name = 'test_간단SVC_S21_0', destroy=False)

data = pd.read_excel(r'C:\Users\haeseok\Downloads\DEFECT_LIST_20210309_tracking+board.xls')
print(data)
write_df_to_mongoDB(data, collection_name = 'test_PLM_0', destroy=False, unique_field='사례코드')
