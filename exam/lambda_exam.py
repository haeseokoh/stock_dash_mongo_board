


# for x in filter.split(','):
#     {x: doc[x]}


# operations = [pymongo.operations.UpdateOne(
#     filter={filter: doc[filter]},
#     update={"$set": doc},
#     upsert=True
# ) for doc in df.to_dict('records')]
#
# result = db.db_col.bulk_write(operations)

def bulk_write(x):
    print(x)
    return x

def UpdateOne(filter, update):
    print(filter, update)
    return {'filter':filter, 'update':update}

data_to_be_updated = [
    {"sourceID": 6, "source": "test", "name": "simon"},
    {"sourceID": 8, "source": "test", "name": "greg"},
    {"sourceID": 9, "source": "test", "name": "julie"},
    {"sourceID": 10, "source": "test", "name": "john"}
]

result = bulk_write([
    UpdateOne(filter={'sourceID': d['sourceID']},
              update={'$set': {'name': d['name'],'source': d['source']}}
              )for d in data_to_be_updated])

result = bulk_write([
    UpdateOne(filter={'sourceID': d['sourceID'], 'source': d['source']},
              update={'$set': {'name': d['name'],'source': d['source']}}
              )for d in data_to_be_updated])


filter = 'sourceID,source'

result = bulk_write([
    UpdateOne(filter={ x:d[x] for x in filter.split(',') },
              update={'$set': {'name': d['name'],'source': d['source']}}
              )for d in data_to_be_updated])

filter = 'sourceID'

result = bulk_write([
    UpdateOne(filter={ x:d[x] for x in filter.split(',') },
              update={'$set': {'name': d['name'],'source': d['source']}}
              )for d in data_to_be_updated])