from os import getenv
from ..configs.openrouter_configs import openrouter_schema
from .base_service import BaseService

class OpenAIService(BaseService):
    base_url = "https://openrouter.ai/api/v1/"
    key_scheme = "OPENROUTER_API_KEY"
    available_endpoints = ['chat/completions']
    schema = openrouter_schema

    def __init__(self, api_key = None,api_key_scheme = None,schema = None):
        
        if api_key or api_key_scheme:
            api_key = api_key or getenv(api_key_scheme)
            
        super().__init__(
            api_key = api_key or getenv("OPENAI_API_KEY"),
            schema = schema or self.schema
        )

    async def serve(self, input_, endpoint="chat/completions", method="post"):
        return await self._serve(input_=input_, endpoint=endpoint, method=method)
    
    