import os
from dotenv import load_dotenv
from lionagi.libs import SysUtil, BaseService, StatusTracker

load_dotenv()


class iModel:
    """
    iModel is a class for managing AI model configurations and service
    integrations.

    Attributes:
        ln_id (str): A unique identifier for the model instance.
        timestamp (str): The timestamp when the model instance is created.
        endpoint (str): The API endpoint for the model service.
        provider_schema (dict): The schema for the service provider.
        provider (BaseService): The service provider instance.
        endpoint_schema (dict): The schema for the endpoint configuration.
        api_key (str): The API key for the service provider.
        status_tracker (StatusTracker): Instance of StatusTracker to track
            service status.
        service (BaseService): Configured service instance.
        config (dict): Configuration dictionary for the model.
        iModel_name (str): Name of the model.
    """

    def __init__(
        self,
        model: str = None,
        config: dict = None,
        provider: str = None,
        provider_schema: dict = None,
        endpoint: str = "chat/completions",
        token_encoding_name: str = "cl100k_base",
        api_key: str = None,
        api_key_schema: str = None,
        interval_tokens: int = 100_000,
        interval_requests: int = 1_000,
        interval: int = 60,
        service: BaseService = None,
        **kwargs,  # additional parameters for the model
    ):
        """
        Initializes an instance of the iModel class.

        Args:
            model (str, optional): Name of the model.
            config (dict, optional): Configuration dictionary.
            provider (str, optional): Name or class of the provider.
            provider_schema (dict, optional): Schema dictionary for the
                provider.
            endpoint (str, optional): Endpoint string, default is
                "chat/completions".
            token_encoding_name (str, optional): Name of the token encoding,
                default is "cl100k_base".
            api_key (str, optional): API key for the provider.
            api_key_schema (str, optional): Schema for the API key.
            interval_tokens (int, optional): Token interval limit, default is
                100,000.
            interval_requests (int, optional): Request interval limit, default
                is 1,000.
            interval (int, optional): Time interval in seconds, default is 60.
            service (BaseService, optional): An instance of BaseService.
            **kwargs: Additional parameters for the model.
        """
        self.ln_id: str = SysUtil.create_id()
        self.timestamp: str = SysUtil.get_timestamp(sep=None)[:-6]
        self.endpoint = endpoint

        if isinstance(provider, type):
            provider = provider.__name__.replace("Service", "").lower()

        else:
            provider = str(provider).lower() if provider else "openai"

        from lionagi.integrations.provider._mapping import (
            SERVICE_PROVIDERS_MAPPING,
        )

        self.provider_schema = (
            provider_schema or SERVICE_PROVIDERS_MAPPING[provider]["schema"]
        )
        self.provider = SERVICE_PROVIDERS_MAPPING[provider]["service"]
        self.endpoint_schema = self.provider_schema[endpoint]

        if api_key is not None:
            self.api_key = api_key

        elif api_key_schema is not None:
            self.api_key = os.getenv(api_key_schema)
        else:
            self.api_key = os.getenv(self.provider_schema["API_key_schema"][0])

        self.status_tracker = StatusTracker()

        self.service: BaseService = self._set_up_service(
            service=service,
            provider=self.provider,
            api_key=self.api_key,
            schema=self.provider_schema,
            token_encoding_name=token_encoding_name,
            max_tokens=interval_tokens,
            max_requests=interval_requests,
            interval=interval,
        )

        self.config = self._set_up_params(
            config or self.endpoint_schema["config"], **kwargs
        )

        if model and self.config["model"] != model:
            self.iModel_name = model
            self.config["model"] = model
            self.endpoint_schema["config"]["model"] = model

        else:
            self.iModel_name = self.config["model"]

    def update_config(self, **kwargs):
        """
        Updates the configuration with additional parameters.

        Args:
            **kwargs: Additional parameters to update the configuration.
        """
        self.config = self._set_up_params(self.config, **kwargs)

    def _set_up_config(self, model_config, **kwargs):
        """
        Sets up the model configuration.

        Args:
            model_config (dict): The default configuration dictionary.
            **kwargs: Additional parameters to update the configuration.

        Returns:
            dict: Updated configuration dictionary.
        """
        return {**model_config, **kwargs}

    def _set_up_service(self, service=None, provider=None, **kwargs):
        """
        Sets up the service for the model.

        Args:
            service (BaseService, optional): An instance of BaseService.
            provider (str, optional): Provider name or instance.
            **kwargs: Additional parameters for the service.

        Returns:
            BaseService: Configured service instance.
        """
        if not service:
            provider = provider or self.provider
            return provider(**kwargs)
        return service

    def _set_up_params(self, default_config=None, **kwargs):
        """
        Sets up the parameters for the model.

        Args:
            default_config (dict, optional): The default configuration
                dictionary.
            **kwargs: Additional parameters to update the configuration.

        Returns:
            dict: Updated parameters dictionary.

        Raises:
            ValueError: If any parameter is not allowed.
        """
        params = {**default_config, **kwargs}
        allowed_params = (
            self.endpoint_schema["required"] + self.endpoint_schema["optional"]
        )

        if allowed_params != []:
            if (
                len(
                    not_allowed := [k for k in params.keys() if k not in allowed_params]
                )
                > 0
            ):
                raise ValueError(f"Not allowed parameters: {not_allowed}")

        return params

    async def call_chat_completion(self, messages, **kwargs):
        """
        Asynchronous method to call the chat completion service.

        Args:
            messages (list): List of messages for the chat completion.
            **kwargs: Additional parameters for the service call.

        Returns:
            dict: Response from the chat completion service.
        """
        return await self.service.serve_chat(messages, **kwargs)

    def to_dict(self):
        """
        Converts the model instance to a dictionary representation.

        Returns:
            dict: Dictionary representation of the model instance.
        """
        return {
            "ln_id": self.ln_id,
            "timestamp": self.timestamp,
            "provider": self.provider.__name__.replace("Service", ""),
            "api_key": self.api_key[:4]
            + "*" * (len(self.api_key) - 8)
            + self.api_key[-4:],
            "endpoint": self.endpoint,
            "token_encoding_name": self.service.token_encoding_name,
            **self.config,
        }

    # TODO: add more endpoints
    # async def call_embedding(self, input_file, **kwargs):
    #     return await self.service.serve(input_file, "embedding", **kwargs)

    # TODO: add from_dict method
