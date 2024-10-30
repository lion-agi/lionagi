import asyncio
import os

import lionfuncs as ln
import numpy as np
from dotenv import load_dotenv

from lionagi.libs import (
    APIUtil,
    BaseService,
    StatusTracker,
    SysUtil,
    ninsert,
    to_list,
)

from .abc import Component, ModelLimitExceededError

load_dotenv()


_oai_price_map = {
    "gpt-4o": (5, 15),
    "gpt-4o-2024-08-06": (2.5, 10),
    "gpt-4o-mini": (0.15, 0.6),
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
        self.ln_id: str = SysUtil.id()
        self.timestamp: str = ln.time(type_="iso")
        self.endpoint = endpoint
        self.allowed_parameters = allowed_parameters
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
                    not_allowed := [
                        k for k in params.keys() if k not in allowed_params
                    ]
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

        num_tokens = APIUtil.calculate_num_token(
            {"messages": messages},
            "chat/completions",
            self.endpoint_schema.get("token_encoding_name", None),
        )

        if num_tokens > self.token_limit:
            raise ModelLimitExceededError(
                f"Number of tokens {num_tokens} exceeds the limit {self.token_limit}"
            )

        return await self.service.serve_chat(
            messages, required_tokens=num_tokens, **kwargs
        )

    async def call_embedding(self, embed_str, **kwargs):
        """
        Asynchronous method to call the embedding service.

        Args:
            input_file (str): Path to the input file.
            **kwargs: Additional parameters for the service call.

        Returns:
            dict: Response from the embedding service.
        """
        return await self.service.serve_embedding(embed_str, **kwargs)

    async def embed_node(self, node, field="content", **kwargs) -> bool:
        """
        if not specify field, we embed node.content
        """
        if not isinstance(node, Component):
            raise ValueError("Node must a lionagi item")
        embed_str = getattr(node, field)

        if isinstance(embed_str, dict) and "images" in embed_str:
            embed_str.pop("images", None)
            embed_str.pop("image_detail", None)

        num_tokens = APIUtil.calculate_num_token(
            {
                "input": (
                    str(embed_str)
                    if isinstance(embed_str, dict)
                    else embed_str
                )
            },
            "embeddings",
            self.endpoint_schema["token_encoding_name"],
        )

        if self.token_limit and num_tokens > self.token_limit:
            raise ModelLimitExceededError(
                f"Number of tokens {num_tokens} exceeds the limit {self.token_limit}"
            )

        payload, embed = await self.call_embedding(embed_str, **kwargs)
        payload.pop("input")
        node.add_field("embedding", embed["data"][0]["embedding"])
        node._meta_insert("embedding_meta", payload)

    async def format_structure(
        self,
        data: str | dict,
        json_schema: dict | str = None,
        request_fields: dict | list = None,
        **kwargs,
    ) -> dict:
        if json_schema:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": json_schema,
            }
            kwargs["model"] = kwargs.pop("model", "gpt-4o-mini")
        if not request_fields and not json_schema:
            raise ValueError(
                "Either request_fields or json_schema must be provided"
            )
        request_fields = request_fields or json_schema["properties"]

        messages = [
            {
                "role": "system",
                "content": "You are a helpful json formatting assistant.",
            },
            {
                "role": "user",
                "content": f"can you please format the given data into given json schema?"
                f"--- data --- {data} |||| ----json fields required --- {request_fields}",
            },
        ]

        result = await self.call_chat_completion(messages, **kwargs)
        return result["choices"][0]["message"]["content"]

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
                if k in getattr(self.service, "allowed_kwargs", [])
                and v is not None
            },
            "model_costs": None if self.costs == (0, 0) else self.costs,
        }

    async def compute_perplexity(
        self,
        initial_context: str = None,
        tokens: list[str] = None,
        system_msg: str = None,
        n_samples: int = 1,  # number of samples used for the computation
        use_residue: bool = True,  # whether to use residue for the last sample
        **kwargs,  # additional arguments for the model
    ) -> tuple[list[str], float]:
        tasks = []
        context = initial_context or ""

        n_samples = n_samples or len(tokens)
        sample_token_len, residue = divmod(len(tokens), n_samples)
        samples = []

        if n_samples == 1:
            samples = [tokens]
        else:
            samples = [
                tokens[: (i + 1) * sample_token_len] for i in range(n_samples)
            ]

            if use_residue and residue != 0:
                samples.append(tokens[-residue:])

        sampless = [context + " ".join(sample) for sample in samples]

        for sample in sampless:
            messages = (
                [{"role": "system", "content": system_msg}]
                if system_msg
                else []
            )
            messages.append(
                {"role": "user", "content": sample},
            )

            task = asyncio.create_task(
                self.call_chat_completion(
                    messages=messages,
                    logprobs=True,
                    max_tokens=sample_token_len,
                    **kwargs,
                )
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)  # result is (payload, response)
        results_ = []
        num_prompt_tokens = 0
        num_completion_tokens = 0

        for idx, result in enumerate(results):
            _dict = {}
            _dict["tokens"] = samples[idx]

            num_prompt_tokens += result[1]["usage"]["prompt_tokens"]
            num_completion_tokens += result[1]["usage"]["completion_tokens"]

            logprobs = result[1]["choices"][0]["logprobs"]["content"]
            logprobs = to_list(logprobs, flatten=True, dropna=True)
            _dict["logprobs"] = [(i["token"], i["logprob"]) for i in logprobs]
            results_.append(_dict)

        logprobs = to_list(
            [[i[1] for i in d["logprobs"]] for d in results_], flatten=True
        )

        return {
            "tokens": tokens,
            "n_samples": n_samples,
            "num_prompt_tokens": num_prompt_tokens,
            "num_completion_tokens": num_completion_tokens,
            "logprobs": logprobs,
            "perplexity": np.exp(np.mean(logprobs)),
        }
