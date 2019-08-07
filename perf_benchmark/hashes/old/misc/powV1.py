
# "Flop is floating operation. Hashing is integer operation"
# Have not linked blocks together
# could do class implementation but i imagine it's slower

from hashlib import sha256, sha1
from uuid import uuid4
import matplotlib.pyplot as plt
import multiprocessing as mp
import numpy as np
import json, time

# Helper function to hash a json object (our block)
def hashBlock(block):
	block_serialization = json.dumps(block, sort_keys=True).encode('utf-8')
	block_hash = sha256(block_serialization).hexdigest()

	return block_hash

# Mines/hashes until the desired hash is found
# Actually alters the old block which is probably bad but may be desired
def mineNextBlock(old_block):
	bits = old_block['bits']	# pulls the bit value from the block
	max_nonce = 2 ** 32			# maximum attempts before failing to find next block
	target = 2 ** (256 - bits)	# target value (difficulty determined by bits)
	old_block['nonce'] = 0		# sets nonce to 0 to restart mining

	# attempts max_nonce times to find hash/int that's less than target
	for nonce in range(max_nonce):
		hashy = hashBlock(old_block)

		if int(hashy, 16) < target:
			return {
				'prev_hash': hashy, 
				'transactions': str(uuid4()), 
				'bits': bits, 
				'nonce': 0,
			}

		old_block['nonce'] = old_block['nonce'] + 1

	print("Failed after %d (max_nonce) tries\n" % max_nonce)
	return {
		'prev_hash': 'FAILED', 
		'transactions': str(uuid4()), 
		'bits': bits, 
		'nonce': max_nonce,
	}

# Creates a new block and attempts to find the next block for N trials
# Returns list of each trial time and a total test time
def testTime(N=1000, bits=16, cores=1):
	trial_times = []

	print('Testing with N=%d, bit=%d...' % (N,bits))
	start_test_time = time.time()			# starts total test time
	for trial in range(N):
		block = {							# creates unique new block/test if this takes non-negligible time
			'prev_hash': None, 
			'transactions': str(uuid4()), 
			'bits': bits, 
			'nonce': 0,
		}

		start_trial_time = time.time()		# start trial time
		mineNextBlock(block)				# mines block
		end_trial_time = time.time()		# end trial time

		trial_time = end_trial_time-start_trial_time
		trial_times.append(trial_time)
	end_test_time = time.time()				# ends total test time

	total_time = end_test_time-start_test_time

	print('Test Finished.\n')
	return trial_times, total_time

# Plots according to list of trial times and total test time
def showResults(trial_times, total_time, plot=True):
	print('Results:')
	print('\tAverage Time (s):', np.mean(trial_times))
	print('\tRange of Times: {:.3e}s to {:.3e}s'.format(min(trial_times), max(trial_times)))
	print('\tVariance (s):', np.var(trial_times))
	print('\tTotal Test Time (s):', total_time)

	if plot:
		plt.plot(list(range(len(trial_times))), trial_times)
		plt.title('Time for Each Mine')
		plt.xlabel('Trial (N)')
		plt.ylabel('Time (s)')
		plt.show()

# Runs bit test until a test takes longer than one minute
def testOneMin():
	for i in range(32):
		one_min = time.time() + 60
		testTime(N=1, bits=i)
		if time.time() > one_min:
			print('Max Bits/min:', i)
			break

def main():
	# test time to mine blocks
	input_n = int(input('What sample size, N={int, n>0}? '))
	input_bits = int(input('What difficulty in bits, bits={int, 0<bits<33}? '))

	trial, total = testTime(N=input_n, bits=input_bits)
	#trial, total = testTime(N=1000, bits=12)
	showResults(trial, total, plot=False)

	# test time until it takes longer than a minute
	#testOneMin()


	''' Future work for block linking
	genesis_block = {
		'prev_hash': None,
		'transactions': 123, 	# will just be some random uuid until later (transactions to be added)
		'bits': 8,
		'nonce': 0,
		}
	'''

if __name__ == '__main__':
	main()






