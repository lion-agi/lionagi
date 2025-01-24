# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing_extensions import override

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

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

    @override
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
        dict_ = super().create_payload(**kwargs)
        if (
            "o1" in dict_["payload"]["model"]
            or "o3" in dict_["payload"]["model"]
        ):
            dict_["payload"]["messages"][0]["role"] = "developer"
        return dict_
