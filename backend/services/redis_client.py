import os
import redis


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def ping_redis() -> bool:
    try:
        return bool(redis_client.ping())
    except Exception:
        return False

