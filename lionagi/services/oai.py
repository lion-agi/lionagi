from os import getenv
from ..configs.oai_configs import oai_schema
from .base_service import BaseService, PayloadCreation

class OpenAIService(BaseService):
    """A service to interact with OpenAI's API endpoints.

    Attributes:
        base_url (str): The base URL for the OpenAI API.
        available_endpoints (list): A list of available API endpoints.
        schema (dict): The schema configuration for the API.
        key_scheme (str): The environment variable name for OpenAI API key.
        token_encoding_name (str): The default token encoding scheme.

    Examples:
        >>> service = OpenAIService(api_key="your_api_key")
        >>> asyncio.run(service.serve("Hello, world!", "chat/completions"))
        (payload, completion)

        >>> service = OpenAIService()
        >>> asyncio.run(service.serve("Convert this text to speech.", "audio_speech"))
        ValueError: 'audio_speech' is currently not supported
    """

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
