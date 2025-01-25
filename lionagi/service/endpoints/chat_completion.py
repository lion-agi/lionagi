# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
import warnings
from collections.abc import AsyncGenerator

from .base import EndPoint

warnings.filterwarnings(
    "ignore",
    message=".*Valid config keys have changed in V2.*",
    category=UserWarning,
    module="pydantic._internal._config",
)


CHAT_COMPLETION_CONFIG = {
    "endpoint": "chat/completions",
    "method": "post",
    "requires_tokens": True,
    "openai_compatible": True,
    "is_invokeable": True,
    "is_streamable": True,
}


class ChatCompletionEndPoint(EndPoint):

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)

    async def _invoke(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        from lionagi.libs.package.imports import check_import

        check_import("litellm")
        import litellm  # type: ignore

        litellm.drop_params = True
        from litellm import acompletion  # type: ignore

        provider = self.config.provider

        if not provider in payload["model"]:
            payload["model"] = f"{provider}/{payload['model']}"

        api_key = None

        if "Authorization" in headers:
            api_key = headers.pop("Authorization").replace("Bearer ", "")

        if "x-api-key" in headers:
            api_key = headers.pop("x-api-key")

        params = {
            "api_key": api_key,
            "base_url": self.config.base_url,
            **payload,
            **kwargs,
        }
        if headers:
            params["extra_headers"] = headers
        if not self.openai_compatible:
            params.pop("base_url")

        return await acompletion(**params)

    async def _stream(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ) -> AsyncGenerator:
        from lionagi.libs.package.imports import check_import

        check_import("litellm")
        import litellm  # type: ignore

        litellm.drop_params = True
        from litellm import acompletion  # type: ignore

        provider = self.config.provider

        if not provider in payload["model"]:
            payload["model"] = f"{provider}/{payload['model']}"

        api_key = None

        if "Authorization" in headers:
            api_key = headers.pop("Authorization").replace("Bearer ", "")

        if "x-api-key" in headers:
            api_key = headers.pop("x-api-key")

        params = {
            "api_key": api_key,
            "base_url": self.config.base_url,
            **payload,
            **kwargs,
        }
        if headers:
            params["extra_headers"] = headers
        if not self.openai_compatible:
            params.pop("base_url")

        params["stream"] = True
        async for i in await acompletion(**params):
            yield i

    @property
    def allowed_roles(self):
        return ["system", "user", "assistant"]
