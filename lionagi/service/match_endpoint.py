# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from .endpoint import EndPoint


def match_endpoint(
    provider: str,
    base_url: str,
    endpoint: str,
    endpoint_params: list[str] | None = None,
) -> EndPoint:
    if endpoint not in ["chat/completions", "chat", "messages"]:
        raise ValueError(
            "Invalid endpoint, must be one of 'chat/completions' (openai compatible), 'chat' (an alias), 'messages' (anthropic), other endpoints are not supported yet"
        )

    if provider == "openai":
        from .openai_.chat_completions import OpenAIChatCompletionEndPoint

        return OpenAIChatCompletionEndPoint()

    if provider == "anthropic":
        from .anthropic_.messages import AnthropicChatCompletionEndPoint

        return AnthropicChatCompletionEndPoint()

    if provider == "groq":
        from .groq_.chat_completions import GroqChatCompletionEndPoint

        return GroqChatCompletionEndPoint()

    if provider == "perplexity":
        from .perplexity_.chat_completions import (
            PerplexityChatCompletionEndPoint,
        )

        return PerplexityChatCompletionEndPoint()

    return OpenAIChatCompletionEndPoint(
        provider=provider,
        base_url=base_url,
        endpoint=endpoint,
        endpoint_params=endpoint_params,
    )
