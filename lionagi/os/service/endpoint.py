import asyncio
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
    ) -> None:
        self.endpoint = schema.endpoint
        self.schema = schema
        self.token_calculator = token_calculator
        self.rate_limiter = rate_limiter or RateLimitedExecutor(
            interval=interval,
            interval_request=interval_request,
            interval_token=interval_token,
            refresh_time=refresh_time,
        )
        if self.rate_limiter.processor is None:
            self._is_initialized = False
        else:
            self._is_initialized = True

    async def init_rate_limiter(self) -> None:
        """Initialize the rate limiter for the endpoint."""
        if not self._has_initialized:
            await self.rate_limiter.create_processor()
            self._has_initialized = True

    async def add_api_calling(
        self,
        payload: dict | None= None,       # priority 1
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

    async def execute(self) -> None:
        if not self._has_initialized:
            await self.init_rate_limiter()
        await self.rate_limiter.execute()

    async def stop(self) -> None:
        await self.rate_limiter.stop()

    async def serve(
        self,
        payload: dict = None,
        base_url: str = None,
        method="post",
        api_key: str = None,
        retry_config=RETRY_CONFIG,
    ):
        if not self.rate_limiter.execution_mode:
            await self.execute()

        action_id = await self.add_api_calling(
            payload=payload,
            base_url=base_url,
            endpoint=self.endpoint,
            api_key=api_key,
            method=method,
            retry_config=retry_config,
        )

        while action_id not in self.rate_limiter.completed_action:
            await asyncio.sleep(0.25)

        action: APICalling = self.rate_limiter.pile.pop(action_id)
        return action.to_log()


# File: lionagi/os/service/api/endpoint.py
