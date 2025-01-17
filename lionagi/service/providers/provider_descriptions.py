# This dictionary can be stored in a separate file or in the code:
PROVIDER_DESCRIPTIONS = {
    "openai": {
        "description": (
            "OpenAI is a provider that supports 'chat' and 'completions' endpoints. "
            "Use 'chat' for ChatCompletion calls (like GPT-3.5, GPT-4). "
            "Use 'completions' for the older text completion API."
        ),
        "endpoints": {
            "chat": "Runs ChatCompletion calls, best for conversation-based or multi-turn Q&A.",
            "completions": "Runs text completion calls for older GPT-3 style usage."
        }
    },
    "anthropic": {
        "description": (
            "Anthropic offers Claude-based models, typically called via a 'messages' endpoint. "
            "It's used for chat or conversation-like requests."
        ),
        "endpoints": {
            "messages": "Handles Anthropics's chat-like conversation with Claude."
        }
    },
    "perplexity": {
        "description": (
            "Perplexity is a search-based model that offers 'chat' or 'completions', "
            "often returning summaries and reference URLs from the web."
        ),
        "endpoints": {
            "chat": "Chat-based interface with integrated search results and links.",
            "completions": "Text completion interface, typically includes summarized web references."
        }
    },
    "openrouter": {
        "description": (
            "OpenRouter is a multi-provider interface that typically supports 'chat' "
            "and 'completions' endpoints as a drop-in replacement for OpenAI or others."
        ),
        "endpoints": {
            "chat": "Similar to OpenAI's ChatCompletion interface.",
            "completions": "Similar to OpenAI's Completions interface."
        }
    },
    "exa": {
        "description": (
            "Exa is a specialized 'search' provider that can return relevant links, "
            "highlights, and source URLs. Great for retrieval or knowledge-based tasks."
        ),
        "endpoints": {
            "search": "Search with Exa's advanced retrieval. Returns links, highlights, and sources."
        }
    }
}