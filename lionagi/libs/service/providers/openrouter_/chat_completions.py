# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

CHAT_COMPLETION_CONFIG = {
    "provider": "openrouter",
    "base_url": "https://openrouter.ai/api/v1",
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
    "allowed_roles": ["user", "assistant", "system"],
}


class OpenRouterChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://openrouter.ai/docs/quick-start#quick-start
    """

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)
