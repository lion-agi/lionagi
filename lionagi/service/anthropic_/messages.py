# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..endpoint import ChatCompletionEndPoint


class AnthropicChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://docs.anthropic.com/en/api/
    """

    api_version: str = "2023-06-01"
    provider: str = "anthropic"
    base_url: str = "https://api.anthropic.com/v1"
    endpoint: str = "messages"

    @property
    def openai_compatible(self) -> bool:
        return False

    @property
    def required_kwargs(self) -> set[str]:
        return {
            "messages",
            "model",
            "max_tokens",
        }

    @property
    def optional_kwargs(self) -> set[str]:
        using = {
            "metadata",
            "stop_sequences",
            "stream",
            "system",
            "temperature",
            "tool_choice",
            "tools",
            "top_p",
            "top_k",
        }
        return using

    @property
    def allowed_roles(self):
        return ["user", "assistant"]

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
            "api_version", self.api_version
        )
        if "content-type" not in kwargs:
            headers["content-type"] = "application/json"

        return {
            "payload": payload,
            "headers": headers,
            "cached": cached,
        }
