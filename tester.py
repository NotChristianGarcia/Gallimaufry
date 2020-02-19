import multiprocessing
from pymongo import MongoClient
client = MongoClient('localhost', 27017, readPreference='primary')

db = client.abaco
test_store = db['70']

def threaded_test(num):
    # Check for remaining uses greater than 0
    res = test_store.update_one(
        {'_id': 'tester', 'remaining_uses': {'$gt': 0}},
        {'$inc': {'current_uses': 1,
                  'remaining_uses': -1}})

def threaded_test(num):
    # Check for remaining uses greater than 0
    res = test_store.update_one(
        {'_id': 'tester', 'remaining_uses': {'$gt': 0}},
        {'$inc': {'current_uses': 1,
                  'remaining_uses': -1}})

if __name__ == "__main__":
    res = test_store.update_one(
        {'_id': 'tester'},
        {'$set': {'remaining_uses': 50001,
                  'current_uses': 0}},
        upsert=True)

    multiprocessing.freeze_support()
    pool=multiprocessing.Pool(processes=32)
    hey=pool.map(threaded_test, range(50000))
    print(test_store.find_one({'_id':'tester'}))
