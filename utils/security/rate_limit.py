'''
security feature 2: rate limit. this will prevent the api from DOS attacks.
'''

from utils.cache.redis import redis_client
from fastapi import HTTPException
import os

# RATE_LIMIT = int(os.getenv("RATE_LIMT", 100)) # kubernetes config

RATE_LIMIT = 100  # Max requests per minute
RATE_LIMIT_KEY_PREFIX = "rate_limit:"

def check_rate_limit(client_ip: str):
    """Check and enforce rate limiting based on IP address."""
    key = f"{RATE_LIMIT_KEY_PREFIX}{client_ip}"
    current_count = redis_client.get(key)
    if current_count:
        if int(current_count) >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        redis_client.incr(key)
    else:
        redis_client.setex(key, 60, 1)