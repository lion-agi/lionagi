from lionagi.app.OpenAI.oai import OpenAIService
from lionagi.app.OpenAI.oai_configs import oai_schema
from lionagi.app.OpenRouter.openrouter import OpenRouterService
from lionagi.app.OpenRouter.openrouter_configs import openrouter_schema
from lionagi.app.Ollama.service import OllamaService
from lionagi.app.Transformers._transformers import TransformersService
from lionagi.app.LiteLLM.litellm import LiteLLMService
from lionagi.app.MLX.service import MLXService


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
