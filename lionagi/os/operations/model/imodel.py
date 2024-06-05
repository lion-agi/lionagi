"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from dotenv import load_dotenv
from lionagi.os.libs import ninsert
from lionagi.os.libs.sys_util import create_id, get_timestamp

from ..api.service import BaseService
from ..api.status_tracker import StatusTracker

load_dotenv()


_oai_price_map = {
    "gpt-4o": (5, 15),
    "gpt-4-turbo": (10, 30),
    "gpt-3.5-turbo": (0.5, 1.5),
}


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

    default_model = "gpt-4o"

    def __init__(
        self,
        model: str = None,
        config: dict = None,
        provider: str = None,
        provider_schema: dict = None,
        endpoint: str = "chat/completions",
        token_encoding_name: str = None,
        api_key: str = None,
        api_key_schema: str = None,
        interval_tokens: int = None,
        interval_requests: int = None,
        interval: int = None,
        service: BaseService = None,
        allowed_parameters=[],
        device: str = None,
        costs=None,
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
        self.ln_id: str = create_id()
        self.timestamp: str = get_timestamp(sep=None)[:-6]
        self.endpoint = endpoint
        self.allowed_parameters = allowed_parameters
        if isinstance(provider, type):
            provider = provider.__name__.replace("Service", "").lower()

        else:
            provider = str(provider).lower() if provider else "openai"

        from lionagi.integrations.model_provider._mapping import (
            SERVICE_PROVIDERS_MAPPING,
        )

        self.provider_schema = (
            provider_schema or SERVICE_PROVIDERS_MAPPING[provider]["schema"]
        )
        self.provider = SERVICE_PROVIDERS_MAPPING[provider]["service"]
        self.endpoint_schema = self.provider_schema.get(endpoint, {})
        self.token_limit = self.endpoint_schema.get("token_limit", 100_000)

        if api_key is not None:
            self.api_key = api_key

        elif api_key_schema is not None:
            self.api_key = os.getenv(api_key_schema)
        else:
            api_schema = self.provider_schema.get("API_key_schema", None)
            if api_schema:
                self.api_key = os.getenv(
                    self.provider_schema["API_key_schema"][0], None
                )

        self.status_tracker = StatusTracker()

        set_up_kwargs = {
            "api_key": getattr(self, "api_key", None),
            "schema": self.provider_schema or None,
            "endpoint": self.endpoint,
            "token_limit": self.token_limit,
            "token_encoding_name": token_encoding_name
            or self.endpoint_schema.get("token_encoding_name", None),
            "max_tokens": interval_tokens
            or self.endpoint_schema.get("interval_tokens", None),
            "max_requests": interval_requests
            or self.endpoint_schema.get("interval_requests", None),
            "interval": interval or self.endpoint_schema.get("interval", None),
        }

        set_up_kwargs = {
            k: v
            for k, v in set_up_kwargs.items()
            if v is not None and k in self.allowed_parameters
        }

        self.config = self._set_up_params(
            config or self.endpoint_schema.get("config", {}), **kwargs
        )

        if not model:
            if "model" not in self.config:
                model = SERVICE_PROVIDERS_MAPPING[provider]["default_model"]

        if self.config.get("model", None) != model and model is not None:
            self.iModel_name = model
            self.config["model"] = model
            ninsert(self.endpoint_schema, ["config", "model"], model)

        else:
            self.iModel_name = self.config["model"]

        if device:
            set_up_kwargs["device"] = device
        set_up_kwargs["model"] = self.iModel_name
        self.service: BaseService = self._set_up_service(
            service=service,
            provider=self.provider,
            **set_up_kwargs,
        )
        if self.iModel_name in _oai_price_map:
            self.costs = _oai_price_map[self.iModel_name]
        else:
            self.costs = costs or (0, 0)

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
            a = provider.__name__.replace("Service", "").lower()
            if a in ["openai", "openrouter"]:
                kwargs.pop("model", None)

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
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        params = {**default_config, **kwargs}
        allowed_params = self.endpoint_schema.get(
            "required", []
        ) + self.endpoint_schema.get("optional", [])

        if allowed_params != []:
            if (
                len(
                    not_allowed := [k for k in params.keys() if k not in allowed_params]
                )
                > 0
            ):
                raise ValueError(f"Not allowed parameters: {not_allowed}")

        return params

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
            **{
                k: v
                for k, v in self.config.items()
                if k in getattr(self.service, "allowed_kwargs", []) and v is not None
            },
            "model_costs": None if self.costs == (0, 0) else self.costs,
        }
