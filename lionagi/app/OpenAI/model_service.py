from lionagi.os.service.api.base_service import BaseService


class OpenAIService(BaseService):

    default_endpoint = "chat/completions"

    async def serve_chat(self, messages, **kwargs):
        return await self.chat_completion(messages, **kwargs)

    async def serve_embeddings(self, embed_str, **kwargs):
        return await self.serve(input_=embed_str, endpioint="embeddings", **kwargs)

    async def serve_finetune(self, training_file, **kwargs):
        return await self.serve(input_=training_file, endpoint="finetune", **kwargs)

    # implement serve_audio, serve_transcriptions, serve_translations
