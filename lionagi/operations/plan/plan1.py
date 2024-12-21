# plan.py
# ------------------------------------------------------------------
# This module demonstrates how to implement your "plan" function
# using the new strategy-based execution system. It includes:
#  1) A PlanOperation class (subclass of Task)
#  2) The plan(...) function that uses ExecutionController
#  3) Utility methods like run_step
#  4) The relevant prompts (PLAN_PROMPT, EXPANSION_PROMPT)
# ------------------------------------------------------------------

from typing import Any, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field

from lionagi.core.session.session import Branch, Session
from lionagi.core.typing import ID
from lionagi.operations.strategies.strategy import Strategy
from lionagi.protocols.operatives.instruct import (
    INSTRUCT_FIELD_MODEL,
    Instruct,
    InstructResponse,
)

# ---------------------------------------------------------
# 1) New Approach Imports
# ---------------------------------------------------------
from lionagi.protocols.operatives.tasks import OperationType, Task
from lionagi.strategies.controller import ExecutionController
from lionagi.strategies.types import StrategyParams

# ---------------------------------------------------------
# 2) Prompts
# ---------------------------------------------------------
PLAN_PROMPT = """
Develop a high-level plan with {num_steps} distinct steps. Each step should:
1. Represent a major milestone or phase
2. Be logically sequenced for dependencies
3. Be clearly distinct from other steps
4. Have measurable completion criteria
5. Be suitable for further decomposition
"""

EXPANSION_PROMPT = """
Break down a high-level plan into detailed concrete executable actions. Each step should:
- Ensure actions are atomic and verifiable
- Include necessary context and preconditions
- Specify expected outcomes and validations
- Maintain sequential dependencies
- Be self-contained with clear scope
- Include all required context/parameters
- Have unambiguous success criteria
- Specify error handling approach
- Define expected outputs
"""


# ---------------------------------------------------------
# 3) A "PlanOperation" that extends Task
# ---------------------------------------------------------
class PlanOperation(Task):
    """
    Represents a plan operation that includes:
    - The initial instruct result
    - A list of plan steps (Instruct)
    - An optional list of executed steps (InstructResponse)
    """

    # Overriding op_type to 'PLAN'
    op_type: OperationType = Field(default=OperationType.PLAN, const=True)

    initial: Any
    plan: list[Instruct] | None = None
    execute: list[InstructResponse] | None = None


