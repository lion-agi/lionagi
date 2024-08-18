import inspect
from typing import Any

from lionagi.os.file.tokenize.token_calculator import TokenCalculator

from lionagi.os.service.schema import EndpointSchema
from lionagi.os.service.rate_limiter import RateLimitedExecutor
from lionagi.os.service.config import RETRY_CONFIG
from lionagi.os.service.api_calling import APICalling


class EndPoint:

    def __init__(
        self,
        schema: EndpointSchema,
        rate_limiter: RateLimitedExecutor = None,  # priority 1
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        refresh_time: float = 1,
        token_calculator: TokenCalculator = None,
        concurrent_capacity: int = None,
    ) -> None:
        self.endpoint = schema.endpoint
        self.schema = schema
        self.token_calculator = token_calculator
        self.rate_limiter = rate_limiter or RateLimitedExecutor(
            interval=interval or schema.default_rate_limit[0],
            interval_request=interval_request or schema.default_rate_limit[1],
            interval_token=interval_token or schema.default_rate_limit[2],
            refresh_time=refresh_time,
            concurrent_capacity=concurrent_capacity,
        )
        if self.rate_limiter.processor is None:
            self._has_initialized = False
        else:
            self._has_initialized = True

    def update_config(self, **kwargs):
        schema = self.schema.model_copy()
        schema.default_config.update(kwargs)
        self.schema = schema

    async def init_rate_limiter(self) -> None:
        """Initialize the rate limiter for the endpoint."""
        if not self._has_initialized:
            await self.rate_limiter.create_processor()
            self._has_initialized = True

    async def add_api_calling(
        self,
        payload: dict | None = None,  # priority 1
        input_: Any = None,
        base_url: str = None,
        endpoint: str = None,
        api_key: str = None,
        method="post",
        retry_config=RETRY_CONFIG,
    ) -> None:

        if (input_ and payload) or (not input_ and not payload):
            raise ValueError("Only one of input_ or payload should be provided.")

        if payload is None:
            payload = self.schema.create_payload(input_)

        input_ = payload[self.schema.input_key]
        if inspect.isclass(self.token_calculator):
            self.token_calculator = self.token_calculator()

        tokens = self.token_calculator.calculate(input_)
        action: APICalling = self.rate_limiter.create_api_calling(
            payload=payload,
            base_url=base_url,
            endpoint=endpoint,
            api_key=api_key,
            method=method,
            retry_config=retry_config,
        )
        action.required_tokens = tokens
        await self.rate_limiter.append(action)
        return action.ln_id

    async def serve(
        self,
        payload: dict = None,
        base_url: str = None,
        method="post",
        api_key: str = None,
        retry_config=None,
        **kwargs,
    ):
        c_ = {k: v for k, v in kwargs.items() if k not in RETRY_CONFIG}
        r_ = {k: v for k, v in kwargs.items() if k in RETRY_CONFIG}
        retry_config = {**(retry_config or RETRY_CONFIG), **r_}

        if c_:
            self.update_config(**c_)

        await self.init_rate_limiter()
        action_id = await self.add_api_calling(
            payload=payload,
            base_url=base_url,
            endpoint=self.endpoint,
            api_key=api_key,
            method=method,
            retry_config=retry_config,
        )
        await self.rate_limiter.process()
        if action_id in self.rate_limiter.completed_action:
            action: APICalling = self.rate_limiter.pile.pop(action_id)
            return action.to_log()
        return None


# File: lionagi/os/service/api/endpoint.py
