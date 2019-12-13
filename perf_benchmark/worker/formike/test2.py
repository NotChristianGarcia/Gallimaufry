import os
import time
os.environ["OMP_NUM_THREADS"] = "1"
import numpy

std_dev = 1000

size = 8000
whole_start = time.time()
A = numpy.random.normal(0, std_dev, (size, size))
B = numpy.random.normal(0, std_dev, (size, size))

calc_start = time.time()
C = numpy.dot(A, B)

end = time.time()

print("1 core - 8000: ", end - whole_start, end - calc_start)


size = 25000
whole_start = time.time()
A = numpy.random.normal(0, std_dev, (size, size))
B = numpy.random.normal(0, std_dev, (size, size))

calc_start = time.time()
C = numpy.dot(A, B)

end = time.time()

print("1 core - 25000: ", end - whole_start, end - calc_start)
