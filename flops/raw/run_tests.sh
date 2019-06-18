#!/bin/bash

echo "What's the actor_id? "
read actor_id_inp

echo "How many nodes? "
read nodes

export actor_id=$actor_id_inp
export nodes=$nodes

python3 flop_tester_1.py
python3 worker_burn.py
python3 flop_tester_6.py
