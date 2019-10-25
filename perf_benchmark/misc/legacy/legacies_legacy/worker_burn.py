import os
import requests as r


token="74b1aaf8ca3f131071be811964fd2987"

header_dat={'Authorization': f'Bearer {token}'}
url = "https://dev.tenants.aloedev.tacc.cloud/actors/v2"


actor_id = os.environ['actor_id']
nodes = int(os.environ['nodes'])

# Get all current workers
worker_res = r.get(f"{url}/{actor_id}/workers",
                        headers=header_dat)
all_workers = []
for worker_info in worker_res.json()['result']:
    all_workers.append(worker_info['id'])
    
# Delete all current workers
for del_worker in all_workers:
    del_worker_res = r.delete(f"{url}/{actor_id}/workers/{del_worker}",
                        headers=header_dat)

# Spool up more workers!
worker_res = r.post(f"{url}/{actor_id}/workers",
                    headers=header_dat,
                    data={'num': nodes*6})

# Check on amount of workers
while True:
    worker_res = r.get(f"{url}/{actor_id}/workers",
                        headers=header_dat)
    num_workers = len(worker_res.json()['result'])
    if not num_workers == nodes*6:
        continue
    
    host_info = {}
    if num_workers:
        try:
            for worker_info in worker_res.json()['result']:
                worker_info['hostId']
            break
        except KeyError:
            continue
