import redis
import json

import os

# Initialize Redis connection
REDIS_URL="rediss://red-cucgbk3qf0us73cb954g:tP7yEM8hK01CfjLUYIXeTt9TFWgCvJ07@oregon-redis.render.com:6379"
redis_client = redis.StrictRedis.from_url(REDIS_URL)
def save_file_structure_to_redis(repo_link, structure):
    """Store both documents and results in Redis."""

    redis_client.setex(repo_link+"file_structure",3600, json.dumps({"file_structure":structure})) 
def load_file_structure_from_redis(repo_link):
    """Retrieve documents and results from Redis if available."""
    data = redis_client.get(repo_link+"file_structure")
    if data:
        return json.loads(data)  # Deserialize and return
    return None  # Return None if cache is empty
def load_docs_from_redis(repo_link):
    """Retrieve cached results for the given repo_link."""
    cached_data = redis_client.get(repo_link)
    if cached_data:
        return json.loads(cached_data)
    return None

def save_docs_to_redis(repo_link, cached_res, completed=False):
    """Store results along with completion flag in Redis."""
    redis_client.setex(repo_link,3600, json.dumps({"res": cached_res, "completed": completed}))
def delete_docs_from_redis(repo_link):
    redis_client.delete(repo_link)
def display_redis_keys():
    keys = redis_client.keys("*")  # Retrieve all keys
    if keys:
        print("Keys in Redis Cache:")
        for key in keys:
            print(key)
    else:
        print("No keys found in Redis.")
def display_value(key):
    value=redis_client.get(key)
    if value:
        print(value)
    else:
        print("No value associated with the key")

# Call the function to display keys

# save_docs_to_redis("nandu",[1,2,3])
# store_res_to_redis("nandu",[4,5,6])
# print(load_docs_from_redis("https://github.com/NandithaHari6/dbms-project-backend"))
# delete_docs = delete_docs_from_redis("https://github.com/deepankarvarma/To-Do-List-Using-Python")
# delete_docs = delete_docs_from_redis("https://github.com/adityasurya4103/Clinic-Hospital-Management-System-")
# delete_docs = delete_docs_from_redis("nandu")
# delete_docs = delete_docs_from_redis("number")
# display_redis_keys()