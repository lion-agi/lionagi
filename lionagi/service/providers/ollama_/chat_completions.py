from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

CHAT_COMPLETION_CONFIG = {
    "provider": "ollama",
    "base_url": "http://localhost:11434/api",
    "endpoint": "chat",
    "method": "post",
    "openai_compatible": False,
    "is_invokeable": True,
    "requires_tokens": True,
    "is_streamable": True,
    "required_kwargs": {
        "messages",         # ["role", "content", "images", "tool_calls"]   # tool_call ["function", "arguments"]
        "model",
    },
    "optional_kwargs": {
        "tools",
        "format",
        "options",      # .models.GenerateOptions
        "stream",
        "keep_alive",
    },
    "allowed_roles": ["user", "assistant", "system", "tools"],
}


class OllamaChatCompletionEndpoint(ChatCompletionEndPoint):
    """
    documentation: https://github.com/ollama/ollama/blob/main/docs/api.md
    """
    
    def __init__(self, config: dict=CHAT_COMPLETION_CONFIG):
        super().__init__(config)
    
    def create_payload(self, **kwargs) -> dict:
        payload = {}

        
        is_cached = kwargs.get("is_cached", False)
        for k, v in kwargs.items():
            if k in self.acceptable_kwargs:
                payload[k] = v
        return {
            "payload": payload,
            "headers": {},
            "is_cached": is_cached,
        }