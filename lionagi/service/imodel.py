# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import os

from lionagi.service.api_calling import APICalling
from lionagi.service.endpoint import EndPoint

from .match_endpoint import match_endpoint
from .rate_limited_processor import RateLimitedAPIExecutor


class iModel:

    def __init__(
        self,
        provider: str = None,
        base_url: str = None,
        endpoint: str | EndPoint = None,
        endpoint_params: list[str] | None = None,
        api_key: str = None,
        queue_capacity: int = 100,
        capacity_refresh_time: float = 60,
        interval: float | None = None,
        limit_requests: int = None,
        limit_tokens: int = None,
        **kwargs,
    ):
        api_key = os.getenv(api_key, None) or api_key
        kwargs["api_key"] = api_key
        model = kwargs.get("model", None)
        if model:
            if not provider:
                if "/" in model:
                    provider = model.split("/")[0]
                    model = model.replace(provider + "/", "")
                    kwargs["model"] = model
                else:
                    raise ValueError("Provider must be provided")

        if isinstance(endpoint, EndPoint):
            self.endpoint = endpoint
        else:
            self.endpoint = match_endpoint(
                provider=provider,
                base_url=base_url,
                endpoint=endpoint,
                endpoint_params=endpoint_params,
            )
        self.kwargs = kwargs
        self.executor = RateLimitedAPIExecutor(
            queue_capacity=queue_capacity,
            capacity_refresh_time=capacity_refresh_time,
            interval=interval,
            limit_requests=limit_requests,
            limit_tokens=limit_tokens,
        )

    async def invoke(self, **kwargs) -> APICalling | None:
        try:
            api_call = self.endpoint.create_api_calling(**kwargs)
            if self.executor.processor is None:
                await self.executor.start()

            await self.executor.append(api_call)
            await self.executor.forward()
            if api_call.id in self.executor.completed_events:
                return self.executor.completed_events[api_call.id]
        except Exception:
            return None

    @property
    def allowed_roles(self):
        if hasattr(self.endpoint, "allowed_roles"):
            return self.endpoint.allowed_roles
        return ["system", "user", "assistant"]


class iModelManager:

    def __init__(self):
        self.registry: dict[str, iModel] = {}

    @property
    def chat(self) -> iModel:
        return self.registry.get("chat", None)

    @property
    def parse(self) -> iModel:
        return self.registry.get("parse", None)

    def register_imodel(self, name: str, model: iModel):
        if isinstance(model, iModel):
            self.registry[name] = model
        else:
            raise TypeError("Input model is not an instance of iModel")
