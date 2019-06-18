"""
Testing flops 24/7/365.
"""
import os
import time 
import multiprocessing
import numpy as np
import pandas as pd
import requests as r

token="74b1aaf8ca3f131071be811964fd2987"

header_dat={'Authorization': f'Bearer {token}'}
url = "https://dev.tenants.aloedev.tacc.cloud/actors/v2"


runs = 5

actor_id = os.environ['actor_id']
nodes = int(os.environ['nodes'])
workers_per_node = 6
messages_per_worker = 5
executions = nodes * workers_per_node * messages_per_worker

threads = 0        # set to 0 for all threads
std_dev = 1000
size = 8000
msg_dat = f'{threads} {std_dev} {size}'

messager_inp = [actor_id, header_dat, msg_dat]
messager_iterator = [messager_inp] * executions

all_data = pd.DataFrame()

def send_actor_message(it):
    msg_send = r.post(f"https://dev.tenants.aloedev.tacc.cloud/actors/v2/{it[0]}/messages",
                      headers=it[1], data={'message': it[2]})
    return msg_send.json()['result']['executionId']


for run_num in range(1, runs + 1):
    print(f'Starting Run {run_num}.')

    pool = multiprocessing.Pool(processes=16)
    msg_start = time.time()
    exec_id_list = pool.map(send_actor_message, messager_iterator)
    pool.close()
    pool.join()
    msg_end = time.time()

    print(exec_id_list)

    exec_start = time.time()
    results_list = []
	
    executions_completed = 0
    while exec_id_list:
         for exec_id in exec_id_list:
              exec_logs = r.get(f"{url}/{actor_id}/executions/{exec_id}/logs",
				headers=header_dat)

         logs = exec_logs.json()['result']['logs']
         if logs:
             print(f'\rExecutions completed: {executions_completed + 1}', end='')
             results_list.append([f'id - {exec_id}', float(logs.replace('\n',''))])
             exec_id_list.remove(exec_id)
             executions_completed += 1
    exec_end = time.time()

    work_time = 0
    for res in results_list:
        work_time += res[1]

    print(f"\n\nRun Number {run_num}")
    if threads:
        print(f"Threads: {threads}")
    print(f"Std Dev: {std_dev}")
    print(f"Size: {size}")
    print(f"Executions: {executions}")
    print(f"Message Time: {msg_end - msg_start}")
    print(f"Exec Time: {exec_end - exec_start}")
    print(f"Work Time: {work_time}")
    print('\n')

    run_data = pd.DataFrame([[run_num, threads, std_dev, size, executions, msg_end - msg_start, exec_end - exec_start, work_time]],
                            columns=['Run Number', 'Threads', 'Std Dev', 'Size', 'Executions', 'Message Time', 'Exec Time', 'Work Time'])
    all_data = all_data.append(run_data, ignore_index = True)
all_data.to_csv(f'data/{workers_per_node}_workers/{nodes}_nodes_{workers_per_node}_workers_{runs}_trials.csv')
