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
                'chat/completions', 'finetune', 'audio_speech', 'audio_transcriptions', 
                and 'audio_translations'.
            key_scheme (str): The environment variable name for API key.
            token_encoding_name (str): The default token encoding scheme.

        Examples:
            >>> service = OpenAIService(api_key="your_api_key")
            >>> asyncio.run(service.serve("Hello, world!", "chat/completions"))
            (payload, completion)

            >>> service = OpenAIService()
            >>> asyncio.run(service.serve("Convert this text to speech.", "audio_speech"))
            ValueError: 'audio_speech' is currently not supported
        """

        from .oai import OpenAIService
        return OpenAIService(**kwargs)
    
    @staticmethod 
    def OpenRouter(**kwargs):
        """
        A service designed to interface with OpenRouter's API endpoints, simplifying the 
        process of sending requests and handling responses.

        Attributes:
            base_url (str): Defines the base URL for the OpenRouter API.
            available_endpoints (list): Lists the API endpoints that this service can 
                interact with.
            schema (dict): The schema configuration specific to the OpenRouter API.
            key_scheme (str): The environment variable name where the OpenRouter API key 
                is stored.
            token_encoding_name (str): Specifies the default encoding scheme for tokens.

        Examples:
            >>> service = OpenRouterService(api_key="your_api_key")
            >>> asyncio.run(service.serve("Your request here", "chat/completions"))
            (payload, completion)

            >>> service = OpenRouterService()
            >>> asyncio.run(service.serve("Another request.", "chat/completions"))
            # This would routinely follow the expected output as coded in the `serve` and 
            # `serve_chat` methods.

        Warnings:
            - Ensure that the OPENROUTER_API_KEY environment variable is correctly set 
            before initiating the service to avoid authentication issues.
            - Currently, the service is limited in the range of endpoints it supports; 
            extending the functionality requires modifications to the class.
        """

        from .openrouter import OpenRouterService
        return OpenRouterService(**kwargs)

    @staticmethod
    def Transformers(**kwargs):
        
        """
        This service utilizes the Hugging Face's Transformers library to facilitate easy 
        interaction with transformer models, especially focusing on conversation modeling. 
        Its asynchronous architecture enables it to handle requests efficiently in a 
        non-blocking manner.

        Attributes:
            task (str): The specific task to be performed by the transformer model. 
                Currently, only 'conversational' tasks are supported.
            model (Union[str, Any]): Identifier for the transformer model to be used. This 
                can be a model name or a path to a model.
            config (Union[str, Dict, Any]): Configuration for the transformer model. Can 
                include tokenizer information among others.
            pipe (pipeline): The loaded transformer pipeline for the specified task, model, 
                and configuration.

        Example Usage:
            >>> transformers_service = TransformersService(task='conversational', model='gpt-2')
            >>> asyncio.run(transformers_service.serve_chat("Hello, how are you today?"))
            # This will return the input messages along with the model's response in a 
            # structured format.

        Warnings:
            - Ensure the selected model is suitable for conversational tasks to avoid 
            unexpected behavior.
            - As this service heavily relies on external libraries (Hugging Face's 
            Transformers), ensure they are installed and updated to compatible versions.

        Dependencies:
            - Requires the `transformers` library by Hugging Face and `asyncio` for 
            asynchronous operations.
            - The `ThreadPoolExecutor` from the concurrent.futures module is used to run 
            synchronous functions in separate threads, facilitating non-blocking operation.
        """

        from .transformers import TransformersService
        return TransformersService(**kwargs)
