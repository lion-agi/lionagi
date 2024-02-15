import asyncio
import logging
from abc import ABC
from typing import Dict, NoReturn, Optional

from ..utils import APIUtil


class BaseRateLimiter(ABC):
    def __init__(self, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None:
        self.interval: int = interval
        self.max_requests: int = max_requests
        self.max_tokens: int = max_tokens
        self.available_request_capacity: int = max_requests
        self.available_token_capacity: int = max_tokens
        self.rate_limit_replenisher_task: Optional[asyncio.Task[NoReturn]] = None
        self._stop_replenishing: asyncio.Event = asyncio.Event()
        self._lock: asyncio.Lock = asyncio.Lock()
        self.token_encoding_name = token_encoding_name

    async def start_replenishing(self) -> NoReturn:
        """Starts the replenishment of rate limit capacities at regular intervals."""
        try:
            while not self._stop_replenishing.is_set():
                await asyncio.sleep(self.interval)
                async with self._lock:
                    self.available_request_capacity = self.max_requests
                    self.available_token_capacity = self.max_tokens
        except asyncio.CancelledError:
            logging.info("Rate limit replenisher task cancelled.")

        except Exception as e:
            logging.error(f"An error occurred in the rate limit replenisher: {e}")

    async def stop_replenishing(self) -> None:
        """Stops the replenishment task."""
        if self.rate_limit_replenisher_task:
            self.rate_limit_replenisher_task.cancel()
            await self.rate_limit_replenisher_task
        self._stop_replenishing.set()

    async def request_permission(self, required_tokens) -> bool:
        """Requests permission to make an API call.

        Returns True if the request can be made immediately, otherwise False.
        """
        async with self._lock:
            if self.available_request_capacity > 0 and self.available_token_capacity > 0:
                self.available_request_capacity -= 1
                self.available_token_capacity -= required_tokens  # Assuming 1 token per request for simplicity
                return True
            return False

    async def _call_api(
        self, 
        http_session, 
        endpoint: str, 
        base_url: str, 
        api_key: str,
        max_attempts: int = 3, 
        method: str = "post", 
        payload: Dict[str, any]=None, 
        **kwargs,
    ) -> Optional[Dict[str, any]]:
        endpoint = APIUtil.api_endpoint_from_url(base_url + endpoint)
        while True:
            if self.available_request_capacity < 1 or self.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            required_tokens = APIUtil.calculate_num_token(payload, endpoint, self.token_encoding_name, **kwargs)
            
            if await self.request_permission(required_tokens):
                request_headers = {"Authorization": f"Bearer {api_key}"}
                attempts_left = max_attempts

                while attempts_left > 0:
                    try:
                        method = APIUtil.api_method(http_session, method)                         
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
    async def create(cls, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name = None) -> 'BaseRateLimiter':
        instance = cls(max_requests, max_tokens, interval, token_encoding_name)
        instance.rate_limit_replenisher_task = asyncio.create_task(
            instance.start_replenishing()
        )
        return instance


class SimpleRateLimiter(BaseRateLimiter):
    """
    A simple implementation of a rate limiter.

    Inherits from BaseRateLimiter and provides a basic rate limiting mechanism.
    """

    def __init__(self, max_requests: int, max_tokens: int, interval: int = 60, token_encoding_name=None) -> None:
        """Initializes the SimpleRateLimiter with the specified parameters."""
        super().__init__(max_requests, max_tokens, interval, token_encoding_name)
