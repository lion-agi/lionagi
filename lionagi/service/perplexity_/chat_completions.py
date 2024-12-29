# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..endpoint import ChatCompletionEndPoint


class PerplexityChatCompletionEndPoint(ChatCompletionEndPoint):

    provider: str = "perplexity"
    base_url: str = "https://api.perplexity.ai"

    @property
    def optional_kwargs(self) -> set[str]:

        using = {
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
        }
        return using

    @property
    def allowed_roles(self):
        return ["user", "assistant"]
