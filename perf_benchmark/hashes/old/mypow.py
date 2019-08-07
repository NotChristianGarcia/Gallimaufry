# "Flop is floating operation. Hashing is integer operation"
# Have not linked blocks together
# could do class implementation but i imagine it's slower

from uuid import uuid4
import multiprocessing as mp
import json, time, copy, hashlib, os, math

MAX_NONCE = 2**32       # global max nonce; maximum attempts before failing to find next block
                        # 32-bit system

# creates random block
def randomBlock(prev_hash=None, hashes=0, transactions=str(uuid4()), bits=16, nonce=0):
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
            print(f"Succeeded on the {block_to_mine['nonce']-start_nonce}th hash with the block that mined from nonce {start_nonce} to {end_nonce}")
            return [randomBlock(prev_hash=hashy, hashes=block_to_mine['nonce']-start_nonce, bits=bits), 
                    block_to_mine['nonce']]

        block_to_mine['nonce'] = block_to_mine['nonce'] + 1

    # if a process fails within its chunk range, it'll sleep until another process succeeds
    while True:
        time.sleep(10)


# helper function for parallel work
def helper(prev_block, start_nonce, end_nonce, blocks_q, event):
    blocks_q.put(mineNextBlock(prev_block, start_nonce, end_nonce))
    event.set()


# splits block mining into parallel tasks that work on a specific chunk
def parallel(prev_block, cores):

    chunksize = math.ceil(MAX_NONCE / float(cores))
    blocks_q = mp.SimpleQueue()
    processes = []
    event = mp.Event()

    # builds and starts processes
    for i in range(cores):
        worker = mp.Process(target=helper, args=(prev_block, i*chunksize, (i+1)*chunksize, blocks_q, event))
        processes.append(worker)
        worker.start()

    # end all processes once first one finishes; returns the result from first core to finish
    while True:
        if event.is_set():
            for p in processes:
                p.terminate()
            # waits for all processes to end before moving on
            for p in processes:
                while p.is_alive():
                    pass
            return blocks_q.get()
        # lowers overhead from main process checking for event
        else:
            time.sleep(.001)
        # add a timeout

    # add a hashrate finder

    return 'FAILED'


# validates that the chain is correct
def verifyChain(blockchain=None):

    print('\nVerifying Blockchain..')
    for i in range(0,len(blockchain)-1):
        assert int(hashBlock(blockchain[i]), 16) < (2 ** (256-blockchain[i]['bits']))
        assert hashBlock(blockchain[i]) == blockchain[i+1]['prev_hash']

        print(f'Block #{i+1} is correct.')
        time.sleep(0.25)


if __name__ == '__main__':

    # intializes core count, bit difficulty, and blockchain length
    cores = int(input(f'\nHow many cores to work("max" is {os.cpu_count()})? '))
    n_bits = int(input('What difficulty in bits? '))
    n_blocks = int(input('How many blocks to mine (length of chain)? '))
    print(f'\nMining {n_bits}-bit blocks out to the {n_blocks}th block on {cores} core(s)..')

    # initializes chain with genesis_block
    chain = [randomBlock(bits=n_bits)]
    hashes = 0

    # start the test
    start = time.time()

    for i in range(n_blocks):
        print(f'\n{i+1}th Block Mine..')

        result = parallel(chain[i], cores)

        chain.append(result[0])         # adds new block to chain
        chain[i]['nonce'] = result[1]   # changes block nonce to match the found nonce
        hashes += chain[i-1]['hashes']*cores    # utilizes winning cores hashes to determine hashrate

    end = time.time()

    print(f'\nRuntime: {end-start:.4}s')
    print(f'Hashrate: {hashes/(end-start):.3e}hash/s')
    print(f'Hashes: {hashes} hashes')

    # Verifies that the blockchain is valid
    #chain[4] = randomBlock()       # use to break chain
    verifyChain(chain)






