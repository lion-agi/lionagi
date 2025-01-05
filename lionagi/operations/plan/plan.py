# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from pydantic import BaseModel

from lionagi.operatives.instruct.instruct import (
    LIST_INSTRUCT_FIELD_MODEL,
    Instruct,
    InstructResponse,
)
from lionagi.protocols.types import ID
from lionagi.session.branch import Branch
from lionagi.session.session import Session
from lionagi.utils import alcall

from ..utils import prepare_instruct, prepare_session
from .prompt import EXPANSION_PROMPT, PLAN_PROMPT

# ---------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------


class PlanOperation(BaseModel):
    """
    Stores all relevant outcomes for a multi-step Plan:
        * initial: The result of the initial plan prompt
        * plan: A list of plan steps (Instruct objects) generated from the initial planning
        * execute: Any responses from executing those plan steps
    """

    initial: Any
    plan: list[Instruct] | None = None
    execute: list[InstructResponse] | None = None


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------


def chunked(iterable, n):
    """
    Yield successive n-sized chunks from an iterable.
    Example:
        >>> list(chunked([1,2,3,4,5], 2))
        [[1,2],[3,4],[5]]
    """
    for i in range(0, len(iterable), n):
        yield iterable[i : i + n]


# ---------------------------------------------------------------------
# Single-Step Runner
# ---------------------------------------------------------------------


