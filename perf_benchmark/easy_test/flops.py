"""
Flop test for Abaco. Reads in a string message of "'std_deviation' 'size'" from
Abaco. Does some cool multi-threaded math and outputs total time to completion.
"""
import os
import time

WAIT=int(os.environ.get('WAIT'))

whole_start = time.time()
calc_start = time.time()
time.sleep(WAIT)
end = time.time()

print(end - whole_start, end - calc_start)
