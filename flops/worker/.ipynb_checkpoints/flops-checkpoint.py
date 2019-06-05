"""
Flop test for Abaco. Reads in a string message of "'std_deviation' 'size'" from
Abaco. Does some cool multi-threaded math and outputs total time to completion.
"""
import os
import time

threads, std_dev, size = map(int, os.environ.get('MSG').split())
#threads, std_dev, size = map(int, "3 10 3000".split())
os.environ["OMP_NUM_THREADS"] = str(threads)

import numpy

start = time.time()
A = numpy.random.normal(0, std_dev, (size, size))
B = numpy.random.normal(0, std_dev, (size, size))
C = numpy.dot(A, B)
r = numpy.linalg.eig(C)[0]
end = time.time()

print(end-start)
