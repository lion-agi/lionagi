from typing import Any, Dict, NoReturn, Optional, Type, List, Union
from .base_rate_limiter import BaseRateLimiter, SimpleRateLimiter


class BaseEndpoint:
    """
    Represents an API endpoint with rate limiting capabilities.

    This class encapsulates the details of an API endpoint, including its rate limiter.

    Attributes:
        endpoint (str): The API endpoint path.
        rate_limiter_class (Type[li.BaseRateLimiter]): The class used for rate limiting requests to the endpoint.
        max_requests (int): The maximum number of requests allowed per interval.
        max_tokens (int): The maximum number of tokens allowed per interval.
        interval (int): The time interval in seconds for replenishing rate limit capacities.
        config (Dict): Configuration parameters for the endpoint.
        rate_limiter (Optional[li.BaseRateLimiter]): The rate limiter instance for this endpoint.

    Examples:
        # Example usage of EndPoint with SimpleRateLimiter
        endpoint = EndPoint(
            max_requests=100,
            max_tokens=1000,
            interval=60,
            endpoint_='chat/completions',
            rate_limiter_class=li.SimpleRateLimiter,
            config={'param1': 'value1'}
        )
        asyncio.run(endpoint.init_rate_limiter())
    """

    def __init__(
        self,
        max_requests: int = 1_000,
        max_tokens: int = 100_000,
        interval: int = 60,
        endpoint_: Optional[str] = None,
        rate_limiter_class: Type[BaseRateLimiter] = SimpleRateLimiter,
        encode_kwargs=None,
        token_encoding_name=None,
        config: Dict = None,
    ) -> None:
        self.endpoint = endpoint_ or 'chat/completions'
        self.rate_limiter_class = rate_limiter_class
        self.max_requests = max_requests
        self.max_tokens = max_tokens
        self.interval = interval
        self.token_encoding_name = token_encoding_name
        self.config = config or {}
        self.rate_limiter: Optional[BaseRateLimiter] = None
        self._has_initialized = False
        self.encode_kwargs = encode_kwargs or {}

    async def init_rate_limiter(self) -> None:
        """Initializes the rate limiter for the endpoint."""
        self.rate_limiter = await self.rate_limiter_class.create(
            self.max_requests, self.max_tokens, self.interval, self.token_encoding_name
        )
        self._has_initialized = True


class Embedding(BaseEndpoint):
    ...
    