from lionagi.util import to_dict
from lionagi.util.api_util import BaseService

from lionagi.integrations.config.mlx_configs import model


class MlXService(BaseService):
    def __init__(self, model=model, **kwargs):

        from lionagi.util.import_util import ImportUtil

        ImportUtil.check_import("mlx_lm")

        from mlx_lm import load, generate

        super().__init__()

        model_, tokenizer = load(model, **kwargs)

        self.model_name = model
        self.model = model_
        self.tokenizer = tokenizer
        self.generate = generate

    async def serve_chat(self, messages, **kwargs):
        if 'verbose' not in kwargs.keys():
            verbose=True
            
        prompts = [
            to_dict(msg["content"])["instruction"]
            for msg in messages
            if msg["role"] == "user"
        ]

        payload = {"messages": messages}

        try:
            response = self.generate(
                self.model, self.tokenizer, prompt=f"{prompts[-1]} \nOutput: ", verbose=verbose
            )
            completion = {"model": self.model_name, "choices": [{"message": response}]}

            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
