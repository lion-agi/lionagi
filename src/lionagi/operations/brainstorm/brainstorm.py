# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from pydantic import BaseModel

from lionagi.libs.async_utils import alcall
from lionagi.protocols.base import ID
from lionagi.session.session import Branch, Session
from lionagi.utils import to_list

from ..fields.instruct import INSTRUCT_FIELD_MODEL, Instruct, InstructResponse
from ..utils import prepare_instruct, prepare_session
from .get_prompt import BrainStormTemplate, get_prompt


class BrainstormOperation(BaseModel):
    initial: Any
    brainstorm: list[Instruct] | None = None
    explore: list[InstructResponse] | None = None


async def run_instruct(
    ins: Instruct,
    session: Session,
    branch: Branch,
    auto_run: bool,
    verbose: bool = True,
    **kwargs: Any,
) -> Any:
    """Execute an instruction within a brainstorming session.

    Args:
        ins: The instruction model to run.
        session: The current session.
        branch: The branch to operate on.
        auto_run: Whether to automatically run nested instructions.
        verbose: Whether to enable verbose output.
        **kwargs: Additional keyword arguments.

    Returns:
        The result of the instruction execution.
    """

    async def run(ins_):
        if verbose:
            msg_ = (
                ins_.guidance[:100] + "..."
                if len(ins_.guidance) > 100
                else ins_.guidance
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


async def brainstorm(
    instruct: Instruct | dict[str, Any],
    num_instruct: int = 2,
    session: Session | None = None,
    branch: Branch | ID.Ref | None = None,
    auto_run: bool = True,
    auto_explore: bool = False,
    explore_kwargs: dict[str, Any] | None = None,
    branch_kwargs: dict[str, Any] | None = None,
    return_session: bool = False,
    verbose: bool = False,
    template: BrainStormTemplate = BrainStormTemplate.DEFAULT,
    template_context: dict[str, Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Perform a brainstorming session.

    Args:
        instruct: Instruction model or dictionary.
        num_instruct: Number of instructions to generate.
        session: Existing session or None to create a new one.
        branch: Existing branch or reference.
        auto_run: If True, automatically run generated instructions.
        branch_kwargs: Additional arguments for branch creation.
        return_session: If True, return the session with results.
        verbose: Whether to enable verbose output.
        **kwargs: Additional keyword arguments.

    Returns:
        The results of the brainstorming session, optionally with the session.
    """

    if auto_explore and not auto_run:
        raise ValueError("auto_explore requires auto_run to be True.")

    if verbose:
        print(f"Starting brainstorming...")

    field_models: list = kwargs.get("field_models", [])
    if INSTRUCT_FIELD_MODEL not in field_models:
        field_models.append(INSTRUCT_FIELD_MODEL)

    kwargs["field_models"] = field_models
    session, branch = prepare_session(session, branch, branch_kwargs)
    prompt = get_prompt(template, num_instruct=num_instruct)
    instruct = prepare_instruct(instruct, prompt, **(template_context or {}))

    res1 = await branch.operate(**instruct, **kwargs)
    out = BrainstormOperation(initial=res1)

    if verbose:
        print("Initial brainstorming complete.")

    instructs = None

    async def run(ins_):
        if verbose:
            msg_ = (
                ins_.guidance[:100] + "..."
                if len(ins_.guidance) > 100
                else ins_.guidance
            )
            print(f"\n-----Running instruction-----\n{msg_}")
        b_ = session.split(branch)
        return await run_instruct(
            ins_, session, b_, auto_run, verbose=verbose, **kwargs
        )

    if not auto_run:
        if return_session:
            return out, session
        return out

    async with session.branches:
        response_ = []
        if hasattr(res1, "instruct_models"):
            instructs: list[Instruct] = res1.instruct_models
            ress = await alcall(instructs, run)
            ress = to_list(ress, dropna=True, flatten=True)

            response_ = [
                res if not isinstance(res, str | dict) else None
                for res in ress
            ]
            response_ = to_list(
                response_, unique=True, dropna=True, flatten=True
            )
            out.brainstorm = (
                response_ if isinstance(response_, list) else [response_]
            )
            response_.insert(0, res1)

        if response_ and auto_explore:

            async def explore(ins_: Instruct):
                if verbose:
                    msg_ = (
                        ins_.guidance[:100] + "..."
                        if len(ins_.guidance) > 100
                        else ins_.guidance
                    )
                    print(f"\n-----Exploring Idea-----\n{msg_}")
                b_ = session.split(branch)
                res = await b_.instruct(ins_, **(explore_kwargs or {}))
                return InstructResponse(response=res, **ins_.model_dump())

            response_ = to_list(
                [
                    i.instruct_models
                    for i in response_
                    if hasattr(i, "instruct_models")
                ],
                dropna=True,
                unique=True,
                flatten=True,
            )
            res_explore = await alcall(response_, explore)
            out.explore = res_explore

    if return_session:
        return out, session

    return out
