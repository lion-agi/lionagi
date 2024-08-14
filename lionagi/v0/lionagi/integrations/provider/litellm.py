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

        import litellm

        litellm.drop_params = True

        self.acompletion = litellm.acompletion
        self.model = model
        self.kwargs = kwargs
        self.allowed_kwargs = allowed_kwargs

    async def serve_chat(self, messages, **kwargs):
        payload = {"messages": messages}
        config = {}
        for k, v in kwargs.items():
            if k in self.allowed_kwargs:
                config[k] = v

        kwargs = {**self.kwargs, **config}
        kwargs["model"] = self.model or kwargs.get("model")

        try:
            completion = await self.acompletion(messages=messages, **kwargs)
            return payload, completion.model_dump()
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
