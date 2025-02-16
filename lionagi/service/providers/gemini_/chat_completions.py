# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import AsyncGenerator

from google import genai
from google.genai import types as _g_types

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

client = genai.Client()
response = client.models.generate_content()
config = _g_types.GenerateContentConfig()

CHAT_COMPLETION_CONFIG = {}


CHAT_COMPLETION_CONFIG = {
    "provider": "google",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "endpoint": "models/{model}:generateContent?key=${GOOGLE_API_KEY}",
    "method": "post",
    "openai_compatible": False,
    "is_invokeable": True,
    "requires_tokens": True,
    "is_streamable": True,
    "required_kwargs": {
        "contents",
        "model",
    },
    "optional_kwargs": {
        "config",
    },
    "allowed_roles": ["user", "assistant", "system"],
    "invoke_with_endpoint": True,
}


class OllamaChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://platform.openai.com/docs/api-reference/chat/create
    """

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        from lionagi.libs.package.imports import check_import

        check_import("openai")
        check_import("ollama")

        from ollama import list, pull
        from openai import AsyncOpenAI

        super().__init__(config)
        self.client = AsyncOpenAI(
            base_url=self.config.base_url,
            api_key="ollama",
        )
        self._pull = pull
        self._list = list

    async def _invoke(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        self._check_model(payload["model"])
        params = {**payload, **kwargs}
        headers.pop("Authorization", None)
        params["extra_headers"] = headers

        if "response_format" in payload:
            return await self.client.beta.chat.completions.parse(**params)
        params.pop("response_format", None)
        return await self.client.chat.completions.create(**params)

    async def _stream(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ) -> AsyncGenerator:

        self._check_model(payload["model"])
        params = {**payload, **kwargs}
        headers.pop("Authorization", None)
        params["extra_headers"] = headers

        async for chunk in self.client.beta.chat.completions.stream(**params):
            yield chunk

    @property
    def allowed_roles(self):
        return ["system", "user", "assistant"]

    def _pull_model(self, model: str):
        from tqdm import tqdm

        current_digest, bars = "", {}
        for progress in self._pull(model, stream=True):
            digest = progress.get("digest", "")
            if digest != current_digest and current_digest in bars:
                bars[current_digest].close()

            if not digest:
                print(progress.get("status"))
                continue

            if digest not in bars and (total := progress.get("total")):
                bars[digest] = tqdm(
                    total=total,
                    desc=f"pulling {digest[7:19]}",
                    unit="B",
                    unit_scale=True,
                )

            if completed := progress.get("completed"):
                bars[digest].update(completed - bars[digest].n)

            current_digest = digest

    def _list_local_models(self) -> set:
        response = self._list()
        return {i.model for i in response.models}

    def _check_model(self, model: str):
        if model not in self._list_local_models():
            self._pull_model(model)
