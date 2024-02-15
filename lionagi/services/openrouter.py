from os import getenv
from ..configs.openrouter_configs import openrouter_schema
from .base_service import BaseService, PayloadCreation

class OpenRouterService(BaseService):
    base_url = "https://openrouter.ai/api/v1/"
    available_endpoints = ['chat/completions']
    schema = openrouter_schema
    key_scheme = "OPENROUTER_API_KEY"
    token_encoding_name = "cl100k_base"
    
    
    def __init__(self, api_key = None, key_scheme = None,schema = None, token_encoding_name: str = "cl100k_base", **kwargs):
        key_scheme = key_scheme or self.key_scheme            
        super().__init__(
            api_key = api_key or getenv(key_scheme),
            schema = schema or self.schema,
            token_encoding_name=token_encoding_name, **kwargs
        )
        self.active_endpoint = []

    async def serve(self, input_, endpoint="chat/completions", method="post", **kwargs):
        if endpoint not in self.active_endpoint:
            await self. init_endpoint(endpoint)
        if endpoint == "chat/completions":
            return await self.serve_chat(input_, **kwargs)
        else:
            return ValueError(f'{endpoint} is currently not supported')
    
    async def serve_chat(self, messages, **kwargs):
        endpoint = "chat/completions"
        
        if endpoint not in self.active_endpoint:
            await self. init_endpoint(endpoint)
            self.active_endpoint.append(endpoint)
        payload = PayloadCreation.chat_completion(
            messages, self.endpoints[endpoint].config, self.schema[endpoint], **kwargs)

        try:
            completion = await self.call_api(payload, endpoint, "post")
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e