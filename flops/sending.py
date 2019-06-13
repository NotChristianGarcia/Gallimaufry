import requests as r
import multiprocessing
import time

start = time.time()
def internet_resource_getter(it):
    stuff_got = []
    response = r.post("https://dev.tenants.aloedev.tacc.cloud/actors/v2/qAMA8MLmwGkb3/messages",
                       headers={'Authorization': 'Bearer 74b1aaf8ca3f131071be811964fd2987'},
                       data={'message':'0 1000 2'})

    stuff_got.append(response.json())

    return stuff_got


pool = multiprocessing.Pool(processes=8)
pool_outputs = pool.map(internet_resource_getter, range(200))
pool.close()
pool.join()
print(time.time() - start)
