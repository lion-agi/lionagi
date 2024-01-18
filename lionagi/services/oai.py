from os import getenv
from ..configs.oai_configs import oai_schema
from .base_service import BaseService, PayloadCreation

class OpenAIService(BaseService):

    base_url = "https://api.openai.com/v1/"
    available_endpoints = ['chat/completions', 'finetune', 'audio_speech', 'audio_transcriptions', 'audio_translations']
    schema = oai_schema
    key_scheme = "OPENAI_API_KEY"
    token_encoding_name = "cl100k_base"

    def __init__(self, api_key = None, key_scheme = None,schema = None, token_encoding_name: str = "cl100k_base"):
        key_scheme = key_scheme or self.key_scheme            
        super().__init__(
            api_key = api_key or getenv(key_scheme),
            schema = schema or self.schema,
            token_encoding_name=token_encoding_name
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
        if "chat/completions" not in self.active_endpoint:
            await self. init_endpoint("chat/completions")
            self.active_endpoint.append("chat/completions")
        payload = PayloadCreation.chat_completion(
            messages, self.endpoints["chat/completions"].config, self.schema["chat/completions"], **kwargs)

        try:
            completion = await self.call_api(payload, "chat/completions", "post")
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
    
    # async def serve_finetune(self, training_file):
    #     return await self.serve(input_=training_file, endpoint="finetune")
    
"""
from lionagi.services import OpenAIService

service = OpenAIService()
await service.initiate_endpoint('chat/completions', max_tokens)

await service.serve_chat(input)
service.serve_finetuning
service.serve_audio_speech(input, method='')

"""