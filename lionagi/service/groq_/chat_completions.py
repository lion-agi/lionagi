from ..endpoint import ChatCompletionEndPoint


class GroqChatCompletionEndPoint(ChatCompletionEndPoint):

    provider: str = "groq"
    base_url: str = "https://api.groq.com/openai/v1"

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
            "max_completion_tokens",
            "modalities",
            "prediction",
            "audio",
            "presence_penalty",
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
