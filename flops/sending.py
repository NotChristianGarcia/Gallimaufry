import requests as r
import multiprocessing
import time

def internet_resource_getter(it):
    response = r.post("https://dev.tenants.aloedev.tacc.cloud/actors/v2/YJE3V4qQ5rA5/messages",
                       headers={'Authorization': 'Bearer 74b1aaf8ca3f131071be811964fd2987'},
                       data={'message':'0 1000 2'})

    return response.json()

start = time.time()
pool = multiprocessing.Pool(processes=8)
pool_outputs = pool.map(internet_resource_getter, range(200))
pool.close()
pool.join()
print(time.time() - start)
print(pool_outputs)
