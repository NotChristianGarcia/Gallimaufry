import requests as r
import multiprocessing
import time

def internet_resource_getter(it):
    response = r.post("https://dev.tenants.aloedev.tacc.cloud/actors/v2/PozyW1wkKJm4l/messages",
                       headers={'Authorization': 'Bearer 74b1aaf8ca3f131071be811964fd2987'},
                       data={'message':'0 1000 2'})

    return response.json()

for test in [4, 8]:
    start = time.time()
    pool = multiprocessing.Pool(processes=test)
    pool_outputs = pool.map(internet_resource_getter, range(300))
    pool.close()
    pool.join()
    print(f'{test} processes, {time.time() - start}')
    #print(pool_outputs)
