import os
from pydantic import BaseModel

from lionagi.service.endpoints.chat_completion import ChatCompletionEndPoint

CHAT_COMPLETION_CONFIG = {
    "provider": "gemini",
    "base_url": "https://generativelanguage.googleapis.com/v1beta",
    "endpoint": "models/{model}/generateContent?key=${api_key}",
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
        "max_output_tokens",
        "stream",
        "tools",
        "tool_config",
        "response_format",
        "n",
        "stop",
        "response_mime_type",
        "safety_settings",
    },
    "allowed_roles": ["user", "assistant", "system"],
    "invoke_with_endpoint": True,
}


class GeminiChatCompletionEndPoint(ChatCompletionEndPoint):

    def __init__(self, config: dict = CHAT_COMPLETION_CONFIG):
        super().__init__(config)
        
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GENERATIVEAI_API_KEY"))
        self._genai = genai

    def create_payload(self, **kwargs) -> dict:
        dict_ = super().create_payload(**kwargs)
        
        history: list = dict_["payload"]["messages"]
        msg = history[-1]["content"]
        sys_ = None
        history_ = []
        
        if history[0]["role"] == "system":
            sys_ = history[0]["content"]
            history = history[1:]
        
        for i in history[:-1]:
            if i["role"] == "assistant":
                i["role"] = "model"
            i["parts"] = i.pop("content")
            history_.append(i)
            
        model_config = {}
        model_config["model_name"] = dict_["payload"]["model"]
        model_config["generation_config"] = {
            k:v for k, v in dict_["payload"].items() if k in ["temperature", "top_p", "top_k", "max_output_tokens", "response_mime_type"]
        }
        model_config["generation_config"]["response_mime_type"] = model_config["generation_config"].get("response_mime_type", "text/plain")
        
        for i in ("safety_settings", "tool_config", "tools"):
            if i in dict_["payload"]:
                model_config[i] = dict_["payload"][i]
        if sys_:
            model_config["system_instruction"] = sys_
        if "safety_settings" in dict_["payload"]:
            model_config["safety_settings"] = dict_["payload"]["safety_settings"]

        
        
        model = self._genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config,
            tools='code_execution',
        )
        
        
        
        
        
        
        
        
        
        

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











# Create the model
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 65536,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-thinking-exp-01-21",
  generation_config=generation_config,
  tools='code_execution',
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)


    def create_payload(self, **kwargs) -> dict:
        ...











    async def _invoke(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        try:
            import google.generativeai as genai
        except ImportError:
            from lionagi.utils import run_package_manager_command
            run_package_manager_command(["pip", "install", "google-generativeai"])

        return await super()._invoke(payload, headers, **kwargs)

    async def _stream(
        self,
        payload: dict,
        headers: dict,
        **kwargs,
    ):
        try:
            import google.generativeai as genai
        except ImportError:
            from lionagi.utils import run_package_manager_command
            run_package_manager_command(["pip", "install", "google-generativeai"])
            
        async for i in super()._stream(payload, headers, **kwargs):
            yield i