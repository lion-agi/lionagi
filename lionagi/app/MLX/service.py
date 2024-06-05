import re
from lionagi.os.libs.sys_util import check_import
from lionagi.services.api.ln_api import BaseService
from .configs import model


class MLXService(BaseService):
    def __init__(self, model=model, **kwargs):

        check_import("mlx_lm")
        check_import("ipywidgets")

        if model is not None and "olmo" in str(model).lower():
            check_import("olmo", pip_name="ai2-olmo")

        from mlx_lm import load, generate

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
