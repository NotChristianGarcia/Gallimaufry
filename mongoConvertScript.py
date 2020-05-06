import redis
import json
from pymongo import MongoClient
client1 = MongoClient('mongodb://localhost:27015')
db1 = client1.abaco

client2 = MongoClient('mongodb://localhost:27015')
db2 = client2.abaco

# Mongo Conversion
# Helper functions that converts Mongo to new formatting
def convertLogs(base_list, executions):
    copied_list = copy.deepcopy(base_list)
    newList = []
    for actor in copied_list:
        aid = actor['_id']
        newDict = {'exp': actor['exp'], '_id': aid, 'logs': actor[aid]}
        newList.append(newDict)
        
    for log in newList:
        wanted_exec_id = log['_id']
        for execution in executions:
            if execution['id'] == wanted_exec_id:
                log['actor_id'] = execution['actor_id']
                log['tenant'] = execution['tenant']
                break
    return newList

def convertPermissions(base_list):
    copied_list = copy.deepcopy(base_list)
    newList = []
    for actor in copied_list:
        aid = actor['_id']
        newDict = {'_id': aid}
        newDict.update(actor[aid])
        newList.append(newDict)
    return newList

def convertExecutions(base_list):
    copied_list = copy.deepcopy(base_list)
    newList = []
    for actor_outer in copied_list:
        del actor_outer['_id']
        for aid, execution in actor_outer.items():
            for exec_id, exec_dict in execution.items():
                exec_dict['_id'] = f"{aid}_{exec_id}"
                if exec_dict.get('start_time'):
                    exec_dict['start_time'] = unix_to_dt(exec_dict['start_time'])
                if exec_dict.get('message_received_time'):
                    exec_dict['message_received_time'] = unix_to_dt(exec_dict['message_received_time'])
                if exec_dict.get('final_state'):
                    if exec_dict.get('final_state').get('StartedAt'):
                        exec_dict['final_state']['StartedAt'] = docker_time_to_dt(exec_dict['final_state']['StartedAt'])
                    if exec_dict.get('final_state').get('FinishedAt'):
                        exec_dict['final_state']['FinishedAt'] = docker_time_to_dt(exec_dict['final_state']['FinishedAt'])
                newList.append(exec_dict)
    return newList

def convertClients(base_list):
    copied_list = copy.deepcopy(base_list)
    newList = []
    for actor in copied_list:
        aid = actor['_id']
        newDict = {'_id': aid}
        newDict.update(actor[aid])
        newList.append(newDict)
    return newList


# Redis Conversion
# Helper functions that converts Redis to new formatting
def convertActors(base_list):
    copied_list = copy.deepcopy(base_list)
    for actor_dict in copied_list:
        if actor_dict.get('last_update_time'):
            actor_dict['last_update_time'] = unix_to_dt(actor_dict['last_update_time'])
        if actor_dict.get('create_time'):
            actor_dict['create_time'] = unix_to_dt(actor_dict['create_time'])
    return copied_list

def convertWorkers(base_list):
    copied_list = copy.deepcopy(base_list)
    newList = []
    for actor in copied_list:
        aid = actor.pop('_id')
        for worker_id, worker_dict in actor.items():
            worker_dict['_id'] = f"{aid}_{worker_id}"
            worker_dict['actor_id'] = aid
            if worker_dict.get('create_time'):
                worker_dict['create_time'] = unix_to_dt(worker_dict['create_time'])
            if worker_dict.get('last_health_check_time'):
                worker_dict['last_health_check_time'] = unix_to_dt(worker_dict['last_health_check_time'])
            newList.append(worker_dict)
    return newList

def convertNonces(base_list):
    copied_list = copy.deepcopy(base_list)
    for nonce in copied_list:
        for nonce_id, nonce_dict in nonce.items():
            if not nonce_id == "_id":
                if nonce_dict.get('last_use_time'):
                    nonce_dict['last_use_time'] = unix_to_dt(nonce_dict['last_use_time'])
                if nonce_dict.get('create_time'):
                    nonce_dict['create_time'] = unix_to_dt(nonce_dict['create_time'])
    return copied_list

# Redis Reader
# Helper function that reads a Redis DB into a JSON dict
def redis2dict(db):
    allDocs = []
    redisDB = redis.Redis(db=db, port=6379)
    for key in redisDB.scan_iter():
        key = key.decode('utf-8')
        jsonDict = json.loads(redisDB.get(key))
        jsonDict['_id'] = key
        allDocs.append(jsonDict)
    return allDocs

# Metrics database creation
def createMetrics(base_list):
    actor_dbids = []
    actor_total = 0
    execution_dbids = []
    execution_total = 0

    copied_list = copy.deepcopy(base_list)

    for actor in copied_list:
        actor_dbids.append(actor.pop('_id'))
        actor_total += 1
        for _, actor_inner in actor.items():
            for _, execution in actor_inner.items():
                execution_dbids.append(f'{execution["actor_id"]}_{execution["id"]}')
                execution_total += 1
                
    metrics = [{'_id': 'stats',
                'actor_total': actor_total,
                'actor_dbids': actor_dbids,
                'execution_total': execution_total,
                'execution_dbids': execution_dbids}]
    return metrics

def unix_to_dt(unix):
    return datetime.datetime.utcfromtimestamp(float(unix))

def docker_time_to_dt(docker_time):
    return datetime.datetime.strptime(docker_time.replace('Z', '')[:-1], "%Y-%m-%dT%H:%M:%S.%f")

base_logs_store_json = list(db1['1'].find({}))
base_permissions_store_json = list(db1['2'].find({}))
base_executions_store_json = list(db1['3'].find({}))
base_clients_store_json = list(db1['4'].find({}))
base_actors_store_json = redis2dict('1')
base_workers_store_json = redis2dict('2')
base_nonce_store_json = redis2dict('3')
base_alias_store_json = redis2dict('4')
base_pregen_clients_json = redis2dict('5')

converted_permissions = convertPermissions(base_permissions_store_json)
converted_executions = convertExecutions(base_executions_store_json)
converted_clients = convertClients(base_clients_store_json)
converted_actors = convertActors(base_actors_store_json)
converted_workers = convertWorkers(base_workers_store_json)
converted_nonces = convertNonces(base_nonce_store_json)
converted_aliases = base_alias_store_json
converted_pregen = base_pregen_clients_json
converted_logs = convertLogs(base_logs_store_json, converted_executions)
new_metrics = createMetrics(base_executions_store_json)

db_naming = {'n1': converted_logs,
             'n2': converted_permissions,
             'n3': converted_executions,
             'n4': converted_clients,
             'n5': converted_actors,
             'n6': converted_workers,
             'n7': converted_nonces,
             'n8': converted_aliases,
             'n9': converted_pregen,
             'n10': new_metrics}

# Convert and upload modified data
for db_name, db_data in db_naming.items(): 
    try:
        print(f"Currently processing db: {db_name}")
        db2[db_name].drop()
        db2[db_name].insert_many(db_data)
    except TypeError:
        pass