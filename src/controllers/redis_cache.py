import redis
import pickle
REDIS_URL="rediss://red-cucgbk3qf0us73cb954g:tP7yEM8hK01CfjLUYIXeTt9TFWgCvJ07@oregon-redis.render.com:6379"
redis_client = redis.StrictRedis.from_url(REDIS_URL)

def save_docs_to_redis(repo_link, documents):
    """Store serialized documents in Redis."""
    redis_client.set(repo_link, pickle.dumps(documents))
def load_docs_from_redis(repo_link):
    """Retrieve documents from Redis if available."""
    data = redis_client.get(repo_link)
    return pickle.loads(data) if data else None
def delete_docs_from_redis(repo_link):
    redis_client.delete(repo_link)
# delete_docs = delete_docs("https://github.com/NandithaHari6/dbms-project-backend")