# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
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
        "cache_control",
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

        for i in self.required_kwargs:
            if i not in payload:
                raise ValueError(f"Missing required argument: {i}")

        if "cache_control" in payload:
            cache_control = payload.pop("cache_control")
            if cache_control:
                cache_control = {"type": "ephemeral"}
                last_message = payload["messages"][-1]["content"]
                if isinstance(last_message, str):
                    last_message = {
                        "type": "text",
                        "text": last_message,
                        "cache_control": cache_control,
                    }
                elif isinstance(last_message, list) and isinstance(
                    last_message[-1], dict
                ):
                    last_message[-1]["cache_control"] = cache_control
                payload["messages"][-1]["content"] = (
                    [last_message]
                    if not isinstance(last_message, list)
                    else last_message
                )

        first_message = payload["messages"][0]
        system = None
        if first_message.get("role") == "system":
            system = first_message["content"]
            system = [{"type": "text", "text": system}]
            payload["messages"] = payload["messages"][1:]
            payload["system"] = system

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
