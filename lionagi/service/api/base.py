from abc import abstractmethod

from aiocache import cached
from pydantic import BaseModel, Field

from lionagi.protocols.types import Event
from lionagi.settings import Settings


class ConnectionEvent(Event):
    """Event emitted when the connector is connected."""

    request_body: dict | None = Field(
        None,
        description="The request body sent to the connector.",
    )
    is_cached: bool | None = None


class ConnectorConfig(BaseModel):

    name: str | None = None
    is_streamable: bool | None = None


class Connector:

    def __init__(self, config: ConnectorConfig = None):
        self.config = config

    @property
    def name(self):
        return self.config.name

    @property
    def is_streamable(self):
        return self.config.is_streamable

    @abstractmethod
    async def connect(self):
        """Connect to the endpoint."""
        pass

    @abstractmethod
    async def _invoke(self, **kwargs):
        pass

    async def invoke(self, *, is_cached: bool = False, **kwargs):
        if is_cached:
            return await self._cached_invoke(**kwargs)
        return await self._invoke(**kwargs)

    @cached(**Settings.API.CACHED_CONFIG)
    async def _cached_invoke(self, **kwargs) -> ConnectionEvent:
        """Cached version of `connector.invoke` using aiocache."""
        return await self._invoke(**kwargs)

    async def stream(self, **kwargs):
        if not self.is_streamable:
            raise ValueError("This endpoint is not streamable.")
        raise NotImplementedError("Subclasses should implement this method.")


class EndpointConfig(BaseModel):

    provider: str | None = Field(
        None,
        description="The provider of the endpoint. such as, google, openai, etc.",
    )
    name: str | None = Field(
        None,
        description="The name of the endpoint.",
    )
    request_schema: dict | None = Field(
        None,
        description="The request body json schema for the endpoint.",
    )
    connector_config: dict | None = Field(
        None,
        description="The connector config for the endpoint.",
    )


class Endpoint:

    def __init__(self, config: EndpointConfig = None):
        self.config = config
        self.connector: Connector = None
