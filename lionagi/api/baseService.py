import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class StatusTracker:
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    

class RateLimiter(ABC):
    def __init__(self, max_requests_per_minute: int, max_tokens_per_minute: int):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
        self.rate_limit_replenisher_task = asyncio.create_task(self.rate_limit_replenisher())

    @abstractmethod
    async def rate_limit_replenisher(self):
        pass
  
  
class BaseAPIService(ABC):
    def __init__(self, rate_limiter: RateLimiter, api_key: str, token_encoding_name: str, max_attempts: int, status_tracker: StatusTracker):
        self.rate_limiter = rate_limiter
        self.api_key = api_key
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.status_tracker = status_tracker

    @abstractmethod
    async def call_api_endpoint(self, endpoint:str, **kwargs):
        pass