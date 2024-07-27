from typing import Callable, Type, Any
from pydantic import BaseModel, ConfigDict

from lionagi.os.file.tokenize.token_calculator import TokenCalculator
from lionagi.os.service.api.specification import ENDPOINT_CONFIG
from lionagi.os.service.api.status_tracker import StatusTracker
from lionagi.os.service.api.rate_limiter import RateLimiter
from lionagi.os.service.api.utils import create_payload


class ENDPOINT_CONFIG(BaseModel):
    endpoint: str
    pricing: tuple
    batch_pricing: tuple
    token_limit: int
    default_config: dict
    default_rate_limit: tuple  # (interval, interval_request, interval_token)
    required_params: list[str] = []
    optional_params: list[str] = []
    input_key: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True, populate_by_name=True, extra="forbid"
    )

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, **data):
        return cls(**data)


class EndPoint:

    def __init__(
        self,
        endpoint: str,
        endpoint_config: ENDPOINT_CONFIG | dict = {},
        rate_limiter: RateLimiter | None = None,  # takes priority over endpoint_config
    ) -> None:

        self.endpoint = endpoint
        if isinstance(endpoint_config, dict):
            self.endpoint_config = ENDPOINT_CONFIG(**endpoint_config)
        else:
            self.endpoint_config = endpoint_config

        self.status_tracker = StatusTracker()

        if rate_limiter and isinstance(rate_limiter, RateLimiter):
            self.rate_limiter = rate_limiter
            self._has_initialized = True
        else:
            self._has_initialized = False

    async def init_rate_limiter(self) -> None:
        """Initialize the rate limiter for the endpoint."""
        if not self._has_initialized:
            self.rate_limiter = await RateLimiter.create(
                *self.endpoint_config.default_rate_limit
            )
            self._has_initialized = True

    def create_payload(
        self,
        input_: Any,
        input_key: str = None,
        config: dict = None,
        required_params: list[str] = None,
        optional_params: list[str] = None,
        **kwargs,
    ) -> dict:
        """kwargs are for additional model arguments"""
        return create_payload(
            input_=input_,
            input_key=input_key or self.endpoint_config.input_key,
            config=config or self.endpoint_config.default_config,
            required_=required_params or self.endpoint_config.required_params,
            optional_=optional_params or self.endpoint_config.required_params,
            **kwargs,
        )


# File: lionagi/os/service/api/endpoint.py
