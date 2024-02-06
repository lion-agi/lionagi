from litellm import acompletion

from .base_service import BaseService

class LiteLLMService(BaseService):
    def __init__(self, model: str = None, **kwargs):
        super().__init__()
        self.model = model
        self.kwargs = kwargs

    async def serve_chat(self, messages, **kwargs):
        payload = {'messages': messages}
        kwargs = {**self.kwargs, **kwargs}

        try:
            completion = await acompletion(model=self.model, messages=messages, **kwargs)
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e