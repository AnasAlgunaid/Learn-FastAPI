# core/dependencies.py
import redis

# Initialize the Redis client
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


# Function to return the Redis client
def get_redis_client():
    return redis_client
