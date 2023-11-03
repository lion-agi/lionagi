import os
from .SyncService import SyncAPIService
from .AsyncService import AsyncAPIService

async_api_service = AsyncAPIService(
    api_key=os.getenv("OPENAI_API_KEY"),
    max_requests_per_minute=500, 
    max_tokens_per_minute=10000,
    token_encoding_name="cl100k_base",
    max_attempts=3
)

sync_api_service = SyncAPIService(
    api_key=os.getenv("OPENAI_API_KEY"),
    max_requests_per_minute=500,
    max_tokens_per_minute=10000,
    token_encoding_name="cl100k_base",
    max_attempts=3
)