import re

import lionagi.libs.ln_convert as convert
from lionagi.integrations.config.mlx_configs import model
from lionagi.libs.ln_api import BaseService
from lionagi.libs.sys_util import SysUtil


class MLXService(BaseService):
    def __init__(self, model=model, **kwargs):

        SysUtil.check_import("mlx_lm")
        SysUtil.check_import("ipywidgets")

        if model is not None and "olmo" in str(model).lower():
            SysUtil.check_import("olmo", pip_name="ai2-olmo")

        from mlx_lm import generate, load

        super().__init__()

        model_, tokenizer = load(model, **kwargs)

        self.model_name = model
        self.model = model_
        self.tokenizer = tokenizer
        self.generate = generate
        self.allowed_kwargs = []

    async def serve_chat(self, messages, **kwargs):
        if "verbose" not in kwargs.keys():
            verbose = False

        prompts = [msg["content"] for msg in messages if msg["role"] == "user"]

        payload = {"messages": messages}

        try:
            response = self.generate(
                self.model,
                self.tokenizer,
                prompt=f"{prompts[-1]} \nOutput: ",
                verbose=verbose,
            )
            if "```" in response:
                regex = re.compile(r"```[\s\S]*?```")
                matches = regex.findall(response)
                msg = matches[0].strip("```")
                completion = {"choices": [{"message": {"content": msg}}]}
            else:
                completion = {"choices": [{"message": {"content": response}}]}
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
