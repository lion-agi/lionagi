# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.operatives.instruct.instruct import Instruct, InstructResponse
from lionagi.session.session import Branch
from lionagi.utils import alcall, to_list

from .base import StrategyExecutor


class ConcurrentExecutor(StrategyExecutor):
    """Executor for concurrent instruction processing.

    Runs each instruction in parallel without chunking.
    """

    async def execute_instruct(
        self, ins: Instruct, branch: Branch, auto_run: bool, **kwargs
    ):
        async def run(ins_):
            if self.params.verbose:
                print(f"\n-----Running sub-instruction-----\n{ins_.msg}")
            b_ = self.session.split(branch)
            return await self.execute_instruct(ins_, b_, False, **kwargs)

        config = {**ins.model_dump(), **kwargs}
        res = await branch._instruct(**config)
        branch.msgs.logger.dump()
        instructs = (
            res.instruct_models if hasattr(res, "instruct_models") else []
        )

        if auto_run and instructs:
            ress = await alcall(instructs, run)
            response_ = []
            for r in ress:
                if isinstance(r, list):
                    response_.extend(r)
                else:
                    response_.append(r)
            response_.insert(0, res)
            return response_
        return res

    async def instruct_concurrent_single(
        self, ins_: Instruct, execute_branch: Branch
    ) -> InstructResponse:
        if self.params.verbose:
            print(f"\n-----Running instruction-----\n{ins_.msg}")
        b_ = self.session.split(execute_branch)
        response = await self.execute_instruct(
            ins_, b_, self.params.auto_run, **self.params.execute_kwargs
        )
        return InstructResponse(instruct=ins_, response=response)

    async def execute(
        self, res
    ) -> tuple[list[Instruct], list[InstructResponse]]:
        async with self.session.branches:
            response_ = []
            instructs = []
            if hasattr(res, "instruct_models"):
                instructs: list[Instruct] = res.instruct_models
                ress = await alcall(
                    instructs,
                    self.instruct_concurrent_single,
                    execute_branch=self.execute_branch,
                )
                ress = to_list(ress, dropna=True, flatten=True)
                response_ = [r for r in ress if not isinstance(r, (str, dict))]
                response_ = to_list(
                    response_, unique=True, dropna=True, flatten=True
                )
            return instructs, response_
