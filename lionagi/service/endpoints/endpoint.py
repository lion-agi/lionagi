# lionagi/service/endpoints/endpoint.py

import aiohttp
from typing import Any

from lionagi.service.endpoints.config import EndpointConfig

class EndPoint:
    """
    Represents a single API endpoint.  Holds the configuration and a
    client session for making requests.
    """

    def __init__(self, config: EndpointConfig) -> None:
        self.config = config
        self.client_session = aiohttp.ClientSession() # Each endpoint has its own session

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def full_url(self) -> str:
        if self.config.endpoint_params:
            return self.config.base_url + self.config.endpoint.format(
                **self.config.endpoint_params
            )
        return self.config.base_url + "/" + self.config.endpoint


    async def _invoke(self, payload: dict, headers: dict, **kwargs) -> Any:
        """
        Performs the actual HTTP request using aiohttp.
        """

        async with self.client_session.request(
            method=self.config.method.upper(),
            url=self.full_url,
            headers=headers,
            json=payload,  # Assuming JSON for simplicity
            **kwargs,
        ) as response:

            response.raise_for_status()  # Raise HTTPError for bad codes (4xx, 5xx)
            return await response.json()  # Assuming JSON response

    async def _stream(self, payload: dict, headers: dict, **kwargs) -> Any:
        """
        Handles streaming requests (if supported by the endpoint).
        STUBBED for now.
        """
        raise NotImplementedError("Streaming not yet implemented.")

    # Other methods from the original EndPoint class (calculate_tokens, etc.)
    # can be added here as needed.  They would likely interact with the
    # self.config object.  For example:

    def calculate_tokens(self, payload: dict) -> int:
        """Calculates the number of tokens needed for a request (STUB)."""
        if self.config.requires_tokens:
            # TODO: Implement actual token calculation
            # This is just a placeholder
            return 1
        return 0