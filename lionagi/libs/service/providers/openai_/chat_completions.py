# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

from .spec import reasoning_models, reasoning_not_support_params

CHAT_COMPLETION_CONFIG = {
    "provider": "openai",
    "base_url": "https://api.openai.com/v1",
    "endpoint": "chat/completions",
    "method": "post",
    "openai_compatible": True,
    "is_invokeable": True,
    "requires_tokens": True,
    "is_streamable": True,
    "required_kwargs": {
        "messages",
        "model",
    },
    "deprecated_kwargs": {
        "max_tokens",
        "function_call",
        "functions",
    },
    "optional_kwargs": {
        "store",
        "reasoning_effort",
        "metadata",
        "frequency_penalty",
        "logit_bias",
        "logprobs",
        "top_logprobs",
        "max_completion_tokens",
        "n",
        "modalities",
        "prediction",
        "audio",
        "presence_penalty",
        "response_format",
        "seed",
        "service_tier",
        "stop",
        "stream",
        "stream_options",
        "temperature",
        "top_p",
        "tools",
        "tool_choice",
        "parallel_tool_calls",
        "user",
    },
    "allowed_roles": ["user", "assistant", "system", "developer", "tool"],
}


class OpenAIChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://platform.openai.com/docs/api-reference/chat/create
    """

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)

    def create_payload(self, **kwargs) -> dict:
        """Generates a request payload (and headers) for this endpoint.

        Args:
            **kwargs:
                Arbitrary parameters passed by the caller.

        Returns:
            dict:
                A dictionary containing:
                - "payload": A dict with filtered parameters for the request.
                - "headers": A dict of additional headers (e.g., `Authorization`).
                - "is_cached": Whether the request is to be cached.
        """
        payload = {}
        is_cached = kwargs.get("is_cached", False)
        headers = kwargs.get("headers", {})
        for k, v in kwargs.items():
            if k in self.acceptable_kwargs:
                payload[k] = v
        if "api_key" in kwargs:
            headers["Authorization"] = f"Bearer {kwargs['api_key']}"

        if payload.get("model") in reasoning_models:
            for param in reasoning_not_support_params:
                payload.pop(param, None)
            if payload["messages"][0].get("role") == "system":
                payload["messages"][0]["role"] = "developer"
        else:
            payload.pop("reasoning_effort", None)

        return {
            "payload": payload,
            "headers": headers,
            "is_cached": is_cached,
        }
