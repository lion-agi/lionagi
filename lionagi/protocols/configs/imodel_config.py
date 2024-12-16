# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import os

from lionagi.core.models.schema_model import SchemaModel
from lionagi.core.typing.pydantic_ import Field
from lionagi.core.typing.typing_ import Any


class iModelConfig(SchemaModel):
    """Configuration for iModel service interaction.

    Provides explicit configuration for iModel services. Users must specify
    the environment variable name that contains their API key.

    Basic Usage:
        >>> config = iModelConfig(
        ...     provider="anthropic",
        ...     api_key_env="MY_ANTHROPIC_KEY",
        ...     model="claude-3"
        ... )
        >>> imodel = iModel(**config.dict())
    """

    provider: str = Field(..., description="Service provider name")
    api_key: str = Field(
        ..., description="Environment variable name containing API key"
    )
    task: str = Field(
        default="chat", description="Task type for model interface"
    )
    model: str | None = Field(default=None, description="Model identifier")
    interval_tokens: int | None = Field(
        default=None, description="Token limit per minute"
    )
    interval_requests: int | None = Field(
        default=None, description="Request limit per minute"
    )
    kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific arguments",
    )

    @classmethod
    def load_json(cls, file_path: str) -> "iModelConfig":
        """Load configuration from a JSON file."""
        try:
            data = json.load(file_path)
            out = cls(**data)
            validate_api_key(out.api_key)
            return out
        except Exception as e:
            raise ValueError(
                f"Error loading configuration from {file_path}: {e}"
            )


def validate_api_key(v: str) -> str:
    """Validate API key environment variable exists."""
    if not os.getenv(v):
        if len(v) > 10:
            v = v[:10] + "..."
        raise ValueError(
            f"API Key Environment variable '{v}' not found or empty. "
            "Please set your API key in the specified environment "
            "variable. Never directly input API keys in config files."
        )


__all__ = ["iModelConfig"]
