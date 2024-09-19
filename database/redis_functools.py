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

    def set_model(self, key: str, model: Any, expiration: Optional[int] = None):
        """Set a scikit-learn model in Redis"""
        model_bytes = io.BytesIO()
        joblib.dump(model, model_bytes)
        model_bytes.seek(0)
        self.redis_client.set(key, model_bytes.getvalue(), ex=expiration)

    def get_model(self, key: str) -> Optional[Any]:
        """Get a scikit-learn model from Redis"""
        model_bytes = self.redis_client.get(key)
        if model_bytes:
            return joblib.load(io.BytesIO(model_bytes))
        return None

if __name__ == '__main__':
    redis_manager = RedisManager()
