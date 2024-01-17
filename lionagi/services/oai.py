from os import getenv
from ..configs.oai_configs import oai_schema
from .base_service import BaseService

class OpenAIService(BaseService):

    base_url = "https://api.openai.com/v1/"
    available_endpoints = ['chat/completions', 'finetune', 'audio_speech', 'audio_transcriptions', 'audio_translations']
    schema = oai_schema
    key_scheme = "OPENAI_API_KEY"

    def __init__(self, api_key = None, key_scheme = None,schema = None):
        key_scheme = key_scheme or self.key_scheme            
        super().__init__(
            api_key = api_key or getenv(key_scheme),
            schema = schema or self.schema
        )

    async def serve(self, input_, endpoint="chat/completions", method="post"):
        await self._init()
        return await self._serve(input_=input_, endpoint=endpoint, method=method)
    
    async def serve_chat(self, messages):
        return await self.serve(input_=messages)
    
    async def serve_finetune(self, training_file):
        return await self.serve(input_=training_file, endpoint="finetune")
    