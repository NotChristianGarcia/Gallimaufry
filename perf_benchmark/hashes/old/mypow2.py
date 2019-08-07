# "Flop is floating operation. Hashing is integer operation"
# Have not linked blocks together
# could do class implementation but i imagine it's slower

from uuid import uuid4
import json, time, copy, hashlib, os

MAX_NONCE = 2**32       # global max nonce; maximum attempts before failing to find next block
                        # 32-bit system

# creates random block
def randomBlock(prev_hash=None, hashes=0, transactions=str(uuid4()), bits=10, nonce=0):
    return {
            'prev_hash': prev_hash,
            'hashes': hashes,
            'transactions': transactions, 
            'bits': bits, 
            'nonce': nonce,
            }


# Hashes a json object (our block)
def hashBlock(block):
    block_serialization = json.dumps(block, sort_keys=True).encode('utf-8')
    block_hash = hashlib.sha256(block_serialization).hexdigest()

    return block_hash


# Mines/hashes until the desired hash is found
def mineNextBlock(prev_block, start_nonce=0, end_nonce=MAX_NONCE):
    block_to_mine = copy.deepcopy(prev_block)
    block_to_mine['nonce'] = start_nonce        # initiates new start nonce
    bits = block_to_mine['bits']                # pulls the bit value from the block
    target = 2 ** (256 - bits)                  # target value (difficulty determined by bits)

    # attempts max_nonce times to find hash/int that's less than target
    for nonce in range(start_nonce, end_nonce):
        hashy = hashBlock(block_to_mine)

        if int(hashy, 16) < target:
            return randomBlock(prev_hash=hashy, hashes=block_to_mine['nonce'], bits=bits)

        block_to_mine['nonce'] = block_to_mine['nonce'] + 1

    print(f'Failed after {MAX_NONCE} (max_nonce) tries\n')
    return randomBlock(prev_hash='FAILED', bits=bits, nonce=MAX_NONCE)


if __name__ == '__main__':
    logs = {}
    logs['messages'] = f'Max Cores: {os.cpu_count()}'

    # intializes core count, bit difficulty, and blockchain length
    n_bits = int(input('What difficulty in bits? '))
    #n_bits = 24

    logs['messages'] = f' Mining a {n_bits}-bit block to the next block on 1 core..'

    # start the test
    start = time.time()

    next_block = mineNextBlock(randomBlock(bits=n_bits))

    end = time.time()
    hashrate = next_block['hashes']/(end-start)

    # writing logs
    logs['runtime'] = end-start
    logs['hashrate'] = hashrate
    logs['hashes'] = next_block['hashes']

    print(logs,end='')

