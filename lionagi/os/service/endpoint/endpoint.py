from .schema import EndpointSchema
from .rate_limiter import RateLimitedExecutor
from lionagi.os.service.config import RETRY_CONFIG
from lionagi.os.file.tokenize.token_calculator import TokenCalculator


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
        payload: dict = None,
        base_url: str = None,
        endpoint: str = None,
        api_key: str = None,
        method="post",
        retry_config=RETRY_CONFIG,
    ) -> None:
        tokens = self.token_calculator.calculate(payload)
        action = self.rate_limiter.create_api_calling(
            payload=payload,
            base_url=base_url,
            endpoint=endpoint,
            api_key=api_key,
            method=method,
            retry_config=retry_config,
        )
        action.required_tokens = tokens
        await self.rate_limiter.append(action)


# File: lionagi/os/service/api/endpoint.py
