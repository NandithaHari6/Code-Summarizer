import redis
import json
import os

# Initialize Redis connection
REDIS_URL="rediss://red-cucgbk3qf0us73cb954g:tP7yEM8hK01CfjLUYIXeTt9TFWgCvJ07@oregon-redis.render.com:6379"
redis_client = redis.StrictRedis.from_url(REDIS_URL)

def store_to_cache(repo_link, ref_summary, gen_summary):
    """Store reference and generated summaries in Redis"""
    key = f"summary:{repo_link}"
    data = {"ref_summary": ref_summary, "gen_summary": gen_summary}
    redis_client.set(key, json.dumps(data))
    print(f"Stored summaries for {repo_link} in Redis.")

def load_from_cache(repo_link):
    """Load summaries from Redis cache"""
    key = f"summary:{repo_link}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def delete_from_cache(repo_link):
    """Delete summaries from Redis cache"""
    key = f"summary:{repo_link}"
    redis_client.delete(key)
    print(f"Deleted summaries for {repo_link} from Redis.")

def display_cache():
    """Display all stored summaries in Redis"""
    for key in redis_client.scan_iter("summary:*"):
        print(f"{key}: {redis_client.get(key)}")