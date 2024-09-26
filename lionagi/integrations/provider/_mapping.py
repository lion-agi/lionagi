from .oai import OpenAIService
from .openrouter import OpenRouterService
from .ollama import OllamaService
from .transformers import TransformersService
from .litellm import LiteLLMService
from .mlx_service import MLXService
from .groq import GroqService
from lionagi.integrations.config.oai_configs import oai_schema
from lionagi.integrations.config.openrouter_configs import openrouter_schema

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
    "groq": {
        "service": GroqService,
        "schema": groq_schema,
        "default_model": "llama3-70b-8192",
}

# TODO
# "Ollama": OllamaService,
# "Transformers": TransformersService,
# "MLX": MLXService,
