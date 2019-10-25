"""
Testing flops 24/7/365.
"""
import os
import time 
import numpy as np
import pandas as pd
import requests as r

#jwt = os.environ['jwt']

token="74b1aaf8ca3f131071be811964fd2987"

header_dat={'Authorization': f'Bearer {token}'}
url = "https://dev.tenants.aloedev.tacc.cloud/actors/v2"


actor_id = 'oOxoxDDvBDGWB'

all_data = pd.DataFrame()
for test_var in [9000]:
    nodes = 1
    workers_per_node = 6
    messages_per_worker = 5

    threads = 0        # set to 0 for all threads
    std_dev = 1000
    size = test_var
    executions = nodes * workers_per_node * messages_per_worker
    messageDat = f'{threads} {std_dev} {size}'
    runs = 2

    for run_num in range(1, runs + 1):
        print(f'Starting Run {run_num}.')
        msg_start = time.time()
        exec_id_list = []
        for i in range(executions):
            execution = r.post(f"{url}/{actor_id}/messages",
                               headers=header_dat,
                               data={'message':messageDat})
            exec_id = execution.json()['result']['executionId']
            exec_id_list.append(exec_id)
            print(f'\rCreated execution: {i+1}', end='')
        msg_end = time.time()

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
all_data.to_csv(f'{nodes}_nodes_{runs}_trials.csv')
