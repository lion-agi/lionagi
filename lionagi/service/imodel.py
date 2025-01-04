# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import os
import warnings

from .endpoints.base import APICalling, EndPoint
from .endpoints.match_endpoint import match_endpoint
from .endpoints.rate_limited_processor import RateLimitedAPIExecutor

warnings.filterwarnings(
    "ignore",
    message=".*Valid config keys have changed in V2.*",
    category=UserWarning,
    module="pydantic._internal._config",
)


class iModel:
    """Manages API calls for a specific provider with optional rate-limiting.

    The iModel class encapsulates a specific endpoint configuration (e.g.,
    chat or completion endpoints). It determines and sets the necessary
    API key based on the provider and uses a RateLimitedAPIExecutor to
    handle queuing and throttling requests.

    Attributes:
        endpoint (EndPoint):
            The chosen endpoint object (constructed via `match_endpoint` if
            none is provided).
        should_invoke_endpoint (bool):
            If True, the endpoint is called for real. If False, calls might
            be mocked or cached.
        kwargs (dict):
            Any additional keyword arguments passed to initialize and
            configure the iModel (e.g., `model`, `api_key`).
        executor (RateLimitedAPIExecutor):
            The rate-limited executor that queues and runs API calls in a
            controlled fashion.
    """

    def __init__(
        self,
        provider: str = None,
        base_url: str = None,
        endpoint: str | EndPoint = "chat",
        endpoint_params: list[str] | None = None,
        api_key: str = None,
        queue_capacity: int = 100,
        capacity_refresh_time: float = 60,
        interval: float | None = None,
        limit_requests: int = None,
        limit_tokens: int = None,
        invoke_with_endpoint: bool = True,
        **kwargs,
    ) -> None:
        """Initializes the iModel instance.

        Args:
            provider (str, optional):
                Name of the provider (e.g., 'openai', 'anthropic').
            base_url (str, optional):
                Base URL for the API (if a custom endpoint is needed).
            endpoint (str | EndPoint, optional):
                Either a string representing the endpoint type (e.g., 'chat')
                or an `EndPoint` instance.
            endpoint_params (list[str] | None, optional):
                Additional parameters for the endpoint (e.g., 'v1' or other).
            api_key (str, optional):
                An explicit API key. If not given, tries to load one from
                environment variables based on the provider.
            queue_capacity (int, optional):
                Maximum number of requests allowed in the queue before
                executing them.
            capacity_refresh_time (float, optional):
                Time interval (in seconds) after which the queue capacity
                is refreshed.
            interval (float | None, optional):
                Interval in seconds to check or process requests in
                the queue. If None, defaults to capacity_refresh_time.
            limit_requests (int | None, optional):
                Maximum number of requests allowed per cycle, if any.
            limit_tokens (int | None, optional):
                Maximum number of tokens allowed per cycle, if any.
            invoke_with_endpoint (bool, optional):
                If True, the endpoint is actually invoked. If False,
                calls might be mocked or cached.
            **kwargs:
                Additional keyword arguments, such as `model`, or any other
                provider-specific fields.
        """
        if api_key is None:
            match provider:
                case "openai":
                    api_key = "OPENAI_API_KEY"
                case "anthropic":
                    api_key = "ANTHROPIC_API_KEY"
                case "openrouter":
                    api_key = "OPENROUTER_API_KEY"
                case "perplexity":
                    api_key = "PERPLEXITY_API_KEY"
                case "groq":
                    api_key = "GROQ_API_KEY"

        if os.getenv(api_key, None) is not None:
            self.api_key_scheme = api_key
            api_key = os.getenv(api_key)

        kwargs["api_key"] = api_key
        model = kwargs.get("model", None)
        if model:
            if not provider:
                if "/" in model:
                    provider = model.split("/")[0]
                    model = model.replace(provider + "/", "")
                    kwargs["model"] = model
                else:
                    raise ValueError("Provider must be provided")

        if isinstance(endpoint, EndPoint):
            self.endpoint = endpoint
        else:
            self.endpoint = match_endpoint(
                provider=provider,
                base_url=base_url,
                endpoint=endpoint,
                endpoint_params=endpoint_params,
            )
        if provider:
            self.endpoint.config.provider = provider
        if base_url:
            self.endpoint.config.base_url = base_url

        self.should_invoke_endpoint = invoke_with_endpoint
        self.kwargs = kwargs
        self.executor = RateLimitedAPIExecutor(
            queue_capacity=queue_capacity,
            capacity_refresh_time=capacity_refresh_time,
            interval=interval,
            limit_requests=limit_requests,
            limit_tokens=limit_tokens,
        )

    def create_api_calling(self, **kwargs) -> APICalling:
        """Constructs an `APICalling` object from endpoint-specific payload.

        Args:
            **kwargs:
                Additional arguments used to generate the payload (merged
                with self.kwargs).

        Returns:
            APICalling:
                An `APICalling` instance with the constructed payload,
                headers, and the selected endpoint.
        """
        kwargs.update(self.kwargs)
        payload = self.endpoint.create_payload(**kwargs)
        return APICalling(
            payload=payload["payload"],
            headers=payload["headers"],
            endpoint=self.endpoint,
            is_cached=payload.get("is_cached", False),
            should_invoke_endpoint=self.should_invoke_endpoint,
        )

    async def process_chunk(self, chunk) -> None:
        """Processes a chunk of streaming data.

        Override this method in subclasses if you need custom handling
        of streaming responses from the API.

        Args:
            chunk:
                A portion of the streamed data returned by the API.
        """
        pass

    async def stream(self, **kwargs) -> APICalling | None:
        """Performs a streaming API call with the given arguments.

        Args:
            **kwargs:
                Arguments for the request, merged with self.kwargs.

        Returns:
            `APICalling` | None:
                An APICalling instance upon success, or None if something
                goes wrong.
        """
        try:
            kwargs["stream"] = True
            api_call = self.create_api_calling(**kwargs)
            async for i in api_call.stream():
                await self.process_chunk(i)
            return api_call
        except Exception as e:
            raise ValueError(f"Failed to stream API call: {e}")

    async def invoke(self, **kwargs) -> APICalling | None:
        """Invokes a rate-limited API call with the given arguments.

        Args:
            **kwargs:
                Arguments for the request, merged with self.kwargs.

        Returns:
            APICalling | None:
                The `APICalling` object if successfully invoked and
                completed; otherwise None.

        Raises:
            ValueError:
                If the call fails or if an error occurs during invocation.
        """
        try:
            kwargs.pop("stream", None)
            api_call = self.create_api_calling(**kwargs)
            if (
                self.executor.processor is None
                or self.executor.processor.is_stopped()
            ):
                await self.executor.start()

            await self.executor.append(api_call)
            await self.executor.forward()
            if api_call.id in self.executor.completed_events:
                return self.executor.pile.pop(api_call.id)
        except Exception as e:
            raise ValueError(f"Failed to invoke API call: {e}")

    @property
    def allowed_roles(self) -> set[str]:
        """list[str]: Roles that are permissible for this endpoint.

        Returns:
            If the endpoint has an `allowed_roles` attribute, returns that;
            otherwise, defaults to `{"system", "user", "assistant"}`.
        """
        if hasattr(self.endpoint, "allowed_roles"):
            return self.endpoint.allowed_roles
        return {"system", "user", "assistant"}

    @property
    def sequential_exchange(self) -> bool:
        """bool: Indicates whether requests must occur in a strict sequence.

        Returns:
            True if the endpoint requires sequential handling of
            messages; False otherwise.
        """
        return self.endpoint.sequential_exchange

    def to_dict(self):
        kwargs = self.kwargs
        if "kwargs" in self.kwargs:
            kwargs = self.kwargs["kwargs"]
        return {
            "provider": self.endpoint.config.provider,
            "endpoint": self.endpoint.config.model_dump(),
            "api_key": (
                self.api_key_scheme
                if hasattr(self, "api_key_scheme")
                else None
            ),
            "processor_config": self.executor.config,
            "invoke_with_endpoint": self.should_invoke_endpoint,
            **{k: v for k, v in kwargs.items() if k != "api_key"},
        }

    @classmethod
    def from_dict(cls, data: dict):
        provider = data.pop("provider", None)
        base_url = data.pop("base_url", None)
        api_key = data.pop("api_key", None)
        processor_config = data.pop("processor_config", {})

        endpoint_config_params = data.pop("endpoint", {})
        endpoint_ = endpoint_config_params.pop("endpoint", None)
        endpoint_params = endpoint_config_params.get("endpoint_params", None)

        endpoint = match_endpoint(
            provider=provider,
            base_url=base_url,
            endpoint=endpoint_,
            endpoint_params=endpoint_params,
        )
        endpoint.update_config(**endpoint_config_params)
        return cls(
            provider=provider,
            base_url=base_url,
            endpoint=endpoint,
            api_key=api_key,
            **data,
            **processor_config,
        )
