# "Flop is floating operation. Hashing is integer operation"
# Have not linked blocks together
# could do class implementation but i imagine it's slower

from uuid import uuid4
import multiprocessing as mp
import copy, os, json, time, hashlib

MAX_NONCE = 2**32		# global max nonce; maximum attempts before failing to find next block

# creates random block
def randomBlock(bits=16):
	return {
			'prev_hash': None,
			'prev_nonce': None,
			'transactions': str(uuid4()), 
			'bits': bits, 
			'nonce': 0,
			}

# Helper function to hash a json object (our block)
def hashBlock(block):
	block_serialization = json.dumps(block, sort_keys=True).encode('utf-8')
	block_hash = hashlib.sha256(block_serialization).hexdigest()

	return block_hash

# Mines/hashes until the desired hash is found
def mineNextBlock(old_block):
	blockToMine = copy.deepcopy(old_block)
	blockToMine['nonce'] = 0
	bits = blockToMine['bits']	# pulls the bit value from the block
	target = 2 ** (256 - bits)	# target value (difficulty determined by bits)

	# attempts max_nonce times to find hash/int that's less than target
	for nonce in range(MAX_NONCE):
		hashy = hashBlock(blockToMine)

		if int(hashy, 16) < target:
			return {
				'prev_hash': hashy,
				'prev_nonce': blockToMine['nonce'],
				'transactions': str(uuid4()), 
				'bits': bits, 
				'nonce': 0,
			}

		blockToMine['nonce'] = blockToMine['nonce'] + 1

	print(f'Failed after {MAX_NONCE} (max_nonce) tries\n')
	return {
		'prev_hash': 'FAILED',
		'transactions': str(uuid4()), 
		'bits': bits,
		'nonce': max_nonce,
	}

if __name__ == '__main__':

	cores = os.cpu_count()
	in_bits = int(input('What difficulty in bits, bits={int, 0<bits<33}? '))
	print(f'\nMining {cores*100} {in_bits}-bit blocks on {cores} cores..')

	args = []
	for i in range(cores*100):
		args.append(randomBlock(bits=in_bits))

	start = time.time()
	nextBlocks = mp.Pool(processes=cores).map(mineNextBlock, args)
	end = time.time()

	nonce_count = 0
	for block in nextBlocks:
		nonce_count += block['prev_nonce']

	hashrate = nonce_count/(end-start)
	print('\tCores:\t\t', cores)
	print('\tRuntime:\t {:.4} seconds'.format(end-start))
	print('\tHashrate:\t {:.3e} hashes/second'.format(hashrate))






