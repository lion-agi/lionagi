from lionagi.os.service.api.base_service import BaseService
from .tokenize.token_calculator import OpenAITokenCalculator
from .model_specs.config import OAI_CONFIG

_AVAILABLE_ENDPOINTS = [
    i for i in OAI_CONFIG.keys() if i not in ["API_key_schema", "base_url"]
]


class OpenAIService(BaseService):

    base_url = OAI_CONFIG["base_url"]
    token_calculator = OpenAITokenCalculator
    available_endpoints = _AVAILABLE_ENDPOINTS
    default_endpoint = "chat/completions"
    default_provider_pricing = OPENAI_PRICING

    async def serve_chat(self, messages, **kwargs):
        return await self.chat_completion(messages, **kwargs)

    async def serve_embeddings(self, embed_str, **kwargs):
        return await self.serve(input_=embed_str, endpioint="embeddings", **kwargs)

    async def serve_finetune(self, training_file, **kwargs):
        return await self.serve(input_=training_file, endpoint="finetune", **kwargs)

    # implement serve_audio, serve_transcriptions, serve_translations
