import io
import os

import joblib
import redis
import json
from typing import Any, Optional

from dotenv import load_dotenv

load_dotenv()


class RedisManager:
    def __init__(self):
        self.host = os.getenv('REDIS_HOST')
        self.port = os.getenv('REDIS_PORT')
        self.db = os.getenv('REDIS_DB')
        self.redis_client = redis.Redis(host=self.host, port=self.port, db=self.db)

    def health_check(self) -> bool:
        """Perform a health check on the Redis connection"""
        try:
            return self.redis_client.ping()
        except redis.ConnectionError:
            return False

    def set(self, key: str, value: Any, expiration: Optional[int] = None):
        """Set a key-value pair in Redis"""
        serialized_value = json.dumps(value)
        self.redis_client.set(key, serialized_value, ex=expiration)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis by key"""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    def delete(self, key: str):
        """Delete a key from Redis"""
        self.redis_client.delete(key)

    def set_serializable_object(self, key: str, obj: Any, expiration: Optional[int] = None):
        """Set a serializable object in Redis"""
        obj_bytes = io.BytesIO()
        joblib.dump(obj, obj_bytes)
        obj_bytes.seek(0)
        self.redis_client.set(key, obj_bytes.getvalue(), ex=expiration)

    def get_serializable_object(self, key: str) -> Any:
        """Get a serializable object from Redis"""
        obj_bytes = self.redis_client.get(key)
        if obj_bytes is None:
            return None
        return joblib.load(io.BytesIO(obj_bytes))

if __name__ == '__main__':
    redis_manager = RedisManager()
