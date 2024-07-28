from os import getenv
from functools import singledispatchmethod
from typing import Any, Callable, Mapping, Type

import aiohttp
import logging

from lion_core import LN_UNDEFINED
from lion_core.libs import nget
from lion_core.exceptions import LionOperationError
from lionagi.os.file.tokenize.token_calculator import TokenCalculator
from lionagi.os.service.endpoint.endpoint import EndPoint


class BaseService:
    """Base class for API services with rate limiting capabilities.

    This class provides a framework for managing multiple API endpoints
    with rate limiting and caching functionalities.

    Attributes:
        base_url (str): Base URL for the API service.
        available_endpoints (list): List of available endpoint names.
    """

    base_url: str = ""
    available_endpoints: list = []
    default_endpoint: str = "chat/completions"
    default_provider_config: dict = {}
    default_provider_pricing: dict = {}
    token_calculator: TokenCalculator | Type = TokenCalculator

    def __init__(
        self,
        provider_config: dict | None = None,
        provider_pricing: dict | None = None,
        api_key: str | None = None,
        api_key_scheme: str | None = None,
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        token_calculator: TokenCalculator | Type | None = None,
        tokenizer: Callable | None = None,
        tokenizer_config: dict = {},
    ):
        """Initialize the BaseService.

        Args:
            provider_config: Configuration for the service provider.
            provider_pricing: Pricing information for the service.
            api_key: API key for authentication.
            api_key_scheme: Environment variable name for the API key.
            interval: Time interval for rate limiting.
            interval_request: Maximum requests per interval.
            interval_token: Maximum tokens per interval.
            token_calculator: Calculator for token usage.
            tokenizer: Tokenizer function.
            tokenizer_config: Additional configuration for the tokenizer.
        """
        self._api_key = api_key or getenv(api_key_scheme, None)
        self.provider_config = provider_config or self.default_provider_config
        self.provider_pricing = provider_pricing or self.default_provider_pricing
        self.endpoints: dict[str, EndPoint] = {}
        self.rate_limit_config = {
            "interval": interval,
            "interval_request": interval_request,
            "interval_token": interval_token,
            "token_calculator": token_calculator or self.token_calculator,
            "tokenizer": tokenizer,
            **tokenizer_config,
        }

    @singledispatchmethod
    async def _init_endpoint(self, endpoint: Any, **kwargs):
        """Initialize an endpoint."""
        raise NotImplementedError(f"Endpoint {endpoint} not implemented.")

    @_init_endpoint.register(EndPoint)
    async def _(self, endpoint: EndPoint, **kwargs):
        """Initialize an EndPoint instance."""
        if endpoint.endpoint not in self.endpoints:
            self.endpoints[endpoint.endpoint] = endpoint
        if not self.endpoints[endpoint.endpoint]._has_initialized:
            await self.endpoints[endpoint.endpoint].init_rate_limiter()

    @_init_endpoint.register(str)
    async def _(self, endpoint: str, **kwargs):
        """Initialize an endpoint by name."""
        if endpoint not in self.available_endpoints:
            raise ValueError(
                f"Endpoint {endpoint} not available for service "
                f"{self.__class__.__name__}"
            )
        endpoint_config = nget(self.schema, [endpoint, "config"])
        rate_limit_config = {**self.rate_limit_config, **kwargs}
        endpoint = EndPoint(
            endpoint=endpoint,
            endpoint_config=endpoint_config,
            **rate_limit_config,
        )
        await self._init_endpoint(endpoint)

    @_init_endpoint.register(set)
    @_init_endpoint.register(tuple)
    @_init_endpoint.register(list)
    async def _(self, endpoint, **kwargs):
        """Initialize multiple endpoints."""
        for ep in endpoint:
            await self._init_endpoint(ep, **kwargs)

    async def call_api(
        self,
        *,
        endpoint: str,
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
        cached: bool = False,
        base_url: str | None = None,
        **kwargs,
    ) -> Any:
        """Make an API call to the specified endpoint.

        Args:
            endpoint: The name of the endpoint to call.
            method: The HTTP method to use (default: "post").
            retries: Number of retries for failed calls.
            initial_delay: Initial delay before first retry.
            delay: Delay between retries.
            backoff_factor: Factor to increase delay between retries.
            default: Default value to return on failure.
            timeout: Timeout for the API call.
            verbose: Whether to log verbose output.
            error_msg: Custom error message for failures.
            error_map: Mapping of exception types to handler functions.
            payload: The payload to send with the request.
            required_tokens: Number of tokens required for the call.
            cached: Whether to use cached results.
            **kwargs: Additional keyword arguments for the API call.

        Returns:
            The API response or the default value on failure.

        Raises:
            LionOperationError: If the endpoint is not initialized.
        """
        if endpoint not in self.endpoints:
            try:
                await self._init_endpoint(endpoint)
            except NotImplementedError as e:
                raise LionOperationError(
                    f"The endpoint {endpoint} has not been initialized."
                ) from e

        call_api = (
            self.endpoints[endpoint].rate_limiter.cached_call_api
            if cached
            else self.endpoints[endpoint].rate_limiter.call_api
        )
        base_url = base_url or self.base_url
        if not base_url:
            base_url = self.provider_config.get("base_url")

        async with aiohttp.ClientSession() as http_session:
            return await call_api(
                http_session=http_session,
                api_key=self._api_key,
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

    async def serve(
        self,
        input_: Any,
        endpoint: str | EndPoint = None,
        *,
        endpoint_config: dict | None = None,
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
        required_tokens: int | None = None,
        cached: bool = False,
        **kwargs,
    ):
        """kwargs are for additional model arguments"""
        endpoint = endpoint or self.default_endpoint
        ep_ = endpoint.endpoint if isinstance(endpoint, EndPoint) else endpoint
        if not ep_ in self.endpoints:
            try:
                await self._init_endpoint(endpoint)
            except NotImplementedError as e:
                raise LionOperationError(
                    f"The endpoint {endpoint} has not been initialized."
                ) from e

        payload = self.endpoints[ep_].create_payload(
            input_=input_, config=endpoint_config, **kwargs
        )
        try:
            completion = await self.call_api(
                endpoint=ep_,
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
                cached=cached,
                **kwargs,
            )
            return payload, completion
        except LionOperationError as e:
            logging.error(f"API call to {ep_} failed: {e}")
            self.endpoints["chat/completions"].status_tracker.num_tasks_failed += 1
            return payload, None

    async def chat_completion(
        self, messages, required_tokens=None, **kwargs
    ) -> tuple[dict, dict | None]:
        """kwargs are for BaseService.serve function"""
        return await self.serve(
            input_=self.prepare_chat_input(messages),
            endpoint="chat/completions",
            method="post",
            required_tokens=required_tokens,
            **kwargs,
        )

    # override this method in the child class if need to prepare the input differently
    @staticmethod
    def prepare_chat_input(messages):
        """openai standard with optional image processing"""
        msgs = []

        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, (dict, str)):
                    msgs.append({"role": msg["role"], "content": content})
                elif isinstance(content, list):
                    _content = []
                    for i in content:
                        if "text" in i:
                            _content.append({"type": "text", "text": str(i["text"])})
                        elif "image_url" in i:
                            _content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"{i['image_url'].get('url')}",
                                        "detail": i["image_url"].get("detail", "low"),
                                    },
                                }
                            )
                    msgs.append({"role": msg["role"], "content": _content})

        return msgs


# File: lionagi/os/service/api/base_service.py
