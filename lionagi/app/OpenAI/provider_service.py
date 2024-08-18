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
    "embeddings": OAI_MODEL_SPECIFICATIONS["text-embeddings-3-small"].endpoint_schema[
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
            api_key=api_key,
            api_key_schema=api_key_schema,
        )

