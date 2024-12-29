# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Literal

import litellm
from aiocache import cached
from pydantic import BaseModel, Field

from lionagi.service.api_calling import APICalling

from ..settings import Settings
from .token_calculator import TokenCalculator

litellm.drop_params = True


class EndPoint(BaseModel, ABC):
    base_url: str
    endpoint: str
    endpoint_params: list[str] | None = None
    method: Literal["get", "post", "put", "delete"] = Field("post")

    @abstractmethod
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
        return self.base_url + self.endpoint

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

    def create_api_calling(self, **kwargs) -> APICalling:
        payload = self.create_payload(**kwargs)
        return APICalling(
            endpoint=self,
            rcall_params=kwargs.get("rcall_params", None),
            **payload,
        )


class ChatCompletionEndPoint(EndPoint):

    provider: str
    endpoint: str = "chat/completions"
    method: str = "post"

    def is_invokeable(self):
        return True

    async def _invoke(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        from litellm import acompletion

        provider = provider or self.provider

        if not provider in payload["model"]:
            payload["model"] = f"{provider}/{payload['model']}"

        api_key = None

        if "Authorization" in headers:
            api_key = headers.pop("Authorization").replace("Bearer ", "")

        params = {
            "api_key": api_key,
            "base_url": self.base_url,
            **payload,
            **kwargs,
        }
        if headers:
            params["extra_headers"] = headers

        return await acompletion(**params)

    @property
    def allowed_roles(self):
        return ["system", "user", "assistant"]
