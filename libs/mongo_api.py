import pymongo
import pandas as pd

class DB:
    
    def __init__(self, database, collection):
        # print('db and col :', database, collection)
        if self.check(database, collection) is None:
            return

        self.db_client = pymongo.MongoClient("mongodb://localhost:27017/")

        # self.db_client = pymongo.MongoClient("mongodb://10.244.25.196:27017/")
        self.db_name = self.db_client[database]
        self.db_col = self.db_name[collection]
        
        # dblist = self.db_client.list_database_names()
        # print('db list : ', dblist)
        # if database in dblist:
        #     print("The {} database exists.".format(database))
        # else:
        #     print("The {} database  does not exists.".format(database))
        
        # collist = self.db_name.list_collection_names()
        # print('collection list : ', collist)
        # if collection in collist:
        #     print("The {} collection exists.".format(collection))
        # else:
        #     print("The {} collection does not exists.".format(collection))
    
    def __del__(self):
        if hasattr(self, 'db_client'):
            self.db_client.close()

    def check(self, db, col):
        if not db and not col:
            # print('check not db and not col :',db and col)
            return None
        if db=='' or col=='':
            # print('check db=='' or col=='' :',db and col)
            return None
        return True
    
    def insert(self, dict, id=None):
        if id == 'id':
            dict["_id"] = dict.get('id')
        elif id == 'cid':
            dict["_id"] = dict.get('cid')
        else:
            dict["_id"] = id
        x = self.db_col.insert_one(dict)
        return x
    
    def insert_many(self, dict):
        x = self.db_col.insert_many(dict)
        return x
    
    def find_one(self, dict):
        x = self.db_col.find_one(dict)
        return x
    
    def find(self, dict):
        x = self.db_col.find(dict)
        return x
    
    def find_all(self):
        x = self.db_col.find()
        return x
    
    def find_select(self, filter={}, dict={"title": 1, "search_key": 1}):
        x = self.db_col.find(filter, dict)
        return x
    
    # https://velopert.com/545
    def update_one(self, dict_query, dict_value):
        x = self.db_col.update_one(dict_query, dict_value, upsert=True)
        return x
    
    def update_many(self, dict_query, dict_value):
        x = self.db_col.update_many(dict_query, dict_value)
        return x

    def aggregate(self, f_col, l_field, f_field):
        # https://docs.mongodb.com/manual/reference/operator/aggregation/lookup/
        # Use $lookup with $mergeObjects
    
        # 가독성을 좋게 하는 코딩 스타일
        # https://www.fun-coding.org/mongodb_advanced8.html
        pipeline = list()
        pipeline.append({
            "$lookup": {
                "from": f_col,  # foreign col
                "localField": l_field,
                "foreignField": f_field,
                "as": "fromItems"
            }
        })
        pipeline.append({
            '$replaceRoot': {
                'newRoot': {
                    '$mergeObjects': [
                        '$$ROOT',
                        {'$arrayElemAt': ['$fromItems', 0]},
                    ]
                }
            }
        })
        pipeline.append({
            '$project': {
                'fromItems': 0
            },
        })
    
        cursor = self.db_col.aggregate(pipeline)
        return cursor


def db_init(database, collection):
    db = DB(database, collection)
    return db


def db_update(db, df, id=None):
    # df.rename(columns = {'old_nm' : 'new_nm'), inplace = True)
    # 출처: https://rfriend.tistory.com/468 [R, Python 분석과 프로그래밍의 친구 (by R Friend)]
    if id is not None:
        df.rename(columns={id: '_id'}, inplace=True)
    
    # https://stackoverflow.com/questions/20167194/insert-a-pandas-dataframe-into-mongodb-using-pymongo
    # db.insert_many(df.to_dict('records'))
    # https://stackoverflow.com/questions/42398600/do-bulk-inserts-update-in-mongodb-with-pymongo
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    operations = [pymongo.operations.ReplaceOne(
        filter={"_id": doc["_id"]},
        replacement=doc,
        upsert=True
    ) for doc in df.to_dict('records')]
    
    result = db.db_col.bulk_write(operations)
    return result


