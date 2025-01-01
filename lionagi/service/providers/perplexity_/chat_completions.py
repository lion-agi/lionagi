# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

CHAT_COMPLETION_CONFIG = {
    "provider": "perplexity",
    "base_url": "https://api.perplexity.ai",
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
    "optional_kwargs": {
        "max_tokens",
        "temperature",
        "top_p",
        "search_domain_filter",
        "return_images",
        "return_related_questions",
        "search_recency_filter",
        "top_k",
        "stream",
        "presence_penalty",
        "frequency_penalty",
    },
    "allowed_roles": ["user", "assistant"],
}


class PerplexityChatCompletionEndPoint(ChatCompletionEndPoint):

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)
