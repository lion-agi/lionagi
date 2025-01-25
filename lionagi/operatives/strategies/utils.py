# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from lionagi.operatives.instruct.instruct import Instruct
from lionagi.session.session import Branch, Session
from lionagi.utils import alcall


async def run_instruct(
    ins: Instruct,
    session: Session,
    branch: Branch,
    auto_run: bool,
    verbose: bool = True,
    **kwargs: Any,
) -> Any:
    async def run(ins_):
        if verbose:
            msg_ = (
                ins_.instruction[:100] + "..."
                if len(ins_.instruction) > 100
                else ins_.instruction
            )
            print(f"\n-----Running instruction-----\n{msg_}")
        b_ = session.split(branch)
        return await run_instruct(
            ins_, session, b_, False, verbose=verbose, **kwargs
        )

    config = {**ins.model_dump(), **kwargs}
    res = await branch.operate(**config)
    branch.msgs.logger.dump()
    instructs = []

    if hasattr(res, "instruct_models"):
        instructs = res.instruct_models

    if auto_run is True and instructs:
        ress = await alcall(instructs, run)
        response_ = []
        for res in ress:
            if isinstance(res, list):
                response_.extend(res)
            else:
                response_.append(res)
        response_.insert(0, res)
        return response_

    return res
