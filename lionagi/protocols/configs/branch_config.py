# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from lionagi.core.models.schema_model import SchemaModel
from lionagi.core.typing.pydantic_ import Field

from .imodel_config import iModelConfig
from .log_config import LogConfig
from .retry_config import TimedFuncCallConfig


class MessageConfig(SchemaModel):
    """Configuration for message handling in Branch"""

    validation_mode: Literal["raise", "return_value", "return_none"] = Field(
        default="return_value",
        description="How to handle message validation failures",
    )
    auto_retries: bool = Field(
        False, description="Whether to automatically retry message parsing"
    )

    max_retries: int = Field(
        default=0, description="Maximum retries for message parsing"
    )
    allow_actions: bool = Field(
        default=True,
        description="Whether to allow action requests in messages",
    )
    auto_invoke_action: bool = Field(
        default=True, description="Whether to automatically invoke actions"
    )


class BranchConfig(SchemaModel):
    """Main configuration for Branch class.

    Combines all aspects of Branch configuration including logging,
    message handling, tool management, and iModel integration.
    """

    name: str | None = Field(
        default=None, description="Branch name for identification"
    )
    user: str | None = Field(
        default=None, description="User ID/name for the branch"
    )
    message_log_config: LogConfig = Field(
        default_factory=LogConfig,
        description="Configuration for log management",
    )
    action_log_config: LogConfig = Field(
        default_factory=LogConfig,
        description="Configuration for action log management",
    )
    message_config: MessageConfig = Field(
        default_factory=MessageConfig,
        description="Configuration for message handling",
    )
    auto_register_tools: bool = Field(
        default=True,
        description="Whether to automatically register tools when needed",
    )
    action_call_config: TimedFuncCallConfig = Field(
        default_factory=TimedFuncCallConfig,
        description="Configuration for action execution",
    )
    imodel_config: iModelConfig | None = Field(
        default=None, description="Configuration for iModel integration"
    )
    retry_imodel_config: iModelConfig | None = Field(
        default=None, description="Configuration for iModel integration"
    )
    kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional branch-specific configurations",
    )


__all__ = [
    "MessageConfig",
    "BranchConfig",
]
