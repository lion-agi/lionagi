from .oai import OpenAIService
from .openrouter import OpenRouterService

# from .ollama import OllamaService
# from .transformers import TransformersService
from .litellm import LiteLLMService

# from .mlx_service import MLXService


from lionagi.integrations.config.oai_configs import oai_schema
from lionagi.integrations.config.openrouter_configs import openrouter_schema

SERVICE_PROVIDERS_MAPPING = {
    "openai": {
        "service": OpenAIService,
        "schema": oai_schema,
    },
    "openrouter": {
        "service": OpenRouterService,
        "schema": openrouter_schema,
    },
    "litellm": {
        "service": LiteLLMService,
        "schema": oai_schema,
    },
}

# TODO
# "Ollama": OllamaService,
# "Transformers": TransformersService,
# "MLX": MLXService,
