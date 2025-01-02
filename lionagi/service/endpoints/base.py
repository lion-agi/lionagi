import asyncio
import logging
from abc import ABC
from typing import Literal

import aiohttp
from aiocache import cached
from pydantic import BaseModel, ConfigDict, Field

from lionagi._errors import ExecutionError, RateLimitError
from lionagi.protocols.types import Event, EventStatus
from lionagi.settings import Settings

from .token_calculator import TokenCalculator


class EndpointConfig(BaseModel):

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        populate_by_name=True,
        use_enum_values=True,
    )

    provider: str | None = None
    base_url: str | None = None
    endpoint: str
    endpoint_params: dict = None
    method: Literal["get", "post", "put", "delete"] = Field("post")
    openai_compatible: bool = False
    required_kwargs: set[str] = Field(default_factory=set)
    optional_kwargs: set[str] = Field(default_factory=set)
    deprecated_kwargs: set[str] = Field(default_factory=set)
    is_invokeable: bool = False
    is_streamable: bool = False
    requires_tokens: bool = False
    api_version: str | None = None
    allowed_roles: list[str] | None = None


class EndPoint(ABC):

    def __init__(self, config: dict):
        self.config = EndpointConfig(**config)

    @property
    def is_streamable(self) -> bool:
        return self.config.is_streamable

    @property
    def requires_tokens(self) -> bool:
        return self.config.requires_tokens

    @property
    def openai_compatible(self) -> bool:
        return self.config.openai_compatible

    @property
    def is_invokeable(self) -> bool:
        return self.config.is_invokeable

    @property
    def required_kwargs(self) -> set[str]:
        return self.config.required_kwargs

    @property
    def optional_kwargs(self) -> set[str]:
        return self.config.optional_kwargs

    @property
    def deprecated_kwargs(self) -> set[str]:
        return self.config.deprecated_kwargs

    @property
    def endpoint_params(self) -> dict | None:
        return self.config.endpoint_params

    @property
    def method(self) -> str:
        return self.config.method

    @property
    def endpoint(self) -> str:
        return self.config.endpoint

    @property
    def acceptable_kwargs(self) -> set[str]:
        return (
            self.required_kwargs
            | self.optional_kwargs
            | self.deprecated_kwargs
        )

    @property
    def full_url(self):
        if self.config.endpoint_params:
            return self.config.base_url + self.config.endpoint.format(
                **self.endpoint_params
            )
        return self.config.base_url + "/" + self.config.endpoint

    @property
    def allowed_roles(self) -> list[str] | None:
        return self.config.allowed_roles

    @property
    def sequential_exchange(self) -> bool:
        if self.allowed_roles:
            return len(self.allowed_roles) == 2
        return False

    @property
    def roled(self) -> bool:
        return self.allowed_roles is not None

    def create_payload(self, **kwargs) -> dict:
        payload = {}
        is_cached = kwargs.get("is_cached", False)
        headers = kwargs.get("headers", {})
        for k, v in kwargs.items():
            if k in self.acceptable_kwargs:
                payload[k] = v
        if "api_key" in kwargs:
            headers["Authorization"] = f"Bearer {kwargs['api_key']}"
        return {
            "payload": payload,
            "headers": headers,
            "is_cached": is_cached,
        }

    async def invoke(
        self, payload, headers, is_cached: bool = False, **kwargs
    ):
        if is_cached:
            return await self._cached_invoke(payload, headers, **kwargs)
        return await self._invoke(payload, headers, **kwargs)

    async def _invoke(self, payload: dict, headers: dict, **kwargs):
        raise NotImplementedError

    async def _stream(self, payload: dict, headers: dict, **kwargs):
        raise NotImplementedError

    @cached(**Settings.API.CACHED_CONFIG)
    async def _cached_invoke(self, payload, headers, **kwargs):
        return await self._invoke(payload, headers, **kwargs)

    def calculate_tokens(self, payload: dict) -> int:
        if self.requires_tokens:
            if "messages" in payload:
                return TokenCalculator.calculate_message_tokens(
                    payload["messages"]
                )
            if "embed" in self.full_url:
                return TokenCalculator.calcualte_embed_token(**payload)
        return 0


