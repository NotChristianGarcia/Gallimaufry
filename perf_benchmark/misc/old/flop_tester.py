"""
Testing flops 24/7/365.
"""
import os
import time
import argparse
import pandas as pd
import requests as r

def input_parsing():
    parser = argparse.ArgumentParser(
        description="{threads} {std_dev} {size} {executions}")
    parser.add_argument('threads', help="Amount of max threads to use")
    parser.add_argument('std_dev', help="Standard deviation")
    parser.add_argument('size', help="Size of square matrix")
    parser.add_argument('executions', help="Amount of executions to do")

    parser.add_argument('-u', '--url', default="http://localhost:8000",
                        help="URL of abaco instance")
    parser.add_argument('-a', '--auth', default='jwt', choices=['jwt', 'token'],
                        help="Either pick JWT or token for authentication")
    parser.add_argument('-t', '--trials', default=1, help="Amount of times to run")
    parser.add_argument('-w', '--workers_wanted', default=1, help="# of workers")
    parser.add_argument('-s', '--data_get', default=True, help="Save data bool")
    args = parser.parse_args()

    url = args.url
    auth = args.auth

    if auth == 'jwt':
        try:
            jwt = os.environ.get('jwt')
        except Exception as e:
            print(e)
        auth = {'X-Jwt-Assertion-TEST':jwt}
    elif auth == 'token':
        try:
            token = os.environ.get('token')
        except Exception as e:
            print(e)
        auth = {'Authorization': f'Bearer {token}'}

    return url, auth, args


def actor_creation(url, auth):
    # Actor that will be creating workers with flop test.
    actor = r.post(f"{url}/actors",
                   headers=auth,
                   data={'image':'notchristiangarcia/flops_test:4.0'})
    actor_id = actor.json()['result']['id']

    with open('actor.txt', 'w') as actor_file:
        actor_file.write(actor_id)
    return actor_id


def worker_check(url, auth, actor_id, workers_wanted):
    r.post(f"{url}/actors/{actor_id}/workers",
           headers=auth, data={'num': workers_wanted})
    while True:
        worker_res = r.get(f"{url}/actors/{actor_id}/workers",
                           headers=auth)
        curr_workers = len(worker_res.json()['result'])
        if curr_workers == workers_wanted:
            print(f"Worker check complete, {curr_workers} available.")
            break
        print(f"Workers spooling, {curr_workers} of {workers_wanted} ready.")
        time.sleep(3)


def executor(url, auth, actor_id, args):
    message_dat = f'{args.threads} {args.std_dev} {args.size}'
    # Executions of this actor, lots of times.
    exec_id_list = []
    for _ in range(int(args.executions)):
        execution = r.post(f"{url}/actors/{actor_id}/messages",
                           headers=auth,
                           data={'message': message_dat})
        exec_id = execution.json()['result']['executionId']
        exec_id_list.append(exec_id)
    return exec_id_list


def results_get(url, auth, actor_id, exec_id_list):
    # Getting result of exec from log once exec complete.
    results_list = []
    while exec_id_list:
        for exec_id in exec_id_list:
            exec_logs = r.get(
                f"{url}/actors/{actor_id}/executions/{exec_id}/logs",
                headers=auth)

            logs = exec_logs.json()['result']['logs']
            if logs:
                print('. ', end='')
                results_list.append([f'id - {exec_id}',
                                     float(logs.replace('\n', ''))])
                exec_id_list.remove(exec_id)
    return results_list

def data_capture(args, results_list, all_data, run_num, msg_time, exec_time):
    work_time = 0
    for res in results_list:
        work_time += res[1]

    print(f"\nRun Number {run_num}")
    print(f"Threads: {args.threads}")
    print(f"Std Dev: {args.std_dev}")
    print(f"Size: {args.size}")
    print(f"Executions: {args.executions}")
    print(f"Message Time: {msg_time}")
    print(f"Exec Time: {exec_time}")
    print(f"Work Time: {work_time}\n")

    size = int(args.size)
    executions = int(args.executions)
    flo = size**2*(2*size-1)
    print(f"FLO/exec: {flo}")
    print(f"FLO total: {flo*executions}")
    print(f"Exec FLOPS: {(flo*executions)/exec_time}")
    print(f"Exec GFLOPS: {((flo*executions)/exec_time)/1000000000}")
    print(f"Work FLOPS: {(flo*executions)/work_time}")
    print(f"Work GFLOPS: {((flo*executions)/work_time)/1000000000}\n")

    run_data = pd.DataFrame([[run_num, args.threads, args.std_dev, args.size,
                              args.executions, msg_time, exec_time, work_time]],
                            columns=['Run Number', 'Threads', 'Std Dev', 'Size',
                                     'Executions', 'Message Time', 'Exec Time',
                                     'Work Time'])
    all_data.append(run_data, ignore_index=True)



def main():
    url, auth, args = input_parsing()

    try:
        with open('actor.txt', 'r') as actor_file:
            actor_id = actor_file.read().replace('\n', '')
    except:
        actor_id = actor_creation(url, auth)

    worker_check(url, auth, actor_id, int(args.workers_wanted))

    all_data = pd.DataFrame()
    for run_num in range(1, int(args.trials) + 1):
        msg_start = time.time()
        exec_id_list = executor(url, auth, actor_id, args)
        msg_time = time.time() - msg_start

        exec_start = time.time()
        results_list = results_get(url, auth, actor_id, exec_id_list)
        exec_time = time.time() - exec_start

        if args.data_get:
            data_capture(args, results_list, all_data,
                         run_num, msg_time, exec_time)
    all_data.to_csv('DATA/data.csv')


if __name__ == "__main__":
    main()