async def run_step(
    ins: Instruct,
    session: Session,
    branch: Branch,
    verbose: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Execute a single step of the plan with an 'expansion' or guidance prompt.

    Args:
        ins: The instruction model for the step.
        session: The current session context.
        branch: The branch to operate on for this step.
        verbose: Whether to enable verbose output.
        **kwargs: Additional keyword arguments passed to the branch operation.

    Returns:
        The result of the branch operation (which may contain more instructions).
    """
    if verbose:
        snippet = (
            ins.instruction[:100] + "..."
            if len(ins.instruction) > 100
            else ins.instruction
        )
        print(f"Further planning: {snippet}")

    # Incorporate the EXPANSION_PROMPT into guidance
    config = {**ins.model_dump(), **kwargs}
    guidance_text = config.pop("guidance", "")
    config["guidance"] = f"{EXPANSION_PROMPT}\n{guidance_text}"

    # Run the step
    result = await branch.operate(**config)
    branch.msgs.logger.dump()  # Dump logs if needed
    return result


# ---------------------------------------------------------------------
# Main Plan Function (with Multiple Execution Strategies)
# ---------------------------------------------------------------------


async def plan(
    instruct: Instruct | dict[str, Any],
    num_steps: int = 2,
    session: Session | None = None,
    branch: Branch | ID.Ref | None = None,
    auto_run: bool = True,
    auto_execute: bool = False,
    execution_strategy: Literal[
        "sequential",
        "concurrent",
        "sequential_concurrent_chunk",
        "concurrent_sequential_chunk",
    ] = "sequential",
    execution_kwargs: dict[str, Any] | None = None,
    branch_kwargs: dict[str, Any] | None = None,
    return_session: bool = False,
    verbose: bool = True,
    **kwargs: Any,
) -> PlanOperation | tuple[PlanOperation, Session]:
    """
    Create and optionally execute a multi-step plan with up to `num_steps`.

    Steps:
      1. Generate an initial plan with up to `num_steps`.
      2. Optionally (auto_run=True) expand on each planned step
         to refine or further clarify them.
      3. Optionally (auto_execute=True) execute those refined steps
         according to `execution_strategy`.

    Args:
        instruct: Initial instruction or a dict describing it.
        num_steps: Maximum number of plan steps (must be <= 5).
        session: An existing Session, or None to create a new one.
        branch: An existing Branch, or None to create a new one.
        auto_run: If True, automatically run the intermediate plan steps.
        auto_execute: If True, automatically execute the fully refined steps.
        execution_strategy:
            - "sequential" (default) runs steps one by one
            - "concurrent" runs all steps in parallel
            - "sequential_concurrent_chunk" processes chunks sequentially, each chunk in parallel
            - "concurrent_sequential_chunk" processes all chunks in parallel, each chunk sequentially
        execution_kwargs: Extra kwargs used during execution calls.
        branch_kwargs: Extra kwargs for branch/session creation.
        return_session: Whether to return (PlanOperation, Session) instead of just PlanOperation.
        verbose: If True, prints verbose logs.
        **kwargs: Additional arguments for the initial plan operation.

    Returns:
        A PlanOperation object containing:
            - initial plan
            - (optional) plan expansions
            - (optional) execution responses
        Optionally returns the session as well, if `return_session=True`.
    """

    # -----------------------------------------------------------------
    # 0. Basic Validation & Setup
    # -----------------------------------------------------------------
    if num_steps > 5:
        raise ValueError("Number of steps must be 5 or less")

    if verbose:
        print(f"Planning execution with {num_steps} steps...")

    # Ensure the correct field model
    field_models: list = kwargs.get("field_models", [])
    if LIST_INSTRUCT_FIELD_MODEL not in field_models:
        field_models.append(LIST_INSTRUCT_FIELD_MODEL)
    kwargs["field_models"] = field_models

    # Prepare session/branch
    session, branch = prepare_session(session, branch, branch_kwargs)
    execute_branch: Branch = session.split(
        branch
    )  # a separate branch for execution

    # -----------------------------------------------------------------
    # 1. Run the Initial Plan Prompt
    # -----------------------------------------------------------------
    plan_prompt = PLAN_PROMPT.format(num_steps=num_steps)
    instruct = prepare_instruct(instruct, plan_prompt)
    initial_res = await branch.operate(**instruct, **kwargs)

    # Wrap initial result in the PlanOperation
    out = PlanOperation(initial=initial_res)

    if verbose:
        print("Initial planning complete. Starting step planning...")

    # If we aren't auto-running the steps, just return the initial plan
    if not auto_run:
        return (out, session) if return_session else out

    # -----------------------------------------------------------------
    # 2. Expand Each Step (auto_run=True)
    # -----------------------------------------------------------------
    results = []
    if hasattr(initial_res, "instruct_models"):
        instructs: list[Instruct] = initial_res.instruct_models
        for i, step_ins in enumerate(instructs, start=1):
            if verbose:
                print(f"\n----- Planning step {i}/{len(instructs)} -----")
            expanded_res = await run_step(
                step_ins, session, branch, verbose=verbose, **kwargs
            )
            results.append(expanded_res)

        if verbose:
            print("\nAll planning steps expanded/refined successfully!")

    # Gather all newly created plan instructions
    refined_plans = []
    for step_result in results:
        if hasattr(step_result, "instruct_models"):
            for model in step_result.instruct_models:
                if model and model not in refined_plans:
                    refined_plans.append(model)

    out.plan = refined_plans

    # -----------------------------------------------------------------
    # 3. Execute the Plan Steps (auto_execute=True)
    # -----------------------------------------------------------------
    if auto_execute:
        if verbose:
            print("\nStarting execution of all plan steps...")

        # We now handle multiple strategies:
        match execution_strategy:

            # ---------------------------------------------------------
            # Strategy A: SEQUENTIAL
            # ---------------------------------------------------------
            case "sequential":
                seq_results = []
                for i, plan_step in enumerate(refined_plans, start=1):
                    if verbose:
                        snippet = (
                            plan_step.instruction[:100] + "..."
                            if len(plan_step.instruction) > 100
                            else plan_step.instruction
                        )
                        print(
                            f"\n------ Executing step {i}/{len(refined_plans)} ------"
                        )
                        print(f"Instruction: {snippet}")

                    step_response = await execute_branch._instruct(
                        plan_step, **(execution_kwargs or {})
                    )
                    seq_results.append(
                        InstructResponse(
                            instruct=plan_step, response=step_response
                        )
                    )

                out.execute = seq_results
                if verbose:
                    print("\nAll steps executed successfully (sequential)!")

            # ---------------------------------------------------------
            # Strategy B: CONCURRENT
            # ---------------------------------------------------------
            case "concurrent":

                async def execute_step_concurrently(plan_step: Instruct):
                    if verbose:
                        snippet = (
                            plan_step.instruction[:100] + "..."
                            if len(plan_step.instruction) > 100
                            else plan_step.instruction
                        )
                        print(f"\n------ Executing step (concurrently) ------")
                        print(f"Instruction: {snippet}")
                    local_branch = session.split(execute_branch)
                    resp = await local_branch._instruct(
                        plan_step, **(execution_kwargs or {})
                    )
                    return InstructResponse(instruct=plan_step, response=resp)

                # Launch all steps in parallel
                concurrent_res = await alcall(
                    refined_plans, execute_step_concurrently
                )
                out.execute = concurrent_res
                if verbose:
                    print("\nAll steps executed successfully (concurrent)!")

            # ---------------------------------------------------------
            # Strategy C: SEQUENTIAL_CONCURRENT_CHUNK
            #   - process plan steps in chunks (one chunk after another),
            #   - each chunk’s steps run in parallel.
            # ---------------------------------------------------------
            case "sequential_concurrent_chunk":
                chunk_size = (execution_kwargs or {}).get("chunk_size", 5)
                all_exec_responses = []

                async def execute_chunk_concurrently(
                    sub_steps: list[Instruct],
                ):
                    if verbose:
                        print(
                            f"\n--- Executing a chunk of size {len(sub_steps)} concurrently ---"
                        )

                    async def _execute(plan_step: Instruct):
                        local_branch = session.split(execute_branch)
                        resp = await local_branch._instruct(
                            plan_step, **(execution_kwargs or {})
                        )
                        return InstructResponse(
                            instruct=plan_step, response=resp
                        )

                    # run each chunk in parallel
                    return await alcall(sub_steps, _execute)

                # process each chunk sequentially
                for chunk in chunked(refined_plans, chunk_size):
                    chunk_responses = await execute_chunk_concurrently(chunk)
                    all_exec_responses.extend(chunk_responses)

                out.execute = all_exec_responses
                if verbose:
                    print(
                        "\nAll steps executed successfully (sequential concurrent chunk)!"
                    )

            # ---------------------------------------------------------
            # Strategy D: CONCURRENT_SEQUENTIAL_CHUNK
            #   - split plan steps into chunks,
            #   - run all chunks in parallel,
            #   - but each chunk’s steps run sequentially.
            # ---------------------------------------------------------
            case "concurrent_sequential_chunk":
                chunk_size = (execution_kwargs or {}).get("chunk_size", 5)
                all_chunks = list(chunked(refined_plans, chunk_size))

                async def execute_chunk_sequentially(
                    sub_steps: list[Instruct],
                ):
                    chunk_result = []
                    local_branch = session.split(execute_branch)
                    for plan_step in sub_steps:
                        if verbose:
                            snippet = (
                                plan_step.instruction[:100] + "..."
                                if len(plan_step.instruction) > 100
                                else plan_step.instruction
                            )
                            print(
                                f"\n--- Executing step (sequential in chunk) ---\nInstruction: {snippet}"
                            )
                        resp = await local_branch._instruct(
                            plan_step, **(execution_kwargs or {})
                        )
                        chunk_result.append(
                            InstructResponse(instruct=plan_step, response=resp)
                        )
                    return chunk_result

                # run all chunks in parallel, each chunk sequentially
                parallel_chunk_results = await alcall(
                    all_chunks,
                    execute_chunk_sequentially,
                    flatten=True,
                    dropna=True,
                )

                out.execute = parallel_chunk_results
                if verbose:
                    print(
                        "\nAll steps executed successfully (concurrent sequential chunk)!"
                    )

            case _:
                raise ValueError(
                    f"Invalid execution strategy: {execution_strategy}"
                )

    # -----------------------------------------------------------------
    # 4. Final Return
    # -----------------------------------------------------------------
    return (out, session) if return_session else out
