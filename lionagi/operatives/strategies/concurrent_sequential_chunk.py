# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from pydantic import model_validator

from lionagi.operatives.instruct.instruct import Instruct, InstructResponse
from lionagi.session.session import Branch, Session
from lionagi.utils import alcall

from .base import StrategyExecutor
from .params import HybridStrategyParams


class ConcurrentSequentialChunkExecutor(StrategyExecutor):
    """Concurrent-sequential chunked executor:
    1. Splits instructions into chunks
    2. Processes chunks concurrently
    3. Processes each instruction within a chunk sequentially.
    """

    params: HybridStrategyParams
    session: Session
    branch: Branch

    @model_validator(mode="before")
    def validate_execution_config(cls, values: dict) -> dict:
        params = values.get("params", None)
        if params is None:
            params = HybridStrategyParams(**values)

        if (
            params.outer_mode != "concurrent"
            or params.inner_mode != "sequential"
        ):
            raise ValueError(
                "Requires outer_mode='concurrent' and inner_mode='sequential'"
            )

        session = values.get("session", params.session)
        if not session:
            raise ValueError("Session is required")
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
            print(
                f"\n-----Executing Instruct {idx}/{ttl}-----\n{msg_}"
                if ttl
                else f"\n-----Executing Instruct {idx}-----\n{msg_}"
            )

        res = await self.branch.instruct(ins_, **self.params.execute_kwargs)
        return InstructResponse(instruct=ins_, response=res)

    async def _execute_chunk(
        self, chunk: list[tuple[Instruct, int, int]]
    ) -> list[InstructResponse]:
        # Each chunk sequential
        branch = self.session.split(self.branch)
        responses = []
        for ins_, idx, ttl in chunk:
            r = await self._execute_single(ins_, idx, ttl)
            responses.append(r)
        return responses

    async def execute(self) -> list[InstructResponse]:
        instructions = self.params.instruct
        chunk_size = self.params.chunk_size
        total = len(instructions)

        if total <= chunk_size:
            chunk = [(ins, i + 1, total) for i, ins in enumerate(instructions)]
            return await self._execute_chunk(chunk)

        chunks = []
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = [
                (instructions[i], i + 1, total) for i in range(start, end)
            ]
            chunks.append(chunk)

        chunk_responses = await alcall(
            chunks, self._execute_chunk, max_workers=self.params.max_workers
        )
        responses = []
        for c in chunk_responses:
            responses.extend(c)
        return responses
