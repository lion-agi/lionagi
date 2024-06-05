from abc import ABC
import asyncio
from typing import Mapping
import logging

from .util import api_endpoint_from_url, api_method
from lionagi.os.operations.files.tokenize.token_calculator import calculate_num_token
from .util import AsyncUtil


class BaseRateLimiter(ABC):
    """
    Abstract base class for implementing rate limiters.

    This class provides the basic structure for rate limiters, including
    the replenishment of request and token capacities at regular intervals.

    Attributes:
            interval: The time interval in seconds for replenishing capacities.
            max_requests: The maximum number of requests allowed per interval.
            max_tokens: The maximum number of tokens allowed per interval.
            available_request_capacity: The current available request capacity.
            available_token_capacity: The current available token capacity.
            rate_limit_replenisher_task: The asyncio task for replenishing capacities.
    """

    def __init__(
        self,
        max_requests: int,
        max_tokens: int,
        interval: int = 60,
        token_encoding_name=None,
    ) -> None:
        self.interval: int = interval
        self.max_requests: int = max_requests
        self.max_tokens: int = max_tokens
        self.available_request_capacity: int = max_requests
        self.available_token_capacity: int = max_tokens
        self.rate_limit_replenisher_task: AsyncUtil.Task | None = None
        self._stop_replenishing: AsyncUtil.Event = AsyncUtil.create_event()
        self._lock: AsyncUtil.Lock = AsyncUtil.create_lock()
        self.token_encoding_name = token_encoding_name

    async def start_replenishing(self):
        """Starts the replenishment of rate limit capacities at regular intervals."""
        try:
            while not self._stop_replenishing.is_set():
                await AsyncUtil.sleep(self.interval)
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
            if (
                self.available_request_capacity > 0
                and self.available_token_capacity > 0
            ):
                self.available_request_capacity -= 1
                self.available_token_capacity -= (
                    required_tokens
                    # Assuming 1 token per request for simplicity
                )
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
        payload: Mapping[str, any] = None,
        required_tokens: int = None,
        **kwargs,
    ) -> Mapping[str, any] | None:
        """
        Makes an API call to the specified endpoint using the provided HTTP session.

        Args:
                http_session: The aiohttp client session to use for the API call.
                endpoint: The API endpoint to call.
                base_url: The base URL of the API.
                api_key: The API key for authentication.
                max_attempts: The maximum number of attempts for the API call.
                method: The HTTP method to use for the API call.
                payload: The payload to send with the API call.

        Returns:
                The JSON assistant_response from the API call if successful, otherwise None.
        """
        endpoint = api_endpoint_from_url(base_url + endpoint)
        while True:
            if (
                self.available_request_capacity < 1
                or self.available_token_capacity < 10
            ):  # Minimum token count
                await AsyncUtil.sleep(1)  # Wait for capacity
                continue

            if not required_tokens:
                required_tokens = calculate_num_token(
                    payload, endpoint, self.token_encoding_name, **kwargs
                )

            if await self.request_permission(required_tokens):
                request_headers = {"Authorization": f"Bearer {api_key}"}
                attempts_left = max_attempts

                while attempts_left > 0:
                    try:
                        method = api_method(http_session, method)
                        async with method(
                            url=(base_url + endpoint),
                            headers=request_headers,
                            json=payload,
                        ) as response:
                            response_json = await response.json()

                            if "error" not in response_json:
                                return response_json
                            logging.warning(
                                f"API call failed with error: {response_json['error']}"
                            )
                            attempts_left -= 1

                            if "Rate limit" in response_json["error"].get(
                                "message", ""
                            ):
                                await asyncio.sleep(15)
                    except Exception as e:
                        logging.warning(f"API call failed with exception: {e}")
                        attempts_left -= 1

                logging.error("API call failed after all attempts.")
                break
            else:
                await AsyncUtil.sleep(1)

    @classmethod
    async def create(
        cls,
        max_requests: int,
        max_tokens: int,
        interval: int = 60,
        token_encoding_name=None,
    ) -> "BaseRateLimiter":
        """
        Creates an instance of BaseRateLimiter and starts the replenisher task.

        Args:
                max_requests: The maximum number of requests allowed per interval.
                max_tokens: The maximum number of tokens allowed per interval.
                interval: The time interval in seconds for replenishing capacities.
                token_encoding_name: The name of the token encoding to use.

        Returns:
                An instance of BaseRateLimiter with the replenisher task started.
        """
        instance = cls(max_requests, max_tokens, interval, token_encoding_name)
        instance.rate_limit_replenisher_task = AsyncUtil.create_task(
            instance.start_replenishing(), obj=False
        )
        return instance


class SimpleRateLimiter(BaseRateLimiter):
    """
    A simple implementation of a rate limiter.

    Inherits from BaseRateLimiter and provides a basic rate limiting mechanism.
    """

    def __init__(
        self,
        max_requests: int,
        max_tokens: int,
        interval: int = 60,
        token_encoding_name=None,
    ) -> None:
        """Initializes the SimpleRateLimiter with the specified parameters."""
        super().__init__(max_requests, max_tokens, interval, token_encoding_name)
