from os import getenv
from dotenv import load_dotenv
load_dotenv()

from .base_service import BaseAPIService, BaseAPIRateLimiter

class OpenAIService(BaseAPIService):
    base_url: str = "https://api.openai.com/v1/"
    _key_scheme: str = "OPENAI_API_KEY"

    def __init__(
        self,
        api_key: str = None,
        token_encoding_name: str = "cl100k_base",
        max_attempts: int = 3,
        max_requests_per_minute: int = 500,
        max_tokens_per_minute: int = 150_000,
        ratelimiter = BaseAPIRateLimiter ,
        status_tracker = None,
        queue = None,
    ):
        super().__init__(
            api_key = api_key or getenv(self._key_scheme),
            status_tracker = status_tracker,
            queue = queue,
            ratelimiter=ratelimiter,
            max_requests_per_minute=max_requests_per_minute, 
            max_tokens_per_minute=max_tokens_per_minute),
        self.token_encoding_name=token_encoding_name
        self.max_attempts = max_attempts



    async def serve(self, payload, endpoint_="chat/completions", method="post"):
        return await self._serve(payload=payload, endpoint_=endpoint_, method=method)

    async def serve_ChatCompletion(self, payload):
        return
















    
    async def 








