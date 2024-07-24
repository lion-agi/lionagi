from typing import Callable, Type, Any

from lionagi.os.file.tokenize.token_calculator import TokenCalculator
from lionagi.os.service.api.specification import ENDPOINT_CONFIG
from lionagi.os.service.api.status_tracker import StatusTracker
from lionagi.os.service.api.rate_limiter import RateLimiter
from lionagi.os.service.api.utils import create_payload


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
        endpoint: str,
        endpoint_config: ENDPOINT_CONFIG | dict,
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        token_calculator: TokenCalculator | Type | None = None,
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
        if isinstance(endpoint_config, dict):
            endpoint_config = ENDPOINT_CONFIG(**endpoint_config)
        self.endpoint_config = endpoint_config
        self.rate_limit_kwargs = {
            "interval": interval,
            "interval_request": interval_request,
            "interval_token": interval_token,
            "token_calculator": token_calculator,
            "tokenizer": tokenizer,
            **kwargs,
        }
        self.status_tracker = StatusTracker()
        self._has_initialized = False

    async def init_rate_limiter(self) -> None:
        """Initialize the rate limiter for the endpoint."""
        self.rate_limiter = await RateLimiter.create(**self.rate_limit_kwargs)
        self._has_initialized = True

    def create_payload(
        self,
        input_: Any,
        input_key: str = None,
        config: dict = None,
        required_params: list[str] = None,
        optional_params: list[str] = None,
        **kwargs,
    ):
        """kwargs are for additional model arguments"""
        return create_payload(
            input_=input_,
            input_key=input_key or self.endpoint_config.input_key,
            config=config or self.endpoint_config.default_config,
            required_=required_params or self.endpoint_config.required_params,
            optional_=optional_params or self.endpoint_config.required_params,
            **kwargs,
        )

    def calculate_token(
        self,
        payload: dict = None,
        image_base64: str = None,
    ):
        ep = self.endpoint
        return self.rate_limiter.token_calculator.calculate(
            ep, payload=payload, image_base64=image_base64
        )


# File: lionagi/os/service/api/endpoint.py
