from typing import Type
from lionagi.os.service.api.provider import (
    Provider,
    PROVIDER_CONFIG,
    PROVIDER_MODEL_SPECIFICATION,
)
from .tokenize.token_calculator import OpenAITokenCalculator
from .model_specs.model_mapping import OPENAI_MODEL_MAPPING
from .model_specs._config import OAI_CONFIG
from .model_service import OpenAIService


_AVAILABLE_ENDPOINTS = [
    i for i in OAI_CONFIG.keys() if i not in ["API_key_schema", "base_url"]
]

OpenAIService.base_url = OAI_CONFIG["base_url"]


class OpenAIProvider(Provider):

    token_calculator: Type[OpenAITokenCalculator] = OpenAITokenCalculator
    config: PROVIDER_CONFIG = PROVIDER_CONFIG(
        api_key_scheme=OAI_CONFIG["API_key_schema"],
        provider="openai",
        base_url=OAI_CONFIG["base_url"],
    )
    model_specification: PROVIDER_MODEL_SPECIFICATION = PROVIDER_MODEL_SPECIFICATION(
        model=OPENAI_MODEL_MAPPING
    )

    service: OpenAIService = OpenAIService()
    available_endpoints = _AVAILABLE_ENDPOINTS
