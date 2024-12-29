# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..endpoint import ChatCompletionEndPoint


class AnthropicChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://docs.anthropic.com/en/api/
    """

    provider: str = "anthropic"
    base_url: str = "https://api.anthropic.com/v1"
    endpoint: str = "messages"

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
