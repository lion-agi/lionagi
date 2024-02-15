import asyncio
import logging
import aiohttp
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, NoReturn, Optional, Type, List, Union

from ..utils import nget, APIUtil, to_list, lcall
from .base_rate_limiter import BaseRateLimiter, SimpleRateLimiter
from .status_tracker import StatusTracker

from .base_endpoint import BaseEndpoint


class BaseService:
    """
    Base class for services that interact with API endpoints.

    This class provides a foundation for services that need to make API calls with rate limiting.

    Attributes:
        api_key (Optional[str]): The API key used for authentication.
        schema (Dict[str, Any]): The schema defining the service's endpoints.
        status_tracker (StatusTracker): The object tracking the status of API calls.
        endpoints (Dict[str, BaseEndpoint]): A dictionary of endpoint objects.
    """

    base_url: str = ''
    available_endpoints: list = []

    def __init__(
        self,
        api_key: Optional[str] = None,
        schema: Dict[str, Any] = None,
        token_encoding_name: str = None,
        max_tokens : int = 100_000,
        max_requests : int = 1_000,
        interval: int = 60
    ) -> None:
        self.api_key = api_key
        self.schema = schema or {}
        self.status_tracker = StatusTracker()
        self.endpoints: Dict[str, BaseEndpoint] = {}
        self.token_encoding_name = token_encoding_name
        self.chat_config = {
            'max_requests': max_requests,
            'max_tokens': max_tokens,
            'interval': interval,
            "token_encoding_name": token_encoding_name
        }


    async def init_endpoint(self, endpoint_: Optional[Union[List[str], List[BaseEndpoint], str, BaseEndpoint]] = None) -> None:
        """
        Initializes the specified endpoint or all endpoints if none is specified.

        Args:
            endpoint_: The endpoint(s) to initialize. Can be a string, an BaseEndpoint, a list of strings, or a list of BaseEndpoints.
        """

        if endpoint_:
            endpoint_ = to_list(endpoint_, flatten=True, dropna=True)
            
            for ep in endpoint_:
                self._check_endpoints(ep)
            
                if ep not in self.endpoints:
                    endpoint_config = self._get_endpoint(ep)

                    if endpoint_config is not None:
                        if ep == "chat/completions":
                            self.endpoints[ep] = BaseEndpoint(
                                max_requests=self.chat_config.get('max_requests', 1000),
                                max_tokens=self.chat_config.get('max_tokens', 100000),
                                interval=self.chat_config.get('interval', 60),
                                endpoint_=ep,
                                token_encoding_name=self.token_encoding_name,
                                config=endpoint_config,
                            )
                        else:
                            self.endpoints[ep] = BaseEndpoint(
                                max_requests=endpoint_config.get('max_requests', 1000) if endpoint_config.get('max_requests', 1000) is not None else 1000,
                                max_tokens=endpoint_config.get('max_tokens', 100000) if endpoint_config.get('max_tokens', 100000) is not None else 100000,
                                interval=endpoint_config.get('interval', 60) if endpoint_config.get('interval', 60) is not None else 60,
                                endpoint_=ep,
                                token_encoding_name=self.token_encoding_name,
                                config=endpoint_config,
                            )

                if not self.endpoints[ep]._has_initialized:
                    await self.endpoints[ep].init_rate_limiter()

        else:
            for ep in self.available_endpoints:
                endpoint_config = nget(self.schema, [ep, 'config'])
                self.schema.get(ep, {})
                if ep not in self.endpoints:
                    self.endpoints[ep] = BaseEndpoint(
                        max_requests=endpoint_config.get('max_requests', 1000),
                        max_tokens=endpoint_config.get('max_tokens', 100000),
                        interval=endpoint_config.get('interval', 60),
                        endpoint_=ep,
                        token_encoding_name=self.token_encoding_name,
                        config=endpoint_config,
                    )
                if not self.endpoints[ep]._has_initialized:
                    await self.endpoints[ep].init_rate_limiter()

    async def call_api(self, payload, endpoint, method, **kwargs):
        """
        Calls the specified API endpoint with the given payload and method.

        Args:
            payload: The payload to send with the API call.
            endpoint: The endpoint to call.
            method: The HTTP method to use for the call.
            kwargs are for tiktoken encoding

        Returns:
            The response from the API call.

        Raises:
            ValueError: If the endpoint has not been initialized.
        """
        if endpoint not in self.endpoints.keys():
            raise ValueError(f'The endpoint {endpoint} has not initialized.')
        async with aiohttp.ClientSession() as http_session:
            completion = await self.endpoints[endpoint].rate_limiter._call_api(
                http_session=http_session, endpoint=endpoint, base_url=self.base_url, api_key=self.api_key,
                method=method, payload=payload, **kwargs)
            return completion

    def _check_endpoints(self, endpoint_):
        f = lambda ep: ValueError (f"Endpoint {ep} not available for service {self.__class__.__name__}")
        if not endpoint_ in self.available_endpoints:
            raise f(endpoint_)
        
    def _get_endpoint(self, endpoint_):
        if endpoint_ not in self.endpoints:
            endpoint_config = nget(self.schema, [endpoint_, 'config'])
            self.schema.get(endpoint_, {})

            if isinstance(endpoint_, BaseEndpoint):
                self.endpoints[endpoint_.endpoint] = endpoint_
            return None
        return endpoint_config