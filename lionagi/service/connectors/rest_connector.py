# lionagi/service/connectors/rest_connector.py
import httpx
from .base import ResourceConnector  # Import the protocol

class RESTConnector(ResourceConnector):
    """
    Example connector for a RESTful external API.
    """
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def connect(self, **kwargs) -> None:
        # e.g. we might do a health check call
        pass

    async def call(self, operation: str, data: dict) -> dict:
        """
        'operation' might be an endpoint path or a config specifying how to call.
        'data' might have 'method', 'path', 'payload', etc.
        """
        method = data.get("method", "GET").upper()
        path = data.get("path", "")
        payload = data.get("payload", {})
        url = f"{self.base_url}/{path}"

        if method == "GET":
            resp = await self.client.get(url, params=payload)
        elif method == "POST":
            resp = await self.client.post(url, json=payload)
        else:
            raise ValueError(f"Unsupported method: {method}")

        resp.raise_for_status()
        return resp.json()