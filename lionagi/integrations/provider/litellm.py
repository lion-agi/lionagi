from lionagi.libs.ln_api import BaseService

allowed_kwargs = [
    "model",
    "frequency_penalty",
    "max_tokens",
    "n",
    "presence_penalty",
    "response_format",
    "seed",
    "stop",
    "stream",
    "temperature",
    "top_p",
    "tools",
    "tool_choice",
    "user",
]


class LiteLLMService(BaseService):
    def __init__(self, model: str = None, **kwargs):
        super().__init__()

        from lionagi.libs.sys_util import SysUtil

        SysUtil.check_import("litellm")

        from litellm import acompletion

        self.acompletion = acompletion
        self.model = model
        self.kwargs = kwargs

    async def serve_chat(self, messages, **kwargs):
        payload = {"messages": messages}
        config = {}
        for k, v in kwargs.items():
            if k in allowed_kwargs:
                config[k] = v

        kwargs = {**self.kwargs, **config}

        try:
            completion = await self.acompletion(
                model=self.model, messages=messages, **kwargs
            )
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
