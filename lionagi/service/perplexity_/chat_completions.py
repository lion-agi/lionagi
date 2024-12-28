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