class APICalling(Event):

    payload: dict
    headers: dict = Field(exclude=True)
    endpoint: EndPoint = Field(exclude=True)
    is_cached: bool = Field(default=False, exclude=True)
    should_invoke_endpoint: bool = Field(default=True, exclude=True)

    @property
    def required_tokens(self) -> int | None:
        if self.endpoint.requires_tokens:
            return self.endpoint.calculate_tokens(self.payload)
        return None

    async def _inner(self, **kwargs):
        if not self.endpoint.required_kwargs.issubset(
            set(self.payload.keys())
        ):
            raise ValueError(
                f"Required kwargs not fully provided: {self.endpoint.required_kwargs}"
            )

        for k in list(self.payload.keys()):
            if k not in self.endpoint.acceptable_kwargs:
                self.payload.pop(k)

        async with aiohttp.ClientSession() as session:
            try:
                if (
                    _m := getattr(session, self.endpoint.method, None)
                ) is not None:
                    async with _m(
                        self.endpoint.full_url, **kwargs
                    ) as response:
                        response_json = await response.json()
                        if "error" not in response_json:
                            return response_json
                        if "Rate limit" in response_json["error"].get(
                            "message", ""
                        ):
                            await asyncio.sleep(5)
                            raise RateLimitError(
                                f"Rate limit exceeded. Error: {response_json['error']}"
                            )
                        raise ExecutionError(
                            "API call failed with error: ",
                            response_json["error"],
                        )
                else:
                    raise ValueError(
                        f"Invalid HTTP method: {self.endpoint.method}"
                    )
            except aiohttp.ClientError as e:
                logging.error(
                    f"API call to {self.endpoint.full_url} failed: {e}"
                )
                return None

    @cached(**Settings.API.CACHED_CONFIG)
    async def _cached_inner(self, **kwargs):
        return await self._inner(**kwargs)

    async def stream(self, **kwargs):
        start = asyncio.get_event_loop().time()
        response = []
        if not self.endpoint.is_streamable:
            raise ValueError(
                f"Endpoint {self.endpoint.endpoint} is not streamable."
            )

        async for i in self.endpoint._stream(
            self.payload, self.headers, **kwargs
        ):
            content = i.choices[0].delta.content
            if content is not None:
                print(content, end="", flush=True)
            response.append(i)
            yield i

        self.execution.duration = asyncio.get_event_loop().time() - start
        self.execution.response = response
        self.execution.status = EventStatus.COMPLETED

    async def invoke(self):
        start = asyncio.get_event_loop().time()
        kwargs = {"headers": self.headers, "json": self.payload}

        try:
            response = None
            if self.should_invoke_endpoint and self.endpoint.is_invokeable:
                response = await self.endpoint.invoke(
                    payload=self.payload,
                    headers=self.headers,
                    is_cached=self.is_cached,
                )
            else:
                if self.is_cached:
                    response = await self._cached_inner(**kwargs)
                else:
                    response = await self._inner(**kwargs)

            self.execution.duration = asyncio.get_event_loop().time() - start
            self.execution.response = response
            self.execution.status = EventStatus.COMPLETED
        except Exception as e:
            self.execution.duration = asyncio.get_event_loop().time() - start
            self.execution.error = str(e)
            self.execution.status = EventStatus.FAILED
            logging.error(f"API call to {self.endpoint.full_url} failed: {e}")

    def __str__(self) -> str:
        return (
            f"APICalling(id={self.id}, status={self.status}, duration="
            f"{self.execution.duration}, response={self.execution.response}"
            f", error={self.execution.error})"
        )

    __repr__ = __str__

    @property
    def request(self) -> dict:
        return {
            "required_tokens": self.required_tokens,
        }
