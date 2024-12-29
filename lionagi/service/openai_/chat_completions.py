# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..endpoint import ChatCompletionEndPoint


class OpenAIChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://platform.openai.com/docs/api-reference/chat/create
    """

    provider: str = "openai"
    base_url: str = "https://api.openai.com/v1"

    @property
    def required_kwargs(self) -> set[str]:
        return {
            "messages",
            "model",
        }

    @property
    def optional_kwargs(self) -> set[str]:

        deprecated = {
            "max_tokens",
            "function_call",
            "functions",
        }
        using = {
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
        }
        return using | deprecated
