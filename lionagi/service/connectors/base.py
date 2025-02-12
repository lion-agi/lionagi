# lionagi/service/connectors/base.py

from typing import Protocol

class ResourceConnector(Protocol):
    """
    A protocol that all resource connectors must implement.
    """
    name: str

    async def connect(self, **kwargs) -> None:
        """Initialize or create a connection. Possibly do nothing if not required."""
        ...

    async def call(self, operation: str, data: dict) -> dict:
        """
        Perform an operation on this resource with `data`.
        Return a dictionary representing the result.
        """
        ...