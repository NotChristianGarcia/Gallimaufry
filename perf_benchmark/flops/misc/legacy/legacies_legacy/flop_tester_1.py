"""
Testing flops 24/7/365.
"""
import os
import time 
import multiprocessing
import numpy as np
import pandas as pd
import requests as r
from datetime import datetime
from dateutil.parser import parse


jwt = os.environ['jwt']

header_dat = {'x-jwt-assertion-dev': jwt}
url = "http://129.114.104.189/actors"


runs = 5

actor_id = os.environ['actor_id']
nodes = int(os.environ['nodes'])
workers_per_node = 1
messages_per_worker = 1
executions = nodes * workers_per_node * messages_per_worker

threads = 0        # set to 0 for all threads
std_dev = 1000
size = 25000
msg_dat = f'{threads} {std_dev} {size}'

messager_inp = [actor_id, header_dat, msg_dat, url]
messager_iterator = [messager_inp] * executions

all_data = pd.DataFrame()

def send_actor_message(it):
    msg_send = r.post(f"{it[3]}/{it[0]}/messages",
                      headers=it[1], data={'message': it[2]})
    return msg_send.json()['result']['executionId']

for run_num in range(1, runs + 1):
    print('')
    print(f'Starting Run {run_num}.')

    pool = multiprocessing.Pool(processes=16)
    msg_start = time.time()
    exec_id_list = pool.map(send_actor_message, messager_iterator)
    pool.close()
    pool.join()
    msg_end = time.time()
    print('Messaging complete.')

    post_msg_start = time.time()
    non_complete_list = exec_id_list.copy()
    executions_completed = 0
    print(f'\rExecutions completed: {executions_completed}', end='')
    time.sleep(.5 * nodes)
    while non_complete_list:
        all_exec_reses = r.get(f"{url}/{actor_id}/executions",
                               headers=header_dat).json()
        for exec_res in all_exec_reses['result']['executions']:
            exec_id = exec_res['id']
            if (exec_id in non_complete_list) and (exec_res['status'] == 'COMPLETE'):
                executions_completed += 1
                print(f'\rExecutions completed: {executions_completed}', end='')
                non_complete_list.remove(exec_id)

    post_msg_end = time.time() 

    msg_time = msg_end - msg_start
    post_msg_time = post_msg_end - post_msg_start
 
    print('\nDoing analytics.')
    results_list = []
    whole_work_times = 0
    calc_times = 0
    exec_init_times = 0
    exec_run_times = 0
    for exec_id in exec_id_list:
        exec_logs = r.get(f"{url}/{actor_id}/executions/{exec_id}/logs",
		          headers=header_dat).json()['result']['logs']
        whole_work_time, calc_time = list(map(float, exec_logs.replace('\n','').split()))
        whole_work_times += whole_work_time
        calc_times += calc_time

        exec_res = r.get(f"{url}/{actor_id}/executions/{exec_id}",
                         headers=header_dat).json() ['result']
        msg_receive_time = parse(exec_res['messageReceivedTime'].replace(' ','T') + 'Z')
        exec_start_time = parse(exec_res['startTime'].replace(' ', 'T') + 'Z')
        exec_start_run_time = parse(exec_res['finalState']['StartedAt'])
        exec_end_run_time = parse(exec_res['finalState']['FinishedAt'])

        exec_init_time = (exec_start_run_time - exec_start_time).total_seconds()
        exec_run_time = (exec_end_run_time - exec_start_run_time).total_seconds()
        
        exec_init_times += exec_init_time
        exec_run_times += exec_run_time
    
    print(f"\n\nRun Number {run_num}")
    if threads:
        print(f"Threads: {threads}")
    print(f"Std Dev: {std_dev}")
    print(f"Size: {size}")
    print(f"Executions: {executions}")
    print(f"Message Time: {msg_time}")
    print(f"Post Msg Time: {post_msg_time}")
    print(f"Abaco Exec Init Time: {exec_init_times}")
    print(f"Abaco Exec Run Time: {exec_run_times}")
    print(f"Whole Work Time: {whole_work_times}")
    print(f"Calc Time: {calc_times}")

    run_data = pd.DataFrame(
        [[run_num, threads, std_dev, size, executions, msg_time, post_msg_time,
          exec_init_times, exec_run_times, whole_work_times, calc_times]],
        columns=['Run Number', 'Threads', 'Std Dev', 'Size', 'Executions',
                 'Message Time', 'Post Message Time', 'Exec Init Time',
                 'Exec Run Time', 'Whole Work Time', 'Calc Time'])
    all_data = all_data.append(run_data, ignore_index = True)
all_data.to_csv(f'data/{workers_per_node}_workers/{nodes}_nodes_{workers_per_node}_workers_{runs}_trials.csv')
