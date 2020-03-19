import redis
import json
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27015')
db = client.abaco

# Mongo Conversion
# Helper functions that converts Mongo to new formatting
def updateMongoLogs(old_json, executions):
    newList = []
    for actor in old_json:
        aid = actor['_id']
        newDict = {'exp': actor['exp'], '_id': aid, 'logs': actor[aid]}
        newList.append(newDict)
        
    for log in newList:
        wanted_exec_id = log['_id']
        for execution in executions:
            for exec_id, exec_info in execution.items():
                if exec_id == '_id':
                    continue
                if exec_id == wanted_exec_id:
                    log['actor_id'] = execution['_id']
                    log['tenant'] = exec_info['tenant']
                    break
    return newList

def updateMongoPermissions(old_json):
    newList = []
    for actor in old_json:
        aid = actor['_id']
        newDict = {'_id': aid}
        newDict.update(actor[aid])
        newList.append(newDict)
    return newList

def updateMongoExecutions(old_json):
    newList = []
    for actor in old_json:
        aid = actor['_id']
        newDict = {'_id': aid}
        newDict.update(actor[aid])
        newList.append(newDict)
    return newList

def updateMongoClients(old_json):
    newList = []
    for actor in old_json:
        aid = actor['_id']
        newDict = {'_id': aid}
        newDict.update(actor[aid])
        newList.append(newDict)
    return newList

# Redis Conversion
# Helper function that converts a Redis DB into a JSON dict
def redis2dict(db):
    allDocs = []
    redisDB = redis.Redis(db=db, port=6397)
    for key in redisDB.scan_iter():
        key = key.decode('utf-8')
        jsonDict = json.loads(redisDB.get(key))
        jsonDict['_id'] = key
        allDocs.append(jsonDict)
    return allDocs

old_logs_store_json = list(db['1'].find({}))
old_permissions_store_json = list(db['2'].find({}))
old_executions_store_json = list(db['3'].find({}))
old_clients_store_json = list(db['4'].find({}))
old_actors_store_json = redis2dict('1')
old_workers_store_json = redis2dict('2')
old_nonce_store_json = redis2dict('3')
old_alias_store_json = redis2dict('4')
old_pregen_clients_json = redis2dict('5')

converted_permissions = updateMongoPermissions(old_permissions_store_json)
converted_executions = updateMongoExecutions(old_executions_store_json)
converted_clients = updateMongoClients(old_clients_store_json)
converted_actors = old_actors_store_json
converted_workers = old_workers_store_json
converted_nonces = old_nonce_store_json
converted_aliases = old_alias_store_json
converted_pregen = old_pregen_clients_json
converted_logs = updateMongoLogs(old_logs_store_json, converted_executions)

db_naming = {'n1': converted_logs,
             'n2': converted_permissions,
             'n3': converted_executions,
             'n4': converted_clients,
             'n5': converted_actors,
             'n6': converted_workers,
             'n7': converted_nonces,
             'n8': converted_aliases,
             'n9': converted_pregen}

# Convert and upload modified data
for db_name, db_data in db_naming.items(): 
    try:
        print(f"Currently processing db: {db_name}")
        db[db_name].drop()
        db[db_name].insert_many(db_data)
    except TypeError:
        pass
