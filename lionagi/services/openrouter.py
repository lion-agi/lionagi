from os import getenv
from .base_api_service import BaseAPIService, BaseAPIRateLimiter

class OpenRouterService(BaseAPIService):
    _key_scheme = "OPENROUTER_API_KEY"

    base_url = "https://openrouter.ai/api/v1/"

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
        
    async def serve(self, payload, endpoint_="chat/completions"):
        return await self._serve(payload=payload, endpoint_=endpoint_)
    