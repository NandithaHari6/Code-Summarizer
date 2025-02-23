import redis
import pickle
REDIS_URL="rediss://red-cucgbk3qf0us73cb954g:tP7yEM8hK01CfjLUYIXeTt9TFWgCvJ07@oregon-redis.render.com:6379"
redis_client = redis.StrictRedis.from_url(REDIS_URL)

def save_docs_to_redis(repo_link, documents, res):
    """Store both documents and results in Redis."""
    cache_data = {
        "documents": documents,
        "res": res
    }
    redis_client.setex(repo_link,3600, pickle.dumps(cache_data))  # Serialize and store

def load_docs_from_redis(repo_link):
    """Retrieve documents and results from Redis if available."""
    data = redis_client.get(repo_link)
    if data:
        return pickle.loads(data)  # Deserialize and return
    return None  # Return None if cache is empty
def delete_docs_from_redis(repo_link):
    redis_client.delete(repo_link)

# save_docs_to_redis("nandu",[1,2,3])
# store_res_to_redis("nandu",[4,5,6])
# print(load_docs_from_redis("https://github.com/NandithaHari6/dbms-project-backend"))
# delete_docs = delete_docs_from_redis("https://github.com/NandithaHari6/dbms-project-backend")