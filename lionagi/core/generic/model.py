import os
from dotenv import load_dotenv
from lionagi.libs import SysUtil, BaseService, StatusTracker

load_dotenv()


class iModel:

    def __init__(
        self,
        model: str = None,
        config: dict = {},
        provider: str = None,
        provider_schema: dict = None,
        endpoint: str = "chat/completions",
        token_encoding_name: str = "cl100k_base",
        api_key: str = None,
        api_key_schema: str = None,
        interval_tokens: int = 100_000,
        interval_requests: int = 1_000,
        interval: int = 60,
        service: BaseService = None,
        **kwargs,  # additional parameters for the model
    ):
        self.ln_id: str = SysUtil.create_id()
        self.timestamp: str = SysUtil.get_timestamp(sep=None)[:-6]
        self.endpoint = endpoint

        if isinstance(provider, type):
            provider = provider.__name__.replace("Service", "").lower()

        else:
            provider = str(provider).lower() if provider else "openai"

        from lionagi.integrations.provider._mapping import SERVICE_PROVIDERS_MAPPING

        self.provider_schema = (
            provider_schema or SERVICE_PROVIDERS_MAPPING[provider]["schema"]
        )
        self.provider = SERVICE_PROVIDERS_MAPPING[provider]["service"]
        self.endpoint_schema = self.provider_schema[endpoint]

        if api_key is not None:
            self.api_key = api_key

        elif api_key_schema is not None:
            self.api_key = os.getenv(api_key_schema)
        else:
            self.api_key = os.getenv(self.provider_schema["API_key_schema"][0])

        self.status_tracker = StatusTracker()

        self.service: BaseService = self._set_up_service(
            service=service,
            provider=self.provider,
            api_key=self.api_key,
            schema=self.provider_schema,
            token_encoding_name=token_encoding_name,
            max_tokens=interval_tokens,
            max_requests=interval_requests,
            interval=interval,
        )

        self.config = self._set_up_params(
            config or self.endpoint_schema["config"], **kwargs
        )

        if model and self.config["model"] != model:
            self.iModel_name = model
            self.config["model"] = model
            self.endpoint_schema["config"]["model"] = model

        else:
            self.iModel_name = self.config["model"]

    def update_config(self, **kwargs):
        self.config = self._set_up_params(self.config, **kwargs)

    def _set_up_config(self, model_config, **kwargs):
        return {**model_config, **kwargs}

    def _set_up_service(self, service=None, provider=None, **kwargs):
        if not service:
            provider = provider or self.provider
            return provider(**kwargs)
        return service

    def _set_up_params(self, default_config={}, **kwargs):
        params = {**default_config, **kwargs}
        allowed_params = (
            self.endpoint_schema["required"] + self.endpoint_schema["optional"]
        )

        if allowed_params != []:
            if (
                len(
                    not_allowed := [k for k in params.keys() if k not in allowed_params]
                )
                > 0
            ):
                raise ValueError(f"Not allowed parameters: {not_allowed}")

        return params

    async def call_chat_completion(self, messages, **kwargs):
        return await self.service.serve_chat(messages, **kwargs)

    def to_dict(self):
        return {
            "ln_id": self.ln_id,
            "timestamp": self.timestamp,
            "provider": self.provider.__name__.replace("Service", ""),
            "api_key": self.api_key[:4]
            + "*" * (len(self.api_key) - 8)
            + self.api_key[-4:],
            "endpoint": self.endpoint,
            "token_encoding_name": self.service.token_encoding_name,
            **self.config,
        }

    # TODO: add more endpoints
    # async def call_embedding(self, input_file, **kwargs):
    #     return await self.service.serve(input_file, "embedding", **kwargs)

    # TODO: add from_dict method
