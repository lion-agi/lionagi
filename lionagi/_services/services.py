from .oai import OpenAIService
from .openrouter import OpenRouterService

class Services:
    
    @staticmethod
    def OpenAI(**kwargs):
        """A service to interact with OpenAI's API endpoints.

        Attributes:
            api_key (Optional[str]): The API key used for authentication.
            schema (Dict[str, Any]): The schema defining the service's endpoints.
            status_tracker (StatusTracker): The object tracking the status of API calls.
            endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
            base_url (str): The base URL for the OpenAI API.
            available_endpoints (list): A list of available API endpoints.
                ['chat/completions', 'finetune', 'audio_speech', 'audio_transcriptions', 'audio_translations']
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
        return OpenAIService(**kwargs)
    
    @staticmethod 
    def OpenRouter(**kwargs):
        """A service to interact with OpenRouter's API endpoints.

        Attributes:
            api_key (Optional[str]): The API key used for authentication.
            schema (Dict[str, Any]): The schema defining the service's endpoints.
            status_tracker (StatusTracker): The object tracking the status of API calls.
            endpoints (Dict[str, EndPoint]): A dictionary of endpoint objects.
            base_url (str): The base URL for the OpenAI API.
            available_endpoints (list): A list of available API endpoints. ['chat/completions']
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
        return OpenRouterService(**kwargs)
