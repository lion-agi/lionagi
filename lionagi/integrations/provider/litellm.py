from lionagi.util.sys_util import SysUtil
from lionagi.util.api_util import BaseService


class LiteLLMService(BaseService):
    def __init__(self, model: str = None, **kwargs):
        super().__init__()

        from lionagi.util.import_util import ImportUtil

        ImportUtil.check_import("litellm")

        from litellm import acompletion

        self.acompletion = acompletion
        self.model = model
        self.kwargs = kwargs

    async def serve_chat(self, messages, **kwargs):
        payload = {"messages": messages}
        kwargs = {**self.kwargs, **kwargs}

        try:
            completion = await self.acompletion(
                model=self.model, messages=messages, **kwargs
            )
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
