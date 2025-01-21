from typing import Any, TypeVar

from pydantic import BaseModel

from lionagi.session.branch import Branch

from .utils import (
    OptimizationForm,
    OptimizationResponse,
    OptimizationType,
    _apply_prompt_improvement,
    _evaluate_prompt,
    _generate_prompt_variations,
)

T = TypeVar("T", bound=BaseModel)


async def optimize(
    branch: Branch,
    *,
    target: OptimizationType | dict[str, Any],
    metrics: list[str] | None = None,
    constraints: dict[str, Any] | None = None,
    response_format: type[T] = None,
    **kwargs,
) -> OptimizationResponse | T:
    """
    **EXPERIMENTAL** !!!
    
    High-level function to optimize a certain aspect (PROMPT, FLOW, TOOLS, etc.)
    in the given Branch. Updates the Branch if it finds a better configuration.

    e.g. usage:
        response = await optimize(
            branch=some_branch,
            target=OptimizationType.PROMPT,
            metrics=["response_quality","token_usage"],
            constraints={"max_length":500},
            eval_instruction="Test with a question about X"
        )
    """

    # 1. Construct or parse the form
    if isinstance(target, dict):
        form = OptimizationForm(**target)
    else:
        form = OptimizationForm(
            target=target,
            metrics=metrics or [],
            constraints=constraints or {},
            **kwargs,
        )
    form.check_completeness(how="raise")  # ensure required fields are valid

    # 2. Based on the target, do specialized logic
    original_config = {}
    variations = []
    best_config = {}
    best_scores_sum = float("-inf")
    best_scores = {}

    if form.target == OptimizationType.PROMPT:
        # We'll treat the Branch's system + partial instructions as the base
        original_config = {
            "system": branch.msgs.get_system(),
            "instruction_template": form.template or "",  # from form
            "guidance_template": "",  # optional
        }

        # Generate variations
        variations = _generate_prompt_variations(original_config)

        # Evaluate each variation
        results = []
        for i, var in enumerate(variations):
            score_dict = await _evaluate_prompt(
                branch=branch,
                prompt_config=var,
                eval_instruction=form.eval_instruction,
                metrics=form.metrics,
            )
            sum_scores = sum(score_dict.values())
            results.append((var, score_dict, sum_scores))

        # Find best
        if results:
            best_var, best_sd, best_sum = max(results, key=lambda x: x[2])
            best_config = best_var
            best_scores = best_sd
            best_scores_sum = best_sum

        # Actually apply it
        _apply_prompt_improvement(branch, best_config)

        # Calculate improvements from the first variation as baseline
        baseline_scores = results[0][1] if results else {}
        improvements = {}
        for m in best_scores:
            if m in baseline_scores:
                improvements[m] = best_scores[m] - baseline_scores[m]
            else:
                improvements[m] = best_scores[m]

        response = OptimizationResponse(
            original=original_config,
            optimized=best_config,
            improvements=improvements,
            steps_taken=len(variations),
            metadata={"best_scores_sum": best_scores_sum},
        )

    elif form.target == OptimizationType.FLOW:
        # TODO: implement real logic
        # As an example, we'll skip and just produce a placeholder
        original_config = {
            "flow_def": form.flow_def or "",
            "constraints": form.constraints,
        }
        # no actual variation for now
        response = OptimizationResponse(
            original=original_config,
            optimized=original_config,
            improvements={m: 0.0 for m in form.metrics},
            steps_taken=1,
        )

    elif form.target == OptimizationType.TOOLS:
        # Possibly reorder or remove certain tools
        # For simplicity, we just return a placeholder
        original_config = {
            "registered_tools": list(branch.acts.registry.keys())
        }
        response = OptimizationResponse(
            original=original_config,
            optimized=original_config,
            improvements={m: 0.0 for m in form.metrics},
            steps_taken=1,
        )
    else:
        # OPERATION => placeholder
        original_config = {"branch_operation": "N/A"}
        response = OptimizationResponse(
            original=original_config,
            optimized=original_config,
            improvements={m: 0.0 for m in form.metrics},
            steps_taken=1,
        )

    # 3. If user wants a structured output, cast it
    if response_format:
        return response_format(**response.model_dump())
    return response
