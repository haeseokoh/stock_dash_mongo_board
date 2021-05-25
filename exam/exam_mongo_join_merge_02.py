from libs.mongo_api import db_init

db_prj_progress = db_init('prj', 'prj_progress')

cursor = db_prj_progress.aggregate(f_col='plm_prj_code', l_field='개발모델명', f_field='model_name')

for x in list(cursor):
    print(x)

print(list(cursor.next().keys()))

# AttributeError: 'CommandCursor' object has no attribute 'find'
# print(list(cursor.find({}).next().keys()))

# AttributeError: 'CommandCursor' object has no attribute 'count_documents'
# print(cursor.count_documents())

# AttributeError: 'CommandCursor' object has no attribute 'skip'
# print(list(cursor.skip(2).limit(20)))

# AttributeError: 'CommandCursor' object has no attribute 'limit'
# print(list(cursor.limit(20)))
