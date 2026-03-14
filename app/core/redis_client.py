import redis
from app.core.config import settings
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

redis_client = None

try:
    if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
        logger.info(f"Connecting to Redis via URL")
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL, 
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True
        )
    else:
        logger.info(f"Connecting to Redis via host/port")
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=getattr(settings, 'REDIS_PASSWORD', None),
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True
        )

    redis_client.ping()
    logger.info("Redis connected successfully")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None 

class RedisCache:
    @staticmethod
    def set(key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration"""
        if redis_client is None:
            logger.debug("Redis not available, skipping set")
            return
        try:
            redis_client.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        if redis_client is None:
            logger.debug("Redis not available, skipping get")
            return None
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None
    
    @staticmethod
    def delete(key: str):
        if redis_client is None:
            return
        try:
            redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")