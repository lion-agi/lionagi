from ..utils.sys_util import install_import, is_package_installed
from .base_service import BaseService


class LiteLLMService(BaseService):
    def __init__(self, model: str = None, **kwargs):
        super().__init__()

        try: 
            if not is_package_installed('litellm'):
                install_import(
                    package_name='litellm',
                    import_name='acompletion'
                )
            from litellm import acompletion 
            self.acompletion = acompletion
        except:
            raise ImportError(f'Unable to import required module from ollama. Please make sure that ollama is installed.')
        
        self.model = model
        self.kwargs = kwargs

    async def serve_chat(self, messages, **kwargs):
        payload = {'messages': messages}
        kwargs = {**self.kwargs, **kwargs}

        try:
            completion = await self.acompletion(model=self.model, messages=messages, **kwargs)
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
        