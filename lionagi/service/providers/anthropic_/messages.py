# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

CHAT_COMPLETION_CONFIG = {
    "provider": "anthropic",
    "endpoint": "messages",
    "method": "post",
    "requires_tokens": True,
    "openai_compatible": False,
    "is_invokeable": True,
    "is_streamable": True,
    "base_url": "https://api.anthropic.com/v1",
    "api_version": "2023-06-01",
    "required_kwargs": {
        "messages",
        "model",
        "max_tokens",
    },
    "optional_kwargs": {
        "metadata",
        "stop_sequences",
        "stream",
        "system",
        "temperature",
        "tool_choice",
        "tools",
        "top_p",
        "top_k",
    },
    "allowed_roles": ["user", "assistant"],
}


class AnthropicChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://docs.anthropic.com/en/api/
    """

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)

    def create_payload(self, **kwargs) -> dict:
        payload = {}
        cached = kwargs.get("cached", False)
        headers = kwargs.get("headers", {})
        for k, v in kwargs.items():
            if k in self.acceptable_kwargs:
                payload[k] = v
        if "api_key" in kwargs:
            headers["x-api-key"] = kwargs["api_key"]
        headers["anthropic-version"] = kwargs.pop(
            "api_version", self.config.api_version
        )
        if "content-type" not in kwargs:
            headers["content-type"] = "application/json"

        return {
            "payload": payload,
            "headers": headers,
            "cached": cached,
        }
