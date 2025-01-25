# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import ClassVar

from pydantic import BaseModel, model_validator

from lionagi.operatives.instruct.instruct import Instruct, InstructResponse
from lionagi.session.session import Branch, Session

from .params import StrategyParams


class StrategyExecutor(BaseModel):
    """Base class for different execution strategies.

    Each concrete executor should implement `execute()` to run instructions
    according to a specific strategy (e.g., sequential, concurrent, chunked).
    """

    session: Session = None
    branch: Branch = None
    execute_branch: Branch = None
    params: StrategyParams = None
    params_cls: ClassVar[type[StrategyParams]] = StrategyParams

    @model_validator(mode="before")
    def validate_execution_config(cls, values: dict) -> dict:
        params_cls = values.get("params_cls", cls.params_cls)
        params = values.get("params", None)

        if isinstance(params, dict):
            params = params_cls(**params)
        if not isinstance(params, StrategyParams):
            params = params_cls(**values)

        session: Session = values.get("session", params.session)
        branch = values.get("branch", params.branch)
        execute_branch = values.get("execute_branch", None) or session.split(
            branch
        )

        return {
            "params": params,
            "session": session,
            "branch": branch,
            "execute_branch": execute_branch,
            "params_cls": params_cls,
        }

    async def execute(
        self, res
    ) -> tuple[list[Instruct], list[InstructResponse]]:
        """Run the instructions based on the strategy implemented by subclasses."""
        raise NotImplementedError
