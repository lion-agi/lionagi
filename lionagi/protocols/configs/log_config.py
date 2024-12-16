# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Any

from pydantic import field_validator

from lionagi.core.models.schema_model import SchemaModel
from lionagi.core.typing.pydantic_ import Field


class LogConfig(SchemaModel):
    """Configuration for log management.

    This class defines all configuration options for LogManager behavior
    including file paths, persistence strategies, and capacity management.

    Attributes:
        persist_dir: Base directory for log storage
        subfolder: Optional subfolder within persist_dir
        file_prefix: Prefix for log filenames
        capacity: Maximum logs before auto-dump
        extension: File extension for log files
        use_timestamp: Whether to include timestamps in filenames
        hash_digits: Random hash digits in filenames
        auto_save_on_exit: Whether to save on program exit
        clear_after_dump: Whether to clear after dumping

    Example:
        >>> config = LogConfig(
        ...     persist_dir="./logs",
        ...     capacity=1000,
        ...     file_prefix="service_"
        ... )
        >>> manager = LogManager.from_config(config)
    """

    # Basic settings
    persist_dir: Path | str | None = Field(
        default="./data/logs", description="Base directory for log persistence"
    )
    subfolder: str | None = Field(
        default=None,
        description="Optional subfolder within persist_dir",
    )
    file_prefix: str | None = Field(
        default=None, description="Prefix for log filenames"
    )
    capacity: int | None = Field(
        default=None,
        description="Maximum number of logs to keep in memory before dumping",
    )

    # File configuration
    extension: str = Field(
        default=".csv",
        description="File extension for log files",
        pattern=r"^\.[a-zA-Z0-9]+$",
    )
    use_timestamp: bool = Field(
        default=True, description="Whether to include timestamp in filenames"
    )
    hash_digits: int = Field(
        default=5,
        description="Number of random hash digits to add to filenames",
        ge=0,
        le=10,
    )

    # Behavior settings
    auto_save_on_exit: bool = Field(
        default=True,
        description="Whether to automatically save logs when program exits",
    )
    clear_after_dump: bool = Field(
        default=True, description="Whether to clear logs after dumping to file"
    )

    @field_validator("persist_dir")
    def validate_persist_dir(cls, v: Any) -> Path:
        """Validate and convert persist_dir to Path."""
        if v is None:
            return Path("./data/logs")
        return Path(v)

    @field_validator("capacity")
    def validate_capacity(cls, v: Any) -> int | None:
        """Validate capacity is positive if set."""
        if v is not None and v <= 0:
            raise ValueError("Capacity must be positive")
        return v
