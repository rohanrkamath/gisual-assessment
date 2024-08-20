'''
I have used caching to keep track of the users location requests. If the same location is sent, there will be a cache hit,
and the user will be notified of it.
'''

import redis
import json
import os

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# kubernetes config

# REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
# REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
# REDIS_DB = int(os.getenv('REDIS_DB', 0))
# REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# # Initialize the Redis client
# redis_client = redis.Redis(
#     host=REDIS_HOST,
#     port=REDIS_PORT,
#     db=REDIS_DB,
#     password=REDIS_PASSWORD,
#     decode_responses=True
# )

# check content in cache
def get_cached_data(location_key: str):
    return redis_client.get(location_key)

# cache
def cache_response(location_key: str, response_message: str):
    redis_client.setex(location_key, 600, json.dumps(response_message.strip()))

# temp lock
def acquire_lock(location_key: str):
    return redis_client.setnx(location_key + '_lock', 'processing')

# release lock in redis
def release_lock(location_key: str):
    redis_client.delete(location_key + '_lock')