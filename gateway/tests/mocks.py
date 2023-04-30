"""
Mocks for testing
"""
from datetime import timedelta

from adapters.redis_connector import RedisConnector, R


class FakeRedis(RedisConnector):

    def __init__(self, ping: bool = True, data: dict | None = None):
        self.ping_result = ping
        self.data = data or dict()

    async def close(self):
        pass

    async def ping(self) -> bool:
        return self.ping_result

    async def set(self, key: str, value: str) -> R:
        self.data[key] = value
        return "OK"

    async def get(self, key: str) -> str | None:
        return self.data.get(key, None)

    async def exists(self, key: str) -> bool:
        return key in self.data

    async def expire(self, key: str, time: int | timedelta) -> bool:
        return True

    async def delete(self, key: str):
        del self.data[key]

    async def incr(self, key: str) -> int:
        if key not in self.data:
            self.data[key] = 0
        self.data[key] += 1
        return self.data[key]


async def no_rate_limiter_middleware(request, redis):
    """
    Mock for rate_limiter_middleware
    """
    return request
