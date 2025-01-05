# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from lionagi.operatives.instruct.instruct import (
    LIST_INSTRUCT_FIELD_MODEL,
    Instruct,
)
from lionagi.operatives.types import FieldModel, SchemaModel
from lionagi.session.session import Branch, Session


class RCallParams(SchemaModel):
    """Parameters for remote function calls."""

    timeout: float = Field(
        default=60, description="Timeout for remote function call"
    )
    max_retries: int = Field(
        default=3, description="Maximum number of retries"
    )
    retry_delay: float = Field(
        default=0.5, description="Delay between retries"
    )
    retry_backoff: float = Field(
        default=2, description="Backoff factor for retry delay"
    )


class StrategyParams(SchemaModel):
    """Base parameters for execution strategies."""

    instruct: list[Instruct] | Instruct = Field(
        ..., description="Instructions to execute"
    )
    session: Session | None = Field(
        default=None, description="Session for managing branches"
    )
    branch: Branch | str | None = Field(
        default=None, description="Branch or branch reference for execution"
    )
    verbose: bool = Field(
        default=True, description="Whether to print execution progress"
    )
    execute_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional keyword arguments for execution",
    )
    branch_kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Keyword arguments for creating new branches",
    )
    auto_run: bool = False
    auto_execute: bool = False
    instruct_model_field: type[FieldModel] = LIST_INSTRUCT_FIELD_MODEL

    @field_validator("branch_kwargs", mode="before")
    def _validate_branch_kwargs(cls, v: Any) -> dict:
        if v is None:
            return {}
        if hasattr(v, "to_dict"):
            return v.to_dict()
        if isinstance(v, dict):
            return v
        raise ValueError("branch_kwargs must be a dictionary or SchemaModel")

    @field_validator("instruct", mode="before")
    def validate_instructions(cls, v: Any) -> list[Instruct]:
        """Validate and convert instructions to list format."""
        if isinstance(v, Instruct):
            return [v]
        if isinstance(v, (list, tuple)):
            if not all(isinstance(i, Instruct) for i in v):
                raise ValueError("All instructions must be Instruct instances")
            return list(v)
        raise ValueError("Instructions must be Instruct or list of Instruct")

    @field_validator("branch", mode="before")
    def validate_branch(cls, v: Any) -> Branch | str | None:
        """Validate branch reference."""
        if v is None or isinstance(v, (Branch, str)):
            return v
        raise ValueError("Branch must be a Branch instance or branch ID")

    @field_validator("session", mode="before")
    def validate_session(cls, v: Any) -> Session | None:
        """Validate session reference."""
        if v is None or isinstance(v, Session):
            return v
        raise ValueError("Session must be a Session instance")

    @model_validator(mode="after")
    def _validate_session_branch(self):
        if self.session is None:
            self.session = Session()
        if self.branch is None:
            self.branch = self.session.new_branch(**self.branch_kwargs)
        elif isinstance(self.branch, Branch):
            if self.branch not in self.session.branches:
                self.session.branches.include(self.branch)
        elif isinstance(self.branch, str):
            if self.branch not in self.session.branches:
                raise ValueError("Branch ID not found in session")
            self.branch = self.session.branches[self.branch]
        return self


class ChunkStrategyParams(StrategyParams):
    """Parameters for chunked execution strategies."""

    chunk_size: int = Field(
        default=5,
        description="Number of instructions to process in each chunk",
        gt=0,
    )
    rcall_params: RCallParams = Field(default_factory=RCallParams)

    @field_validator("rcall_params", mode="before")
    def validate_rcall_params(cls, v: dict) -> RCallParams:
        return RCallParams(**v)


class HybridStrategyParams(ChunkStrategyParams):
    """Parameters for hybrid execution strategies."""

    outer_mode: Literal["concurrent", "sequential"] = Field(
        ..., description="Execution mode for outer loop"
    )
    inner_mode: Literal["concurrent", "sequential"] = Field(
        ..., description="Execution mode for inner loop"
    )
    inner_chunk_size: int | None = Field(
        default=None, description="Chunk size for inner loop execution", gt=0
    )
    inner_rcall_params: RCallParams = Field(default_factory=RCallParams)

    @field_validator("inner_chunk_size", mode="before")
    def validate_inner_chunk_size(cls, v: Any) -> int | None:
        if v is None:
            return None
        if not isinstance(v, int) or v <= 0:
            raise ValueError("inner_chunk_size must be a positive integer")
        return v

    @field_validator("inner_rcall_params", mode="before")
    def validate_inner_rcall_params(cls, v: dict):
        return RCallParams(**v)
