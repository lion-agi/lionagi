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

# TODO: add support for other litellm features in cost management and UI

class LiteLLMService(BaseService):
    def __init__(self, model: str = None, use_proxy=False, **kwargs):
        super().__init__()

        from lionagi.libs.sys_util import SysUtil
        
        if use_proxy:
            SysUtil.check_import("litellm['proxy']")
            import subprocess
            command = ['litellm', '--model', 'huggingface/bigcode/starcoder']
            subprocess.run(command)
            
            SysUtil.check_import("openai")
            import openai
            
            client = openai.OpenAI(api_key="anything",base_url="http://0.0.0.0:4000") # set proxy to base_url
            # request sent to model set on litellm proxy, `litellm --model`
            self.acompletion = client.chat.completions.create
        else:
            from litellm import acompletion
            self.acompletion= acompletion
            
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

        try:
            completion = await self.acompletion(
                model=self.model, messages=messages, **kwargs
            )
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
