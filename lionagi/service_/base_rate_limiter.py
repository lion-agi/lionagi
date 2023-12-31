from os import getenv
import asyncio
from typing import NoReturn
from ..utils.service_utils import RateLimiter

class BaseRateLimiter(RateLimiter):

    def __init__(
        self, 
        max_requests_per_interval: int, 
        max_tokens_per_interval: int,
        interval: int = 60,
    ) -> None:
        super().__init__(max_requests_per_interval, max_tokens_per_interval)
        self.interval = interval
        self.rate_limit_replenisher_task = asyncio.create_task(
            self.rate_limit_replenisher.create(max_requests_per_interval, 
                                               max_tokens_per_interval))

    @classmethod
    async def create(
        cls, max_requests_per_interval: int, max_tokens_per_interval: int
    ) -> None:
        self = cls(max_requests_per_interval, max_tokens_per_interval)
        if not getenv.getenv("env_readthedocs"):
            self.rate_limit_replenisher_task = await asyncio.create_task(
                self.rate_limit_replenisher()
            )
        return self

    async def rate_limit_replenisher(self) -> NoReturn:
        while True:
            await asyncio.sleep(self.interval)  # Replenishes every 60 seconds
            self.available_request_capacity = self.max_requests_per_interval
            self.available_token_capacity = self.max_tokens_per_interval
    
    def _is_busy(self):
        return self.available_request_capacity < 1 or self.available_token_capacity < 10
    
    def _has_capacity(self, required_tokens):
        return self.available_token_capacity >= required_tokens
    
    def _reduce_capacity(self, required_tokens):
        self.available_request_capacity -= 1
        self.available_token_capacity -= required_tokens
        