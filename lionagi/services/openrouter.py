from os import getenv
from typing import Dict

from lionagi.services.base_api_service import BaseAPIService
from lionagi.configs.openrouter_config import openrouter_schema

class OpenRouterService(BaseAPIService):
    
    base_url = "https://openrouter.ai/api/v1"
    key_scheme: str = "OPENROUTER_API_KEY"
    default_schema: Dict = openrouter_schema['chat']
    default_endpoint: str = 'chat/completions'

    def __init__(
        self,
        api_key: str = None, 
        max_requests_per_interval=500,
        max_tokens_per_interval=150_000,
        interval=60,
        max_attempts = 3,
        ):
        
        super().__init__(
            api_key=api_key or getenv(self._key_scheme),
            max_requests_per_interval=max_requests_per_interval,
            max_tokens_per_interval=max_tokens_per_interval,
            interval=interval, 
            max_attempts=max_attempts
            )

    async def serve(
        self, 
        input_=None, 
        schema=None, 
        endpoint_=None, 
        method="post", 
        payload: Dict[str, any] =None,
        encoding_name: str = None,
        **kwargs
        ):
        
        return await self._serve(
            input_=input_,
            schema=schema or self._default_schema,
            endpoint_=endpoint_ or self._default_endpoint,
            method=method,
            payload=payload,
            encoding_name=encoding_name,
            **kwargs
        )
