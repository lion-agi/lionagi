from typing import Callable, Mapping, Type

from lionagi.os.file.tokenize.token_calculator import BaseTokenCalculator
from .rate_limiter import RateLimiter


class EndPoint:
    """Represents an API endpoint with rate limiting capabilities.

    This class encapsulates the configuration and rate limiting logic
    for a specific API endpoint.

    Attributes:
        endpoint (str): The API endpoint path.
        endpoint_config (Mapping): Configuration for the endpoint.
        rate_limit_kwargs (dict): Arguments for rate limiter initialization.
        _has_initialized (bool): Flag indicating if rate limiter is initialized.
        rate_limiter (RateLimiter): The rate limiter instance for this endpoint.
    """

    def __init__(
        self,
        endpoint: str | None = None,
        endpoint_config: Mapping | None = None,
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        token_calculator: BaseTokenCalculator | Type | None = None,
        tokenizer: Callable | Type | None = None,
        **kwargs,
    ):
        """Initialize the EndPoint instance.

        Args:
            endpoint: The API endpoint path.
            endpoint_config: Configuration for the endpoint.
            interval: Time interval for rate limiting.
            interval_request: Maximum requests per interval.
            interval_token: Maximum tokens per interval.
            token_calculator: Calculator for token usage.
            tokenizer: Tokenizer function or type.
            **kwargs: Additional arguments for rate limiter initialization.
        """
        self.endpoint = endpoint or "chat/completions"
        self.endpoint_config = endpoint_config or {}
        self.rate_limit_kwargs = {
            "interval": interval,
            "interval_request": interval_request,
            "interval_token": interval_token,
            "token_calculator": token_calculator,
            "tokenizer": tokenizer,
            **kwargs,
        }
        self._has_initialized = False

    async def init_rate_limiter(self) -> None:
        """Initialize the rate limiter for the endpoint."""
        self.rate_limiter = await RateLimiter.create(**self.rate_limit_kwargs)
        self._has_initialized = True


# File: lionagi/os/service/api/endpoint.py
