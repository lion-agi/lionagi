class Services:

    @staticmethod
    def OpenAI(**kwargs):
        """
        A provider to interact with OpenAI's API endpoints.

        Attributes:
                api_key (Optional[str]): The API key used for authentication.
                schema (Dict[str, Any]): The schema defining the provider's endpoints.
                status_tracker (StatusTracker): The object tracking the status of API calls.
                endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
                base_url (str): The base URL for the OpenAI API.
                available_endpoints (list): A list of available API endpoints, including
                        'chat/completions'
                key_scheme (str): The environment variable name for API key.
                token_encoding_name (str): The default token encoding scheme.
        """

        from lionagi.integrations.provider.oai import OpenAIService

        return OpenAIService(**kwargs)

    @staticmethod
    def OpenRouter(**kwargs):
        """
        A provider to interact with OpenRouter's API endpoints.

        Attributes:
                api_key (Optional[str]): The API key used for authentication.
                schema (Dict[str, Any]): The schema defining the provider's endpoints.
                status_tracker (StatusTracker): The object tracking the status of API calls.
                endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
                base_url (str): The base URL for the OpenAI API.
                available_endpoints (list): A list of available API endpoints, including
                        'chat/completions'
                key_scheme (str): The environment variable name for API key.
                token_encoding_name (str): The default token encoding scheme.
        """

        from lionagi.integrations.provider.openrouter import OpenRouterService

        return OpenRouterService(**kwargs)

    @staticmethod
    def Transformers(**kwargs):
        """
        A provider to interact with Transformers' pipeline

        Attributes:
                task (str): The specific task to be performed by the transformer model.
                        Currently, only 'conversational' tasks are supported.
                model (Union[str, Any]): Identifier for the transformer model to be used. This
                        can be a model name or a path to a model.
                config (Union[str, Dict, Any]): Configuration for the transformer model. Can
                        include tokenizer information among others.
                pipe (pipeline): The loaded transformer pipeline for the specified task, model,
                        and configuration.

        Warnings:
                - Ensure the selected model is suitable for conversational tasks to avoid
                unexpected behavior.
                - As this provider heavily relies on external libraries (Hugging Face's
                Transformers), ensure they are installed and updated to compatible versions.

        Dependencies:
                - Requires the `transformers` library by Hugging Face and `asyncio` for
                asynchronous operations.
        """

        from lionagi.integrations.provider.transformers import (
            TransformersService,
        )

        return TransformersService(**kwargs)

    #
    # @staticmethod
    # def Anthropic(**kwargs):
    #     """
    #     A provider to interact with Anthropic's API endpoints.
    #
    #     Attributes:
    #         api_key (Optional[str]): The API key used for authentication.
    #         schema (Dict[str, Any]): The schema defining the provider's endpoints.
    #         status_tracker (StatusTracker): The object tracking the status of API calls.
    #         endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
    #         base_url (str): The base URL for the Anthropic API.
    #         available_endpoints (list): A list of available API endpoints, including
    #             'chat/completions'
    #         key_scheme (str): The environment variable name for API key.
    #         token_encoding_name (str): The default token encoding scheme.
    #     """
    #
    #     from .api. import AnthropicService
    #     return AnthropicService(**kwargs)

    @staticmethod
    def Ollama(**kwargs):
        """
        A provider to interact with Ollama

        Attributes:
                model (str): name of the model to use
                kwargs (Optional[Any]): additional kwargs for calling the model
        """

        from lionagi.integrations.provider.ollama import OllamaService

        return OllamaService(**kwargs)

    @staticmethod
    def LiteLLM(**kwargs):
        """
        A provider to interact with Litellm

        Attributes:
                model (str): name of the model to use
                kwargs (Optional[Any]): additional kwargs for calling the model
        """

        from .litellm import LiteLLMService

        return LiteLLMService(**kwargs)

    @staticmethod
    def MLX(**kwargs):
        """
        A provider to interact with MlX

        Attributes:
                model (str): name of the model to use
                kwargs (Optional[Any]): additional kwargs for calling the model
        """

        from lionagi.integrations.provider.mlx_service import MLXService

        return MLXService(**kwargs)
