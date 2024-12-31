# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import os

from lionagi.service.endpoint import APICalling, EndPoint

from .match_endpoint import match_endpoint
from .rate_limited_processor import RateLimitedAPIExecutor


class iModel:

    def __init__(
        self,
        provider: str = None,
        base_url: str = None,
        endpoint: str | EndPoint = "chat",
        endpoint_params: list[str] | None = None,
        api_key: str = None,
        queue_capacity: int = 100,
        capacity_refresh_time: float = 60,
        interval: float | None = None,
        limit_requests: int = None,
        limit_tokens: int = None,
        invoke_with_endpoint: bool = True,
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

        self.endpoint.is_invokeable = invoke_with_endpoint
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
            kwargs.update(self.kwargs)
            api_call = self.endpoint.create_api_calling(**kwargs)
            if self.executor.processor is None:
                await self.executor.start()

            await self.executor.append(api_call)
            await self.executor.forward()
            if api_call.id in self.executor.completed_events:
                return self.executor.completed_events[api_call.id]
        except Exception as e:
            raise ValueError(f"Failed to invoke API call: {e}")

    @property
    def allowed_roles(self):
        if hasattr(self.endpoint, "allowed_roles"):
            return self.endpoint.allowed_roles
        return ["system", "user", "assistant"]
