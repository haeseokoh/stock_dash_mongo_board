from libs.mongo_api import db_init

def mongo_aggregate(db, l_col, f_col, l_field, f_field):
    # https://docs.mongodb.com/manual/reference/operator/aggregation/lookup/
    # Use $lookup with $mergeObjects
    
    # 가족성을 좋게 하는 코딩 스타일
    # https://www.fun-coding.org/mongodb_advanced8.html
    pipeline = list()
    pipeline.append({
        "$lookup":{
            "from": f_col, # foreign col
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
    
    db = db
    collection = l_col
    db_prj_progress = db_init(db, collection)

    cursor = db_prj_progress.db_col.aggregate(pipeline)
    return cursor

cursor = mongo_aggregate(db='prj', l_col='prj_progress', f_col='plm_prj_code', l_field='개발모델명', f_field='model_name')

for x in list(cursor):
    print(x)