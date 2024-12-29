# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from ..openai_.chat_completions import OpenAIChatCompletionEndPoint


class OpenRouterChatCompletionEndPoint(OpenAIChatCompletionEndPoint):
    """
    Documentation: https://openrouter.ai/docs/quick-start#quick-start
    """

    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
