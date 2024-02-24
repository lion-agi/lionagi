from lionagi.util.api_util import BaseService
from lionagi.integrations.config.ollama_configs import model

class OllamaService(BaseService):
    
    def __init__(self, model: str = model, **kwargs):
        super().__init__()
        
        from lionagi.util.import_util import ImportUtil
        ImportUtil.check_import('ollama')
        
        import ollama    

        self.ollama = ollama
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
        