from dataclasses import dataclass
import asyncio
from abc import ABC
from typing import Dict, NoReturn, Optional
import asyncio
import logging
import os

from ..utils import APIUtil as au


@dataclass
class StatusTracker:
    """Keeps track of various task statuses within a system.

    Attributes:
        num_tasks_started (int): The number of tasks that have been initiated.
        num_tasks_in_progress (int): The number of tasks currently being processed.
        num_tasks_succeeded (int): The number of tasks that have completed successfully.
        num_tasks_failed (int): The number of tasks that have failed.
        num_rate_limit_errors (int): The number of tasks that failed due to rate limiting.
        num_api_errors (int): The number of tasks that failed due to API errors.
        num_other_errors (int): The number of tasks that failed due to other errors.

    Examples:
        >>> tracker = StatusTracker()
        >>> tracker.num_tasks_started += 1
        >>> tracker.num_tasks_succeeded += 1
    """
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0


class BaseRateLimiter(ABC):
    """Abstract base class for rate limiting.

    This class provides an interface for rate limiting mechanisms. It should
    be subclassed to implement specific rate limiting logic.

    Attributes:
        max_requests_per_minute (int): Maximum number of requests allowed per minute.
        max_tokens_per_minute (int): Maximum number of tokens allowed per minute.

    Methods:
        rate_limit_replenisher: Abstract method to replenish rate limits.
        calculate_num_token: Abstract method to calculate required tokens for a request.
    """

    def __init__(
        self, max_requests: int, max_tokens: int, interval: int=60) -> None:
        self.interval = interval
        self.max_requests = max_requests
        self.max_tokens = max_tokens
        self.available_request_capacity = max_requests
        self.available_token_capacity = max_tokens
        self.rate_limit_replenisher_task: asyncio.Task = None

    async def rate_limit_replenisher(self) -> NoReturn:
        """Replenishes the rate limit capacities at regular intervals."""
        while True:
            await asyncio.sleep(self.interval)
            self.available_request_capacity = self.max_requests
            self.available_token_capacity = self.max_tokens

    async def _call_api(self, http_session, endpoint, base_url, api_key, max_attempts=3, method="post", payload: Dict[str, any] =None) -> Optional[Dict[str, any]]:
        endpoint = au.api_endpoint_from_url(f"https://{base_url}" + endpoint)
        
        while True:
            if self.available_request_capacity < 1 or self.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            
            required_tokens = au.calculate_num_token(payload, endpoint, self.token_encoding_name)
            
            if self.available_token_capacity >= required_tokens:
                self.available_request_capacity -= 1
                self.available_token_capacity -= required_tokens

                request_headers = {"Authorization": f"Bearer {api_key}"}
                attempts_left = max_attempts

                while attempts_left > 0:
                    try:
                        method = au.api_method(http_session, method)                         
                        async with method(
                            url=(base_url+endpoint), headers=request_headers, json=payload
                        ) as response:
                            response_json = await response.json()

                            if "error" in response_json:
                                logging.warning(
                                    f"API call failed with error: {response_json['error']}"
                                )
                                attempts_left -= 1

                                if "Rate limit" in response_json["error"].get("message", ""):
                                    await asyncio.sleep(15)
                            else:
                                return response_json
                    except Exception as e:
                        logging.warning(f"API call failed with exception: {e}")
                        attempts_left -= 1

                logging.error("API call failed after all attempts.")
                break
            else:
                await asyncio.sleep(1)

    @classmethod
    async def create(cls, max_requests_per_minute: int, max_tokens_per_minute: int) -> 'BaseRateLimiter':
        """Creates an instance of BaseAPIRateLimiter and starts the replenisher task."""
        instance = cls(max_requests_per_minute, max_tokens_per_minute)
        if not os.getenv("env_readthedocs"):
            instance.rate_limit_replenisher_task = asyncio.create_task(
                instance.rate_limit_replenisher()
            )
        return instance


class SimpleRateLimiter(BaseRateLimiter):

    def __init__(self, max_requests: int, max_tokens: int, interval: int=60) -> None:
        super().__init__(max_requests, max_tokens, interval)


class EndPoint:
    
    def __init__(self, max_requests=None, max_tokens=None, interval=None, endpoint_=None, rate_limiter_class=None, config=None) -> None:
        self.endpoint = endpoint_ or 'chat/completions'
        self.rate_limiter_class = rate_limiter_class or SimpleRateLimiter
        self.max_requests = max_requests or 1_000
        self.max_tokens = max_tokens or 100_000
        self.interval = interval or 60
        self.config=config
        self.rate_limiter = None

    async def _init(self):
        if self.rate_limiter is None:
            self.rate_limiter = await self.rate_limiter_class.create(self.max_requests, self.max_tokens_per_minute)
            