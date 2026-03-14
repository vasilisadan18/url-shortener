import redis
from app.core.config import settings
import json
from typing import Optional, Any

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

class RedisCache:
    @staticmethod
    def set(key: str, value: Any, expire: int = 3600):
        redis_client.setex(key, expire, json.dumps(value))
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        value= redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    @staticmethod
    def delete(key: str):
        redis_client.delete(key)
    
    @staticmethod
    def delete_pattern(pattern: str):
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)