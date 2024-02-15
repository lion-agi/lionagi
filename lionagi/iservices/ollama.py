from ..utils.sys_util import install_import, is_package_installed
from .base_service import BaseService

class OllamaService(BaseService):
    def __init__(self, model: str = None, **kwargs):
        super().__init__()
        
        try: 
            if not is_package_installed('ollama'):
                install_import(
                    package_name='ollama',
                    import_name='Client'
                )
            import ollama    
            self.ollama = ollama
        except:
            raise ImportError(f'Unable to import required module from ollama. Please make sure that ollama is installed.')
        
        self.model = model
        self.client = self.ollama.AsyncClient(**kwargs)

    async def serve_chat(self, messages, **kwargs):
        self.ollama.pull(self.model)
        payload = {'messages': messages}

        try:
            completion = await self.client.chat(model=self.model, messages=messages, **kwargs)
            completion['choices'] = [{'message': completion.pop('message')}]
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
        