"""
Testing flops 24/7/365.
"""
import os
import time
import argparse
import pprint as pp
import requests as r

def main():
    jwt = os.environ.get('jwt')

    parser = argparse.ArgumentParser(
        description="Takes threads, standard deviation, matrix size, and" +
        "number of executions and executes an Abaco instance to determine flops")
    parser.add_argument('threads', help="Amount of max threads to use")
    parser.add_argument('standard_deviation', help="Standard deviation for math")
    parser.add_argument('size', help="Size of square matrix")
    parser.add_argument('executions', help="Amount of executions to do")
    args = parser.parse_args()

    threads = int(args.threads)
    std_dev = int(args.standard_deviation)
    size = int(args.size)
    executions = int(args.executions)

    #threads = int(input('Threads?: '))
    #std_dev = int(input('Standard Deviation?: '))
    #size = int(input('Size of matrices?: '))
    #executions = int(input('Number of executions: '))

    # message = "'std_deviation' 'size'"
    message_dat = f'{threads} {std_dev} {size}'

    # local
    header_dat = {'X-Jwt-Assertion-TEST':jwt}
    # online
    #header_dat={'Authorization': f'Bearer {token}'}

    url = "http://localhost:8000"

    # Actor that will be creating workers with flop test.
    actor = r.post(f"{url}/actors",
                   headers=header_dat,
                   data={'image':'notchristiangarcia/flops_test:3.0'})
    actor_id = actor.json()['result']['id']

    start = time.time()

    # Executions of this actor, lots of times.
    exec_id_list = []
    for _ in range(executions):
        execution = r.post(f"{url}/actors/{actor_id}/messages",
                           headers=header_dat,
                           data={'message': message_dat})
        exec_id = execution.json()['result']['executionId']
        exec_id_list.append(exec_id)


    # Getting result of exec from log once exec complete.
    results_dict = {}
    while exec_id_list:
        for exec_id in exec_id_list:
            exec_logs = r.get(f"{url}/actors/{actor_id}/executions/{exec_id}/logs",
                              headers=header_dat)

            logs = exec_logs.json()['result']['logs']
            if logs:
                print("...")
                results_dict[f'id - {exec_id}'] = float(logs.replace('\n', ''))
                exec_id_list.remove(exec_id)
    end = time.time()

    print(f"\nTotal time {end-start}")
    pp.pprint(results_dict)

if __name__ == "__main__":
    main()
