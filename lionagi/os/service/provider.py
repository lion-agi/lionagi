from os import getenv

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

    config: ProviderConfig = None
    token_calculator: ProviderTokenCalculator = None
    endpoint_config: dict[str, EndpointSchema] = None  # endpoint: EndpointSchema
    model_specification: dict[str, ModelConfig] = None  # model_name: ModelConfig
    active_endpoints: dict[str, EndPoint] = {}  # endpoint: EndPoint

    def __init__(
        self,
        token_calculator: ProviderTokenCalculator = None,
        config: ProviderConfig = None,
        model_specification: dict[str, ModelConfig] = None,
    ):
        self.token_calculator = token_calculator
        self.endpoint_config = config
        self.model_specification = model_specification

    def add_endpoint(
        self,
        *,
        endpoint="chat/completions",
        schema: EndpointSchema | None = None,  # priority 1
        interval: int | None = None,
        interval_request: int | None = None,
        interval_token: int | None = None,
        refresh_time: float = 1,
    ):
        if not schema:
            schema = self.endpoint_config[endpoint]

        endpoint_ = EndPoint(
            schema=schema,
            rate_limiter=None,
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
        endpoint="chat/completions",
        schema: EndpointSchema = None,
        payload: dict = None,
        method="post",
        retry_config=RETRY_CONFIG,
        api_key_schema=None,  # priority 2
        api_key=None,  # priority 1
        cached=False,
    ) -> Log:
        if cached:
            return await self._cached_serve(
                endpoint=endpoint,
                schema=schema,
                payload=payload,
                method=method,
                retry_config=retry_config,
                api_key_schema=api_key_schema,
                api_key=api_key,
            )
        return await self._serve(
            endpoint=endpoint,
            schema=schema,
            payload=payload,
            method=method,
            retry_config=retry_config,
            api_key_schema=api_key_schema,
            api_key=api_key,
        )

    async def _serve(
        self,
        *,
        endpoint="chat/completions",
        schema: EndpointSchema = None,
        payload: dict = None,
        method="post",
        retry_config=RETRY_CONFIG,
        api_key_schema=None,  # priority 2
        api_key=None,  # priority 1
    ) -> Log:
        if not endpoint in self.active_endpoints:
            self.add_endpoint(endpoint, schema=schema)

        return await self.active_endpoints[endpoint].serve(
            payload=payload,
            base_url=self.config.base_url,
            api_key=api_key or getenv(api_key_schema or self.config.api_key_schema),
            method=method,
            retry_config=retry_config,
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
    ) -> Log:

        return await self._serve(
            endpoint=endpoint,
            schema=schema,
            payload=payload,
            method=method,
            retry_config=retry_config,
            api_key_schema=api_key_schema,
            api_key=api_key,
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