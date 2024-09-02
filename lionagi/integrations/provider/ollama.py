from lionagi.libs.ln_api import BaseService
from lionagi.integrations.config.ollama_configs import model

allowed_kwargs = [
    "model",
    "frequency_penalty",
    # "max_tokens",
    "n",
    "presence_penalty",
    "response_format",
    "seed",
    "stop",
    "stream",
    # "temperature",
    "top_p",
    "tools",
    "tool_choice",
    "user",
]

from typing_extensions import deprecated

from lionagi.os.sys_utils import format_deprecated_msg


@deprecated(
    format_deprecated_msg(
        deprecated_name="lionagi.core.action.function_calling.FunctionCalling",
        deprecated_version="v0.3.0",
        removal_version="v1.0",
        replacement="check `lion-core` package for updates",
    ),
    category=DeprecationWarning,
)
class OllamaService(BaseService):

    def __init__(self, model: str = model, **kwargs):
        super().__init__()

        from lionagi.libs.sys_util import SysUtil

        SysUtil.check_import("ollama")

        import ollama

        self.ollama = ollama
        self.model = model
        self.client = self.ollama.AsyncClient()
        self.allowed_kwargs = allowed_kwargs

    async def serve_chat(self, messages, **kwargs):
        config = {}
        for k, v in kwargs.items():
            if k in allowed_kwargs:
                config[k] = v

        self.ollama.pull(self.model)
        payload = {"messages": messages}
        if "model" not in config:
            config["model"] = self.model

        try:
            completion = await self.client.chat(messages=messages, **config)
            completion["choices"] = [{"message": completion.pop("message")}]
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
