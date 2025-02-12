# lionagi/service/endpoints/config.py



# lionagi/service/endpoints/config.py

from typing import Literal, Dict, Any, Set
from pydantic import BaseModel, Field

class EndpointConfig(BaseModel):
    """Represents configuration data for an API endpoint."""

    name: str = Field(
        ...,
        description="Unique name for the endpoint (e.g., 'chat_completions', 'search_google')."
    )
    provider: str = Field(
        ...,
        description="Name of the service provider (e.g., 'openai', 'google', 'custom_sql')."
                   + " This links the endpoint to a ResourceConnector."
    )
    base_url: str = Field(
        ...,
        description="Base URL for the API (e.g., 'https://api.openai.com/v1')."
    )
    endpoint: str = Field(
        ...,
        description="Endpoint path (e.g., '/chat/completions', '/search')."
    )
    endpoint_params: dict[str, Any] | None = Field(
        default=None,
        description="Key-value pairs for dynamic endpoint formatting (e.g., {'version': 'v1'})."
    )
    method: Literal["get", "post", "put", "delete"] = Field(
        "post",
        description="HTTP method used when calling this endpoint."
    )
    openai_compatible: bool = Field(
        False,
        description="If True, indicates that the endpoint expects OpenAI-style requests."
    )
    required_kwargs: set[str] = Field(
        default_factory=set,
        description="The names of required parameters for this endpoint."
    )
    optional_kwargs: set[str] = Field(
        default_factory=set,
        description="The names of optional parameters for this endpoint."
    )
    deprecated_kwargs: set[str] = Field(
        default_factory=set,
        description="The names of parameters that may still be accepted but are deprecated."
    )
    is_invokeable: bool = Field(
        False,
        description="Whether this endpoint supports direct invocation."
    )
    is_streamable: bool = Field(
        False,
        description="Whether this endpoint supports streaming responses."
    )
    requires_tokens: bool = Field(
        False,
        description="Whether tokens must be calculated before sending a request."
    )
    api_version: str | None = Field(
        None,
        description="An optional version string for the API."
    )
    allowed_roles: list[str] | None = Field(
        None,
        description="If set, only these roles are allowed in message or conversation data."
    )
    request_options: type | None = Field(
        None, exclude=True
    )  # For Pydantic validation
    model: str | None = Field(
        None,
        description="model used for this endpoint",
    )

    api_key: str | None = Field(None, exclude=True) # sensitive info should not exist in config