def db_replace(db, df, id=None):
    # df.rename(columns = {'old_nm' : 'new_nm'), inplace = True)
    # 출처: https://rfriend.tistory.com/468 [R, Python 분석과 프로그래밍의 친구 (by R Friend)]
    if id is not None:
        df.rename(columns={id: '_id'}, inplace=True)
    
    # https://stackoverflow.com/questions/20167194/insert-a-pandas-dataframe-into-mongodb-using-pymongo
    # db.insert_many(df.to_dict('records'))
    # https://stackoverflow.com/questions/42398600/do-bulk-inserts-update-in-mongodb-with-pymongo
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    operations = [pymongo.operations.ReplaceOne(
        filter={"_id": doc["_id"]},
        replacement=doc,
        upsert=True
    ) for doc in df.to_dict('records')]
    
    result = db.db_col.bulk_write(operations)
    return result

# filter for unique field
def db_update2(db, df, filter):
    # https://stackoverflow.com/questions/20167194/insert-a-pandas-dataframe-into-mongodb-using-pymongo
    # db.insert_many(df.to_dict('records'))
    # https://stackoverflow.com/questions/42398600/do-bulk-inserts-update-in-mongodb-with-pymongo
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    operations = [pymongo.operations.ReplaceOne(
        filter={filter: doc[filter]},
        replacement=doc,
        upsert=True
    ) for doc in df.to_dict('records')]
    
    result = db.db_col.bulk_write(operations)
    return result


def db_update3(db, df, filter):
    # https://stackoverflow.com/questions/20167194/insert-a-pandas-dataframe-into-mongodb-using-pymongo
    # db.insert_many(df.to_dict('records'))
    # https://stackoverflow.com/questions/42398600/do-bulk-inserts-update-in-mongodb-with-pymongo
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    operations = [pymongo.operations.UpdateOne(
        filter={filter: doc[filter]}, # filter={x.strip():doc[x.strip()] for x in filter.split(',')}, # <=pymongo.errors.BulkWriteError: batch op errors occurred
        update={"$set":doc},
        upsert=True
    ) for doc in df.to_dict('records')]
    
    result = db.db_col.bulk_write(operations)
    return result


def db_update4(db, df, filter):
    # # https://stackoverflow.com/questions/20167194/insert-a-pandas-dataframe-into-mongodb-using-pymongo
    # # db.insert_many(df.to_dict('records'))
    # # https://stackoverflow.com/questions/42398600/do-bulk-inserts-update-in-mongodb-with-pymongo
    # # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    # operations = [pymongo.operations.UpdateOne(
    #     filter={filter: doc[filter]},
    #     update={"$set": doc},
    #     upsert=True
    # ) for doc in df.to_dict('records')]
    #
    # result = db.db_col.bulk_write(operations)

    if len(filter.split(','))==2:
        df[filter]=df[filter.split(',')[0]]+df[filter.split(',')[1]]
    
    for doc in df.to_dict('records'):
        # remove all ''value contain keys
        # _doc = {k: v for k, v in doc.items() if v is not ''}
        # print(doc)

        myquery={filter: doc[filter]}
        # myquery = {filter.split(',')[0]: doc[filter.split(',')[0]]}
        newvalues = {"$set": doc}
        result = db.db_col.update_one(myquery, newvalues, upsert=True)
        # print(result, doc)
    
    return True


# not work
def db_update5(db, df, filter):
    # # https://stackoverflow.com/questions/20167194/insert-a-pandas-dataframe-into-mongodb-using-pymongo
    # # db.insert_many(df.to_dict('records'))
    # # https://stackoverflow.com/questions/42398600/do-bulk-inserts-update-in-mongodb-with-pymongo
    # # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    # for doc in df.to_dict('records'):
    for index, doc in df.iterrows():
    # for index, doc in df.itertuples(index=False):
        # remove all ''value contain keys
        # _doc = {k: v for k, v in doc.items() if v is not ''}
        print(doc)
        # doc is pandas.core.series.Series need to change dict -> heavy load
        myquery = {filter: doc[filter]}
        newvalues = {"$set": doc}
        result = db.db_col.update_one(myquery, newvalues, upsert=True)
        # print(result, doc)

    return True