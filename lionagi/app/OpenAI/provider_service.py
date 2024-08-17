import os
from lionagi.os.service.provider import ProviderConfig, ProviderService
from .tokenize.token_calculator import OpenAITokenCalculator
from .model_specs.model_specifications import OAI_MODEL_SPECIFICATIONS
from .model_specs._config import OAI_CONFIG


OAI_PROVIDER_CONFIG = ProviderConfig(
    api_key_schema=OAI_CONFIG["API_key_schema"],
    provider="openai",
    base_url=OAI_CONFIG["base_url"],
)


default_endpoint_config = {
    "chat/completions": OAI_MODEL_SPECIFICATIONS["gpt-4o"].endpoint_schema[
        "chat/completions"
    ],
    "embeddings": OAI_MODEL_SPECIFICATIONS["text-embeddings-3-large"].endpoint_schema[
        "embeddings"
    ],
}


class OpenAIService(ProviderService):

    config: ProviderConfig = OAI_PROVIDER_CONFIG
    token_calculator: OpenAITokenCalculator = OpenAITokenCalculator()
    model_specification: dict = OAI_MODEL_SPECIFICATIONS
    endpoint_config: dict = default_endpoint_config

    def __init__(
        self,
        api_key=None,
        api_key_schema=None,
    ):
        super().__init__(
            token_calculator=self.token_calculator,
            config=self.config,
            model_specification=self.model_specification,
            endpoint_config=self.endpoint_config,
        )

        self.api_key = api_key
        if api_key_schema:
            self.config = self.config.model_copy()
            self.config.api_key_schema = api_key_schema
        if self.api_key is None:
            self.api_key = os.getenv(
                self.config.api_key_schema,
                "OPENAI_API_KEY",
            )

    async def serve_chat(self, messages, **kwargs):
        if not "chat/completions" in self.active_endpoints:
            self.add_endpoint(endpoint="chat/completions")

        messages = self.prepare_chat_input(messages)
        payload = self.active_endpoints["chat/completions"].schema.create_payload(
            input_=messages
        )
        return await self.serve(payload=payload, endpoint="chat/completions", **kwargs)
