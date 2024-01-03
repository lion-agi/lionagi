from os import getenv
import dotenv
from .base_api_service import BaseAPIService, BaseAPIRateLimiter

dotenv.load_dotenv()

class OpenAIService(BaseAPIService):

    base_url = "https://api.openai.com/v1/"

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
            api_key = api_key or getenv("OPENAI_API_KEY"),
            status_tracker = status_tracker,
            queue = queue,
            ratelimiter=ratelimiter,
            max_requests_per_minute=max_requests_per_minute, 
            max_tokens_per_minute=max_tokens_per_minute),
        self.token_encoding_name=token_encoding_name
        self.max_attempts = max_attempts

    async def serve(self, payload, endpoint_="chat/completions", method="post"):
        return await self._serve(payload=payload, endpoint_=endpoint_, method=method)
    