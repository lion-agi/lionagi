# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
from abc import ABC
from typing import Any, Literal

import aiohttp
import litellm
from aiocache import cached
from pydantic import BaseModel, Field, field_validator

from .._errors import ExecutionError, RateLimitError
from ..protocols.types import Event, EventStatus, Execution
from ..settings import Settings
from .token_calculator import TokenCalculator

litellm.drop_params = True


class EndPoint(BaseModel, ABC):

    base_url: str
    endpoint: str
    endpoint_params: list[str] | None = None
    method: Literal["get", "post", "put", "delete"] = Field("post")

    def create_payload(self, **kwargs) -> dict:
        payload = {}
        cached = kwargs.get("cached", False)
        headers = kwargs.get("headers", {})
        for k, v in kwargs.items():
            if k in self.acceptable_kwargs:
                payload[k] = v
        if "api_key" in kwargs:
            headers["Authorization"] = f"Bearer {kwargs['api_key']}"
        return {
            "payload": payload,
            "headers": headers,
            "cached": cached,
        }

    @property
    def required_kwargs(self) -> set[str]:
        raise NotImplementedError

    @property
    def optional_kwargs(self) -> set[str]:
        raise NotImplementedError

    @property
    def acceptable_kwargs(self) -> set[str]:
        return self.required_kwargs | self.optional_kwargs

    @property
    def requires_tokens(self):
        return False

    @property
    def full_url(self):
        if self.endpoint_params:
            return self.base_url + self.endpoint.format(**self.endpoint_params)
        return self.base_url + "/" + self.endpoint

    def is_invokeable(self):
        return False

    async def invoke(self, payload, headers, cached: bool = False, **kwargs):
        if cached:
            return await self._cached_invoke(payload, headers, **kwargs)
        return await self._invoke(payload, headers, **kwargs)

    async def _invoke(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        raise NotImplementedError

    @cached(**Settings.API.CACHED_CONFIG)
    async def _cached_invoke(self, payload, headers, **kwargs):
        return await self._invoke(payload, headers, **kwargs)

    def calculate_tokens(self, payload: dict) -> int:
        if self.requires_tokens:
            if "messages" in payload:
                return TokenCalculator.calculate_message_tokens(**payload)
            if "embed" in self.full_url:
                return TokenCalculator.calcualte_embed_token(**payload)
        return 0

    def create_api_calling(self, **kwargs) -> "APICalling":
        payload = self.create_payload(**kwargs)
        return APICalling(
            endpoint=self,
            **payload,
        )


class APICalling(Event):

    payload: dict
    headers: dict = Field(exclude=True)
    endpoint: EndPoint = Field(exclude=True)
    cached: bool = Field(default=False)

    @property
    def required_tokens(self) -> int | None:
        if self.endpoint.requires_tokens:
            return self.endpoint.calculate_tokens(self.payload)
        return None

    async def invoke(self):
        start = asyncio.get_event_loop().time()
        kwargs = {"headers": self.headers, "json": self.payload}

        async def _inner():
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
                        raise ValueError(f"Invalid HTTP method: {self.method}")
                except aiohttp.ClientError as e:
                    logging.error(f"API call to {self.full_url} failed: {e}")
                    return None

        @cached(**Settings.Action.CACHED_CONFIG)
        async def _cached_inner():
            return await _inner()

        try:
            response = None
            if self.endpoint.is_invokeable:
                response = await self.endpoint.invoke(
                    payload=self.payload,
                    headers=self.headers,
                    cached=self.cached,
                )
            else:
                if self.cached:
                    response = await _cached_inner()
                else:
                    response = await _inner()
            self.execution = Execution(
                status=EventStatus.COMPLETED,
                duration=asyncio.get_event_loop().time() - start,
                response=response,
            )
        except Exception as e:
            self.execution = Execution(
                status=EventStatus.FAILED,
                duration=asyncio.get_event_loop().time() - start,
                response=None,
                error=str(e),
            )
            logging.error(f"API call to {self.endpoint.full_url} failed: {e}")

    def __str__(self) -> str:
        return f"APICalling(id={self.id}, status={self.status}, duration={self.execution.duration}, response={self.execution.response}, error={self.execution.error})"

    __repr__ = __str__

    @property
    def request(self) -> dict:
        return {
            "required_tokens": self.required_tokens,
        }


class ChatCompletionEndPoint(EndPoint):

    provider: str
    endpoint: str = "chat/completions"
    method: str = "post"

    @property
    def openai_compatible(self) -> bool:
        return True

    @property
    def is_invokeable(self) -> bool:
        if not hasattr(self, "_invokeable"):
            self._invokeable = True
        return self._invokeable

    @is_invokeable.setter
    def is_invokeable(self, value: bool):
        self._invokeable = value

    async def _invoke(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        from litellm import acompletion

        provider = self.provider

        if not provider in payload["model"]:
            payload["model"] = f"{provider}/{payload['model']}"

        api_key = None

        if "Authorization" in headers:
            api_key = headers.pop("Authorization").replace("Bearer ", "")

        if "x-api-key" in headers:
            api_key = headers.pop("x-api-key")

        params = {
            "api_key": api_key,
            "base_url": self.base_url,
            **payload,
            **kwargs,
        }
        if headers:
            params["extra_headers"] = headers
        if not self.openai_compatible:
            params.pop("base_url")

        return await acompletion(**params)

    @property
    def allowed_roles(self):
        return ["system", "user", "assistant"]
