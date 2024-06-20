default_interval_token_limit = 1_000_000
default_oai_model = "gpt-3.5-turbo"
default_open_source_model = "llama3"
default_mlx_model = "mlx-community/OLMo-7B-hf-4bit-mlx"


class Services:

    @staticmethod
    def openai():
        from lionagi.app.OpenAI.oai import OpenAIService
        from lionagi.app.OpenAI.oai_configs import oai_schema

        return {
            "service": OpenAIService,
            "schema": oai_schema,
            "default_model": default_oai_model,
            "default_interval_token_limit": default_interval_token_limit,
        }

    @staticmethod
    def openrouter():
        from lionagi.app.OpenRouter.openrouter import OpenRouterService
        from lionagi.app.OpenRouter.openrouter_configs import openrouter_schema

        return {
            "service": OpenRouterService,
            "schema": openrouter_schema,
            "default_model": default_open_source_model,
            "default_interval_token_limit": default_interval_token_limit,
        }

    @staticmethod
    def transformers():
        from lionagi.app.Transformers._transformers import TransformersService

        return {
            "service": TransformersService,
            "schema": {"model": default_open_source_model},
            "default_model": default_open_source_model,
            "default_interval_token_limit": None,
        }

    @staticmethod
    def ollama():
        from lionagi.app.Ollama.service import OllamaService

        return {
            "service": OllamaService,
            "schema": {"model": default_open_source_model},
            "default_model": default_open_source_model,
            "default_interval_token_limit": None,
        }

    @staticmethod
    def litellm():
        from lionagi.app.LiteLLM.litellm import LiteLLMService

        return {
            "service": LiteLLMService,
            "schema": {"model": default_oai_model},
            "default_model": default_oai_model,
            "default_interval_token_limit": default_interval_token_limit,
        }

    @staticmethod
    def mlx():
        from lionagi.app.MLX.service import MLXService

        return {
            "service": MLXService,
            "schema": {"model": default_mlx_model},
            "default_model": default_mlx_model,
            "default_interval_token_limit": None,
        }
