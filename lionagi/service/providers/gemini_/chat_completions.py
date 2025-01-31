from pydantic import BaseModel

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

CHAT_COMPLETION_CONFIG = {
    "provider": "gemini",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/",
    "endpoint": "/models/{model}/generateContent?key=${api_key}",
    "method": "post",
    "openai_compatible": False,
    "is_invokeable": True,
    "requires_tokens": True,
    "is_streamable": True,
    "required_kwargs": {
        "messages",
        "model",
    },
    "optional_kwargs": {
        "temperature",
        "top_p",
        "max_tokens",
        "stream",
        "tools",
        "tool_choice",
        "response_format",
        "n",
        "stop",
    },
    "allowed_roles": ["user", "assistant", "system"],
    "invoke_with_endpoint": True,
}


class GeminiChatCompletionEndPoint(ChatCompletionEndPoint):

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)

    def create_payload(self, **kwargs) -> dict:
        dict_ = super().create_payload(**kwargs)

        for k, v in dict_["payload"].items():
            if k == "response_format":
                if isinstance(v, type) and issubclass(v, BaseModel):
                    dict_["payload"]["response_format"] = {
                        "type": "json_object",
                        "response_schema": v.model_json_schema(),
                    }
                elif isinstance(v, dict):
                    dict_["payload"]["response_format"] = {
                        "type": "json_object",
                        "response_schema": v,
                    }

        return dict_

    async def _invoke(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        from lionagi.libs.package.imports import check_import

        check_import("google.generativeai", pip_name="google-generativeai")

        return await super()._invoke(payload, headers, **kwargs)

    async def _stream(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        from lionagi.libs.package.imports import check_import

        check_import("google.generativeai", pip_name="google-generativeai")

        async for i in super()._stream(payload, headers, **kwargs):
            yield i
