from .OpenAI import OpenAIService
from .OpenRouter.openrouter import OpenRouterService
from .Ollama.ollama_service import OllamaService
from .Transformers.transformers import TransformersService
from .LiteLLM.litellm import LiteLLMService
from .mlx_service import MLXService
from lionagi.integrations.OpenAI.oai_configs import oai_schema
from lionagi.integrations.OpenRouter.openrouter_configs import openrouter_schema

SERVICE_PROVIDERS_MAPPING = {
    "openai": {
        "service": OpenAIService,
        "schema": oai_schema,
        "default_model": "gpt-3.5-turbo",
    },
    "openrouter": {
        "service": OpenRouterService,
        "schema": openrouter_schema,
        "default_model": "gpt-3.5-turbo",
    },
    "litellm": {
        "service": LiteLLMService,
        "schema": oai_schema,
        "default_model": "gpt-3.5-turbo",
    },
    "ollama": {
        "service": OllamaService,
        "schema": {"model": "llama3"},
        "default_model": "llama3",
    },
    "transformers": {
        "service": TransformersService,
        "schema": {"model": "gpt2"},
        "default_model": "gpt2",
    },
    "mlx": {
        "service": MLXService,
        "schema": {"model": "mlx-community/OLMo-7B-hf-4bit-mlx"},
        "default_model": "mlx-community/OLMo-7B-hf-4bit-mlx",
    },
}

# TODO
# "Ollama": OllamaService,
# "Transformers": TransformersService,
# "MLX": MLXService,
