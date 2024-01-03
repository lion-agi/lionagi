from os import getenv
from typing import Dict

from .base_api_service import BaseAPIService
from lionagi.objs import PayloadMaker
from lionagi.configs.oai_configs import oai_schema


class OpenAIService(BaseAPIService):
    base_url: str = "https://api.openai.com/v1/"
    key_schema: str = "OPENAI_API_KEY"
    default_schema: Dict = oai_schema['chat']
    default_endpoint: str = 'chat/completions'
    
    def __init__(
        self,
        api_key: str = None, 
        max_requests_per_interval=500,
        max_tokens_per_interval=150_000,
        interval=60,
        max_attempts = 3,
        encoding_name: str="cl100k_base",
        schema=None
        
        ):
        
        super().__init__(
            api_key=api_key or getenv(self.key_schema),
            max_requests_per_interval=max_requests_per_interval,
            max_tokens_per_interval=max_tokens_per_interval,
            interval=interval, 
            max_attempts=max_attempts
            )
        
        self.payload_maker = PayloadMaker(encoding_name=encoding_name)


    def create_payload(self, input_, schema = None, **kwargs):
        payload = self.payload_maker.make(input_=input_, schema=schema, **kwargs) 
        return payload

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
        
        if not payload: 
            payload = self.create_payload(input_=input_, schema=schema, **kwargs)
        
        return await self._serve(
            input_=input_,
            schema=schema or self.default_schema,
            endpoint_=endpoint_ or self.default_endpoint,
            method=method,
            payload=payload,
            encoding_name=encoding_name,
            **kwargs
        )
