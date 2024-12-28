from ..openai_.chat_completions import OpenAIChatCompletionEndPoint


class OpenRouterChatCompletionEndPoint(OpenAIChatCompletionEndPoint):
    """
    Documentation: https://openrouter.ai/docs/quick-start#quick-start
    """

    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
