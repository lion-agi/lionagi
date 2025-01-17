from .models import OpenAIChatCompletionOptions, OpenAIChatCompletionRequest, OpenAIChatRole
from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

CHAT_COMPLETION_CONFIG = {
    "provider": "openai",
    "base_url": "https://api.openai.com/v1",
    "endpoint": "chat/completions",
    "method": "post",
    "openai_compatible": True,
    "is_invokeable": True,
    "requires_tokens": True,
    "is_streamable": True,
    "required_kwargs": set(OpenAIChatCompletionRequest.model_fields.keys()) - {"options"},
    "deprecated_kwargs": {
        "max_tokens",
        "function_call",
        "functions",
    },
    "optional_kwargs": set(OpenAIChatCompletionOptions.model_fields.keys()),
    "allowed_roles": {i.value for i in OpenAIChatRole.__members__.values()},
    "request_model": OpenAIChatCompletionRequest,
}

class OpenAIChatCompletionEndPoint(ChatCompletionEndPoint):
    """
    Documentation: https://platform.openai.com/docs/api-reference/chat/create
    """

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)