# ---------------------------------------------------------
# 4) Helper: run_step (similar to your existing run_step function)
# ---------------------------------------------------------
async def run_step(
    ins: Instruct,
    session: Session,
    branch: Branch,
    verbose: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Execute a single step of the plan by operating on the branch,
    optionally printing verbose messages.
    """
    if verbose:
        instruction_text = ins.instruction
        if (
            instruction_text
            and isinstance(instruction_text, str)
            and len(instruction_text) > 100
        ):
            instruction_text = instruction_text[:100] + "..."
        print(f"Further planning: {instruction_text}")

    # Merge guidance with EXPANSION_PROMPT
    config = {**ins.model_dump(), **kwargs}
    guide = config.pop("guidance", "")
    config["guidance"] = EXPANSION_PROMPT + "\n" + str(guide)

    # Perform a direct operation on the branch
    res = await branch.operate(**config)
    branch.msgs.logger.dump()
    return res


# ---------------------------------------------------------
# 5) The main "plan" function that orchestrates everything
# ---------------------------------------------------------
async def plan(
    instruct: Instruct | dict[str, Any],
    num_steps: int = 2,
    session: Session | None = None,
    branch: Branch | ID.Ref | None = None,
    auto_run: bool = True,
    auto_execute: bool = False,
    execution_strategy: Literal[
        "sequential", "concurrent", "chunked", "hybrid"
    ] = "sequential",
    execution_kwargs: dict[str, Any] | None = None,
    branch_kwargs: dict[str, Any] | None = None,
    return_session: bool = False,
    verbose: bool = True,
    **kwargs: Any,
) -> PlanOperation | tuple[PlanOperation, Session]:
    """
    Create and execute a multi-step plan using the new strategy-based system.

    1) We first generate an initial plan (via PLAN_PROMPT).
    2) If auto_run=True, we expand each step with run_step(...) for further detail.
    3) If auto_execute=True, we then execute those steps using the chosen strategy.

    Returns a PlanOperation object with the initial result, expanded plan, and optional execution results.
    """
    # Safety check
    if num_steps > 5:
        raise ValueError("Number of steps must be 5 or less")

    if verbose:
        print(f"[plan] Creating a plan with {num_steps} steps...")

    # Ensure we have a session & branch
    if session is None:
        session = Session()
    if not isinstance(branch, Branch):
        branch = Branch(session=session, name="PlanBranch")

    # Make sure the 'instruct' is an Instruct or convert it
    if isinstance(instruct, dict):
        instruct = Instruct.model_validate(instruct)

    # Insert the default instruct field model if not provided
    field_models: list = kwargs.get("field_models", [])
    if INSTRUCT_FIELD_MODEL not in field_models:
        field_models.append(INSTRUCT_FIELD_MODEL)
    kwargs["field_models"] = field_models

    # Merge PLAN_PROMPT
    if instruct.instruction is None:
        instruct.instruction = ""
    instruct.instruction = (
        f"{instruct.instruction}\n{PLAN_PROMPT.format(num_steps=num_steps)}"
    )

    # Operate for initial plan
    if verbose:
        print("[plan] Generating initial plan...")
    res1 = await branch.operate(**instruct.model_dump(), **kwargs)

    # Build output
    out = PlanOperation(
        ln_id="plan-op", payload={"num_steps": num_steps}, initial=res1
    )

    # If not auto_run, we return now
    if not auto_run:
        if return_session:
            return out, session
        return out

    # Expand each step (run_step calls)
    if verbose:
        print("[plan] Auto-run is True, expanding each step...")

    # Collect results
    results = []
    if hasattr(res1, "instruct_models"):
        plan_instructs: list[Instruct] = res1.instruct_models
        for i, ins in enumerate(plan_instructs, 1):
            if verbose:
                print(f"\n----- Planning step {i}/{len(plan_instructs)} -----")
            step_result = await run_step(
                ins=ins,
                session=session,
                branch=branch,
                verbose=verbose,
                **kwargs,
            )
            results.append(step_result)
        if verbose:
            print("\nAll planning steps expanded successfully!")

    # Collect all final plan instructs
    all_plans = []
    for res_item in results:
        if hasattr(res_item, "instruct_models"):
            for step_instruct in res_item.instruct_models:
                if step_instruct and step_instruct not in all_plans:
                    all_plans.append(step_instruct)
    out.plan = all_plans

    # Optionally auto-execute
    if auto_execute and all_plans:
        if verbose:
            print(
                "\n[plan] Auto-execute is True. Executing all steps with strategy:",
                execution_strategy,
            )

        # Build a new StrategyOperative to hold the final plan
        plan_operative = Strategy(
            name="PlanExecutionOperative",
            description="Execution for final plan steps.",
        )
        for step_instruct in all_plans:
            # Convert each step_instruct to a 'Task' if needed
            # We can store them as tasks with 'PlanOperation' or something simpler
            # For demonstration, we keep it as a default 'Task'
            plan_operative.add_operation(
                Task(
                    ln_id=step_instruct.ln_id,
                    payload=step_instruct.dict(),
                    op_type=OperationType.PLAN,
                )
            )

        # Create an ExecutionController and define StrategyParams
        controller = ExecutionController()
        exec_params = StrategyParams()
        exec_params_dict = execution_kwargs or {}
        for k, v in exec_params_dict.items():
            setattr(exec_params, k, v)

        # Actually execute with the chosen strategy
        # We pass the 'execution_strategy' by updating exec_params if you want,
        # or rely on the dynamic strategy selection logic.
        # For now, we keep it simple: the dynamic logic is governed by your factory scores.
        # You could also force "sequential" etc. by custom weighting.

        # We need a new branch for actual execution or reuse the old one
        exec_branch = session.split(branch)
        result = await controller.execute_with_strategy(
            operative=plan_operative,
            session=session,
            branch=exec_branch,
            strategy_params=exec_params,
        )

        # Convert result into InstructResponses
        # The result is typically (list_of_tasks, list_of_responses)
        if isinstance(result, tuple) and len(result) == 2:
            tasks_, responses_ = result
            # Convert them to InstructResponse
            executed_steps = []
            for t, r in zip(tasks_, responses_):
                if isinstance(t.payload, dict):
                    # Rebuild an Instruct object
                    temp_instruct = Instruct.model_validate(t.payload)
                    executed_steps.append(
                        InstructResponse(instruct=temp_instruct, response=r)
                    )
                else:
                    # If not an Instruct, store partial info
                    executed_steps.append(
                        InstructResponse(instruct=Instruct(), response=r)
                    )
            out.execute = executed_steps

        if verbose:
            print(
                "\n[plan] All plan steps executed successfully using strategy-based system!"
            )

    # Return final result
    if return_session:
        return out, session
    return out
