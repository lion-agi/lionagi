from os import getenv
from typing import Type
from pydantic import BaseModel
from aiocache import cached

from lionagi.os.file.tokenize.token_calculator import ProviderTokenCalculator
from lionagi.os.service.schema import ModelConfig, EndpointSchema
from lionagi.os.service.endpoint import EndPoint
from lionagi.os.service.config import RETRY_CONFIG, CACHED_CONFIG

from lionagi.os.primitives import Log


class ProviderConfig(BaseModel):
    api_key_schema: str
    provider: str
    base_url: str


class ProviderService:

    default_endpoint = "chat/completions"
    config: ProviderConfig = None
    token_calculator: Type[ProviderTokenCalculator] = None
    endpoint_config: dict[str, EndpointSchema] = None  # endpoint: EndpointSchema
    model_specification: dict[str, ModelConfig] = None  # model_name: ModelConfig

    def __init__(
        self,
        *,
        token_calculator: Type[ProviderTokenCalculator] = None,
        config: ProviderConfig = None,
        model_specification: dict[str, ModelConfig] = None,
        endpoint_config=None,
        api_key=None,
        api_key_schema=None,
    ):
        self.token_calculator = token_calculator
        self.config = config
        self.model_specification = model_specification
        self.endpoint_config = endpoint_config
        self.active_endpoints: dict[str, EndPoint] = {}  # endpoint: EndPoint

        self.api_key = api_key
        if api_key_schema:
            if getenv(api_key_schema, None) is None:
                raise ValueError(
                    f"API key schema {api_key_schema} not found in environment"
                )
            self.config = self.config.model_copy()
            self.config.api_key_schema = api_key_schema
        if self.api_key is None:
            self.api_key = getenv(self.config.api_key_schema)

    def add_endpoint(
        self,
        *,
        endpoint,
        model=None,
        schema: EndpointSchema | None = None,  # priority 1
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        refresh_time: float = 1,
        rate_limiter=None,
    ):
        if not schema:
            if model:
                schema = self.model_specification[model].endpoint_schema[endpoint]
            else:
                schema = self.endpoint_config[endpoint]

        endpoint_ = EndPoint(
            schema=schema,
            rate_limiter=rate_limiter,
            interval=interval,
            interval_request=interval_request,
            interval_token=interval_token,
            refresh_time=refresh_time,
            token_calculator=self.token_calculator[schema.endpoint],
        )

        self.active_endpoints[endpoint] = endpoint_

    async def serve(
        self,
        *,
        endpoint=None,
        input_=None,
        schema: EndpointSchema = None,
        payload: dict = None,
        method="post",
        retry_config=None,
        api_key_schema=None,  # priority 2
        api_key=None,  # priority 1
        cached=False,
        _parse_func=None,
        **kwargs,
    ) -> Log:
        endpoint = endpoint or self.default_endpoint

        if not endpoint in self.active_endpoints:
            self.add_endpoint(endpoint=endpoint)

        if _parse_func:
            input_ = _parse_func(input_)

        payload = self.active_endpoints[endpoint].schema.create_payload(input_=input_)

        if cached:
            return await self._cached_serve(
                endpoint=endpoint,
                schema=schema,
                payload=payload,
                method=method,
                retry_config=retry_config,
                api_key_schema=api_key_schema,
                api_key=api_key,
                **kwargs,
            )
        return await self._serve(
            endpoint=endpoint,
            schema=schema,
            payload=payload,
            method=method,
            retry_config=retry_config,
            api_key_schema=api_key_schema,
            api_key=api_key,
            **kwargs,
        )

    async def _serve(
        self,
        *,
        endpoint=None,
        schema: EndpointSchema = None,
        payload: dict = None,
        method="post",
        retry_config=RETRY_CONFIG,
        api_key_schema=None,  # priority 2
        api_key=None,  # priority 1
        **kwargs,
    ) -> Log:
        if not endpoint in self.active_endpoints:
            self.add_endpoint(endpoint, schema=schema)

        api_key = api_key or self.api_key
        if not api_key:
            api_key = getenv(api_key_schema or self.config.api_key_schema)

        return await self.active_endpoints[endpoint].serve(
            payload=payload,
            base_url=self.config.base_url,
            api_key=api_key,
            method=method,
            retry_config=retry_config,
            **kwargs,
        )

    @cached(**CACHED_CONFIG)
    async def _cached_serve(
        self,
        *,
        endpoint="chat/completions",
        schema: EndpointSchema = None,
        payload: dict = None,
        method="post",
        retry_config=RETRY_CONFIG,
        api_key_schema=None,  # priority 2
        api_key=None,  # priority 1
        **kwargs,
    ) -> Log:

        return await self._serve(
            endpoint=endpoint,
            schema=schema,
            payload=payload,
            method=method,
            retry_config=retry_config,
            api_key_schema=api_key_schema,
            api_key=api_key,
            **kwargs,
        )

    async def serve_chat(self, messages, **kwargs):
        return await self.serve(
            input_=messages,
            endpoint="chat/completions",
            _parse_func=self.prepare_chat_input,
            **kwargs,
        )

    # override this method for different providers
    @classmethod
    def prepare_chat_input(cls, messages):
        """openai standard with optional image processing"""
        msgs = []

        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content")
                if isinstance(content, (dict, str)):
                    msgs.append({"role": msg["role"], "content": content})
                elif isinstance(content, list):
                    _content = []
                    for i in content:
                        if "text" in i:
                            _content.append({"type": "text", "text": str(i["text"])})
                        elif "image_url" in i:
                            _content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"{i['image_url'].get('url')}",
                                        "detail": i["image_url"].get("detail", "low"),
                                    },
                                }
                            )
                    msgs.append({"role": msg["role"], "content": _content})

        return msgs
