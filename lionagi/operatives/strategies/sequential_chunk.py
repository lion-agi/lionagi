# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import model_validator

from lionagi.operatives.instruct.instruct import Instruct, InstructResponse
from lionagi.session.session import Branch, Session

from .base import StrategyExecutor
from .params import ChunkStrategyParams


class SequentialChunkExecutor(StrategyExecutor):
    """Executor for sequential chunked instruction processing.

    Splits instructions into chunks and processes each chunk one by one.
    """

    params: ChunkStrategyParams
    session: Session
    branch: Branch

    @model_validator(mode="before")
    def validate_execution_config(cls, values: dict) -> dict:
        params = values.get("params", None)
        if params is None:
            params = ChunkStrategyParams(**values)

        session = values.get("session", params.session)
        if not session:
            raise ValueError(
                "Session is required for sequential chunk execution"
            )

        branch = values.get("branch", params.branch)
        if isinstance(branch, Branch):
            if branch not in session.branches:
                session.branches.include(branch)
        elif not branch:
            branch = session.new_branch()
        elif isinstance(branch, str):
            branch = session.split(branch)
        else:
            raise ValueError("Invalid branch type")

        return {"params": params, "session": session, "branch": branch}

    async def _execute_single(
        self, ins_: Instruct, idx: int, ttl: int
    ) -> InstructResponse:
        if self.params.verbose:
            msg_ = (
                (ins_.instruction[:100] + "...")
                if len(ins_.instruction) > 100
                else ins_.instruction
            )
            if idx and ttl:
                print(f"\n-----Executing Instruct {idx}/{ttl}-----\n{msg_}")
            else:
                print(f"\n-----Executing Instruct-----\n{msg_}")

        res = await self.branch._instruct(ins_, **self.params.execute_kwargs)
        return InstructResponse(instruct=ins_, response=res)

    async def _execute_chunk(
        self, chunk: list[tuple[Instruct, int, int]]
    ) -> list[InstructResponse]:
        responses = []
        for ins_, idx, ttl in chunk:
            res = await self._execute_single(ins_, idx, ttl)
            responses.append(res)
        return responses

    async def execute(self) -> list[InstructResponse]:
        instructions = self.params.instruct
        chunk_size = self.params.chunk_size
        total = len(instructions)

        if total <= chunk_size:
            chunk = [(ins, i + 1, total) for i, ins in enumerate(instructions)]
            return await self._execute_chunk(chunk)

        responses = []
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = [
                (instructions[i], i + 1, total) for i in range(start, end)
            ]
            chunk_responses = await self._execute_chunk(chunk)
            responses.extend(chunk_responses)

        return responses
