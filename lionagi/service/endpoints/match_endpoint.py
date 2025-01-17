# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from .chat_completion import EndPoint


def match_endpoint(
    provider: str,
    base_url: str,
    endpoint: str,
    endpoint_params: list[str] | None = None,
) -> EndPoint:

    if endpoint in ["chat/completions", "chat", "messages"]:
        from ..providers.openai_.chat_completions import (
            OpenAIChatCompletionEndPoint,
        )

        if provider == "openai":
            return OpenAIChatCompletionEndPoint()

        if provider == "anthropic":
            from ..providers.anthropic_.messages import (
                AnthropicChatCompletionEndPoint,
            )

            return AnthropicChatCompletionEndPoint()

        if provider == "groq":
            from ..providers.groq_.chat_completions import (
                GroqChatCompletionEndPoint,
            )

            return GroqChatCompletionEndPoint()

        if provider == "perplexity":
            from ..providers.perplexity_.chat_completions import (
                PerplexityChatCompletionEndPoint,
            )

            return PerplexityChatCompletionEndPoint()

        if provider == "openrouter":
            from ..providers.openrouter_.chat_completions import (
                OpenRouterChatCompletionEndPoint,
            )

            return OpenRouterChatCompletionEndPoint()

        return OpenAIChatCompletionEndPoint(
            config={
                "provider": provider,
                "base_url": base_url,
                "endpoint": endpoint,
                "endpoint_params": endpoint_params,
            }
        )

    if provider == "exa" and endpoint == "search":
        from ..providers.exa_.search import ExaSearchEndPoint

        return ExaSearchEndPoint()

    raise ValueError(f"Unsupported endpoint: {endpoint}")
