# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.operatives.instruct.instruct import Instruct, InstructResponse

from .base import StrategyExecutor


class SequentialExecutor(StrategyExecutor):
    """Executor that runs instructions sequentially, one after another."""

    async def execute(
        self, res
    ) -> tuple[list[Instruct], list[InstructResponse]]:
        ress = []
        instructs = (
            res.instruct_models if hasattr(res, "instruct_models") else []
        )
        for idx, item in enumerate(instructs, start=1):
            if self.params.verbose:
                print(f"\nExecuting step {idx}/{len(instructs)}")
            out = await self.execute_branch.instruct(
                item, **self.params.execute_kwargs
            )
            ress.append(InstructResponse(instruct=item, response=out))
        return instructs, ress
