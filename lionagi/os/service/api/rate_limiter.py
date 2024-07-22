import asyncio
from abc import ABC
from typing import Any, Callable, Mapping, NoReturn, Type

import aiohttp
from aiocache import cached

from lionagi import logging
from lion_core import LN_UNDEFINED
from lionagi.os.file.tokenize.token_calculator import BaseTokenCalculator
from .utils import api_endpoint_from_url
from .api_call import call_api
from .config import DEFAULT_RATE_LIMIT_CONFIG, CACHED_CONFIG, RETRY_CONFIG


# Note the following was inspired by the OpenAI cookbook, MIT License:
# https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py
class RateLimiter(ABC):
    """Rate limiter for API calls with token-based and request-based limiting.

    Controls API call rates based on request count and token usage within
    specified intervals. Includes features for API call caching and token
    calculation.

    Attributes:
        interval (int): Time interval for replenishing capacities.
        interval_request (int): Maximum requests per interval.
        interval_token (int): Maximum tokens per interval.
        token_calculator (BaseTokenCalculator): Calculator for token usage.
        _rate_limit_replenisher_task (asyncio.Task | None): Replenish task.
        _stop_replenishing (asyncio.Event): Signal to stop replenishment.
        _lock (asyncio.Lock): Lock for thread-safe operations.
    """

    def __init__(
        self,
        interval: int,
        interval_request: int,
        interval_token: int,
        token_calculator: BaseTokenCalculator | Type,
        tokenizer: Callable | Type,
        **kwargs,
    ):
        """Initialize the RateLimiter.

        Args:
            interval: Time interval for replenishing capacities.
            interval_request: Maximum requests per interval.
            interval_token: Maximum tokens per interval.
            token_calculator: Calculator or type for token usage.
            tokenizer: Tokenizer function or type.
            **kwargs: Additional arguments for tokenizer initialization.
        """
        self.interval = interval or DEFAULT_RATE_LIMIT_CONFIG["interval"]
        self.interval_request = (
            interval_request or DEFAULT_RATE_LIMIT_CONFIG["interval_request"]
        )
        self.interval_token = (
            interval_token or DEFAULT_RATE_LIMIT_CONFIG["interval_token"]
        )
        self.token_calculator = self._init_token_calculator(
            token_calculator, tokenizer, **kwargs
        )
        self._rate_limit_replenisher_task: asyncio.Task | None = None
        self._stop_replenishing: asyncio.Event = asyncio.Event()
        self._lock: asyncio.Lock = asyncio.Lock()

    def _init_token_calculator(
        self,
        token_calculator: BaseTokenCalculator | Type,
        tokenizer: Callable | Type,
        **kwargs,
    ) -> BaseTokenCalculator:
        """Initialize the token calculator.

        Args:
            token_calculator: Calculator or type for token usage.
            tokenizer: Tokenizer function or type.
            **kwargs: Additional arguments for tokenizer initialization.

        Returns:
            Initialized BaseTokenCalculator instance.
        """
        if isinstance(token_calculator, type):
            return token_calculator(tokenizer, **kwargs)
        if tokenizer:
            token_calculator.update_tokenizer(tokenizer, **kwargs)
        return token_calculator

    async def start_replenishing(self) -> NoReturn:
        """Start replenishing rate limit capacities at regular intervals."""
        try:
            while not self._stop_replenishing.is_set():
                await asyncio.sleep(self.interval)
                async with self._lock:
                    self.available_request_capacity = self.max_requests
                    self.available_token_capacity = self.max_tokens
        except asyncio.CancelledError:
            logging.info("Rate limit replenisher task cancelled.")
        except Exception as e:
            logging.error(f"Error in rate limit replenisher: {e}")

    async def stop_replenishing(self) -> None:
        """Stop the replenishment task."""
        if self._rate_limit_replenisher_task:
            self._rate_limit_replenisher_task.cancel()
            await self._rate_limit_replenisher_task
        self._stop_replenishing.set()

    async def request_permission(self, required_tokens: int) -> bool:
        """Request permission to make an API call.

        Args:
            required_tokens: Number of tokens required for the call.

        Returns:
            True if the request can be made immediately, otherwise False.
        """
        async with self._lock:
            if (
                self.available_request_capacity > 0
                and self.available_token_capacity > 0
            ):
                self.available_request_capacity -= 1
                self.available_token_capacity -= required_tokens
                return True
            return False

    async def call_api(
        self,
        *,
        http_session: aiohttp.ClientSession,
        api_key: str,
        endpoint: str,
        base_url: str,
        method: str = "post",
        retries: int | None = None,
        initial_delay: float | None = None,
        delay: float | None = None,
        backoff_factor: float | None = None,
        default: Any = LN_UNDEFINED,
        timeout: float | None = None,
        verbose: bool = True,
        error_msg: str | None = None,
        error_map: dict[type, Callable[[Exception], Any]] | None = None,
        payload: Mapping[str, Any] | None = None,
        required_tokens: int | None = None,
        **kwargs,
    ) -> dict:
        """Make a rate-limited API call.

        Args:
            http_session: The aiohttp client session.
            api_key: API key for authentication.
            endpoint: API endpoint.
            base_url: Base URL for the API.
            method: HTTP method (default: "post").
            retries: Number of retries for failed calls.
            initial_delay: Initial delay before first retry.
            delay: Delay between retries.
            backoff_factor: Factor to increase delay between retries.
            default: Default value to return on failure.
            timeout: Timeout for the API call.
            verbose: Whether to log verbose output.
            error_msg: Custom error message for failures.
            error_map: Mapping of exception types to handler functions.
            payload: Request payload.
            required_tokens: Number of tokens required for the call.
            **kwargs: Additional arguments for token calculation.

        Returns:
            The API response or the default value on failure.
        """
        endpoint = api_endpoint_from_url(base_url + endpoint)
        while True:
            if (
                self.available_request_capacity < 1
                or self.available_token_capacity < 10
            ):
                await asyncio.sleep(1)  # Wait for capacity
                continue

            if not required_tokens:
                required_tokens = self.token_calculator.calculate_token(
                    payload, endpoint, **kwargs
                )

            if await self.request_permission(required_tokens):
                try:
                    return await call_api(
                        http_session=http_session,
                        url=(base_url + endpoint),
                        method=method,
                        retries=retries or RETRY_CONFIG["retries"],
                        initial_delay=initial_delay or RETRY_CONFIG["initial_delay"],
                        delay=delay or RETRY_CONFIG["delay"],
                        backoff_factor=backoff_factor or RETRY_CONFIG["backoff_factor"],
                        default=default or RETRY_CONFIG["default"],
                        timeout=timeout or RETRY_CONFIG["timeout"],
                        verbose=verbose or RETRY_CONFIG["verbose"],
                        error_msg=error_msg or RETRY_CONFIG["error_msg"],
                        error_map=error_map or RETRY_CONFIG["error_map"],
                        json=payload,
                        headers={"Authorization": f"Bearer {api_key}"},
                    )
                except Exception as e:
                    logging.error(f"API call failed after all attempts: {e}")
            else:
                await asyncio.sleep(1)

    @cached(**CACHED_CONFIG)
    async def cached_call_api(
        self,
        *,
        http_session: aiohttp.ClientSession,
        api_key: str,
        endpoint: str,
        base_url: str,
        method: str = "post",
        retries: int | None = None,
        initial_delay: float | None = None,
        delay: float | None = None,
        backoff_factor: float | None = None,
        default: Any = LN_UNDEFINED,
        timeout: float | None = None,
        verbose: bool = True,
        error_msg: str | None = None,
        error_map: dict[type, Callable[[Exception], Any]] | None = None,
        payload: Mapping[str, Any] | None = None,
        required_tokens: int | None = None,
        **kwargs,
    ) -> dict:
        """Make a cached, rate-limited API call.

        This method wraps call_api with caching functionality.

        Args and Returns:
            See call_api method for details.
        """
        return await self.call_api(
            http_session=http_session,
            api_key=api_key,
            endpoint=endpoint,
            base_url=base_url,
            method=method,
            retries=retries,
            initial_delay=initial_delay,
            delay=delay,
            backoff_factor=backoff_factor,
            default=default,
            timeout=timeout,
            verbose=verbose,
            error_msg=error_msg,
            error_map=error_map,
            payload=payload,
            required_tokens=required_tokens,
            **kwargs,
        )

    @classmethod
    async def create(
        cls,
        interval: int,
        interval_request: int,
        interval_token: int,
        token_calculator: BaseTokenCalculator | Type,
        tokenizer: Callable | Type,
        **kwargs,
    ) -> "RateLimiter":
        """Create a RateLimiter instance and start the replenisher task.

        Args:
            interval: Time interval for replenishing capacities.
            interval_request: Maximum requests per interval.
            interval_token: Maximum tokens per interval.
            token_calculator: Calculator or type for token usage.
            tokenizer: Tokenizer function or type.
            **kwargs: Additional arguments for tokenizer initialization.

        Returns:
            An instance of RateLimiter with the replenisher task started.
        """
        self = cls(
            interval=interval,
            interval_request=interval_request,
            interval_token=interval_token,
            token_calculator=token_calculator,
            tokenizer=tokenizer,
            **kwargs,
        )
        self._rate_limit_replenisher_task = asyncio.create_task(
            self.start_replenishing()
        )
        return self


# File: lionagi/os/service/api/rate_limiter.py
