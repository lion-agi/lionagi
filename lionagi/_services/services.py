class Services:
    
    @staticmethod
    def OpenAI(**kwargs):
        """
        A service to interact with OpenAI's API endpoints.

        Attributes:
            api_key (Optional[str]): The API key used for authentication.
            schema (Dict[str, Any]): The schema defining the service's endpoints.
            status_tracker (StatusTracker): The object tracking the status of API calls.
            endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
            base_url (str): The base URL for the OpenAI API.
            available_endpoints (list): A list of available API endpoints, including 
                'chat/completions'
            key_scheme (str): The environment variable name for API key.
            token_encoding_name (str): The default token encoding scheme.
        """

        from .oai import OpenAIService
        return OpenAIService(**kwargs)
    
    @staticmethod 
    def OpenRouter(**kwargs):
        """
        A service to interact with OpenRouter's API endpoints.

        Attributes:
            api_key (Optional[str]): The API key used for authentication.
            schema (Dict[str, Any]): The schema defining the service's endpoints.
            status_tracker (StatusTracker): The object tracking the status of API calls.
            endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
            base_url (str): The base URL for the OpenAI API.
            available_endpoints (list): A list of available API endpoints, including 
                'chat/completions'
            key_scheme (str): The environment variable name for API key.
            token_encoding_name (str): The default token encoding scheme.
        """

        from .openrouter import OpenRouterService
        return OpenRouterService(**kwargs)

    @staticmethod
    def Transformers(**kwargs):
        """
        A service to interact with Transformers' pipeline

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
            - As this service heavily relies on external libraries (Hugging Face's 
            Transformers), ensure they are installed and updated to compatible versions.

        Dependencies:
            - Requires the `transformers` library by Hugging Face and `asyncio` for 
            asynchronous operations.
        """

        from .transformers import TransformersService
        return TransformersService(**kwargs)


    @staticmethod
    def Anthropic(**kwargs):
        """
        A service to interact with Anthropic's API endpoints.

        Attributes:
            api_key (Optional[str]): The API key used for authentication.
            schema (Dict[str, Any]): The schema defining the service's endpoints.
            status_tracker (StatusTracker): The object tracking the status of API calls.
            endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
            base_url (str): The base URL for the Anthropic API.
            available_endpoints (list): A list of available API endpoints, including 
                'chat/completions'
            key_scheme (str): The environment variable name for API key.
            token_encoding_name (str): The default token encoding scheme.
        """

        from .anthropic import AnthropicService
        return AnthropicService(**kwargs)
