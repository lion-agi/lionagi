# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


from lionagi.core.session.branch import Branch
from lionagi.core.session.session import Session
from lionagi.core.typing import ID, Any, BaseModel, Literal
from lionagi.protocols.operatives.instruct import (
    INSTRUCT_MODEL_FIELD,
    Instruct,
    InstructResponse,
)

from ..utils import prepare_instruct, prepare_session
from .prompt import EXPANSION_PROMPT, PLAN_PROMPT


class PlanOperation(BaseModel):
    initial: Any
    plan: list[Instruct] | None = None
    execute: list[InstructResponse] | None = None


async def run_step(
    ins: Instruct,
    session: Session,
    branch: Branch,
    verbose: bool = True,
    **kwargs: Any,
) -> Any:
    """Execute a single step of the plan.

    Args:
        ins: The instruction model for the step.
        session: The current session.
        branch: The branch to operate on.
        verbose: Whether to enable verbose output.
        **kwargs: Additional keyword arguments.

    Returns:
        The result of the branch operation.
    """
    if verbose:
        instruction = (
            ins.instruction[:100] + "..."
            if len(ins.instruction) > 100
            else ins.instruction
        )
        print(f"Further planning: {instruction}")

    config = {**ins.model_dump(), **kwargs}
    guide = config.pop("guidance", "")
    config["guidance"] = EXPANSION_PROMPT + "\n" + str(guide)

    res = await branch.operate(**config)
    branch.msgs.logger.dump()
    return res


async def plan(
    instruct: Instruct | dict[str, Any],
    num_steps: int = 2,
    session: Session | None = None,
    branch: Branch | ID.Ref | None = None,
    auto_run: bool = True,
    auto_execute: bool = False,
    execution_strategy: Literal["sequential"] = "sequential",
    execution_kwargs: dict[str, Any] | None = None,
    branch_kwargs: dict[str, Any] | None = None,
    return_session: bool = False,
    verbose: bool = True,
    **kwargs: Any,
) -> PlanOperation | tuple[list[InstructResponse], Session]:
    """Create and execute a multi-step plan.

    Args:
        instruct: Instruction model or dictionary.
        num_steps: Number of steps in the plan.
        session: Existing session or None to create a new one.
        branch: Existing branch or reference.
        auto_run: If True, automatically run the steps.
        branch_kwargs: Additional keyword arguments for branch creation.
        return_session: If True, return the session along with results.
        verbose: Whether to enable verbose output.
        **kwargs: Additional keyword arguments.

    Returns:
        Results of the plan execution, optionally with the session.
    """
    if num_steps > 5:
        raise ValueError("Number of steps must be 5 or less")

    if verbose:
        print(f"Planning execution with {num_steps} steps...")

    field_models: list = kwargs.get("field_models", [])
    if INSTRUCT_MODEL_FIELD not in field_models:
        field_models.append(INSTRUCT_MODEL_FIELD)
    kwargs["field_models"] = field_models
    session, branch = prepare_session(session, branch, branch_kwargs)
    execute_branch: Branch = session.split(branch)
    instruct = prepare_instruct(
        instruct, PLAN_PROMPT.format(num_steps=num_steps)
    )

    res1 = await branch.operate(**instruct, **kwargs)
    out = PlanOperation(initial=res1)

    if verbose:
        print("Initial planning complete. Starting step planning...")

    if not auto_run:
        if return_session:
            return res1, session
        return res1

    results = []
    if hasattr(res1, "instruct_models"):
        instructs: list[Instruct] = res1.instruct_models
        for i, ins in enumerate(instructs, 1):
            if verbose:
                print(f"\n----- Planning step {i}/{len(instructs)} -----")
            res = await run_step(
                ins, session, branch, verbose=verbose, **kwargs
            )
            results.append(res)

        if verbose:
            print("\nAll planning completed successfully!")

    all_plans = []
    for res in results:
        if hasattr(res, "instruct_models"):
            for i in res.instruct_models:
                if i and i not in all_plans:
                    all_plans.append(i)
    out.plan = all_plans

    if auto_execute:
        if verbose:
            print("\nStarting execution of all steps...")
        results = []
        match execution_strategy:
            case "sequential":
                for i, ins in enumerate(all_plans, 1):
                    if verbose:
                        print(
                            f"\n------ Executing step {i}/{len(all_plans)} ------"
                        )
                        msg = (
                            ins.instruction[:100] + "..."
                            if len(ins.instruction) > 100
                            else ins.instruction
                        )
                        print(f"Instruction: {msg}")
                    res = await execute_branch.instruct(
                        ins, **(execution_kwargs or {})
                    )
                    res_ = InstructResponse(instruct=ins, response=res)
                    results.append(res_)
                out.execute = results
                if verbose:
                    print("\nAll steps executed successfully!")
            case _:
                raise ValueError(
                    f"Invalid execution strategy: {execution_strategy}"
                )

    if return_session:
        return out, session
    return out
