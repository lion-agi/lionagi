from typing import Any, TypeVar

from pydantic import BaseModel

from lionagi.session.branch import Branch

from .utils import (
    Experience,
    LearnForm,
    LearnResponse,
    LearnTarget,
    _apply_learned_policy,
    _learn_policy_patterns,
)

T = TypeVar("T", bound=BaseModel)


async def learn(
    branch: Branch,
    *,
    target: LearnTarget | dict[str, Any],
    experiences: list[Experience] | None = None,
    max_iterations: int = 5,
    response_format: type[T] | None = None,
    **kwargs,
) -> LearnResponse | T:
    """
    High-level function to 'learn' from experiences and update the Branch with
    new knowledge. Distinct from 'optimize' in that it's about "improving
    decision-making" or "improving response patterns" from data.

    e.g. usage:
        response = await learn(
            branch=some_branch,
            target=LearnTarget.POLICY,
            experiences=[exp1, exp2, ...],
            max_iterations=10
        )
    """
    # 1. Construct or parse the form
    if isinstance(target, dict):
        form = LearnForm(**target)
    else:
        form = LearnForm(
            target=target,
            experiences=experiences or [],
            max_iterations=max_iterations,
            **kwargs,
        )
    form.check_completeness(how="raise")  # ensure required fields

    # 2. Based on target, do specialized logic
    learned_patterns: dict[str, Any] = {}
    improvements: dict[str, float] = {}

    if form.target == LearnTarget.POLICY:
        # Extract policy patterns from experiences
        policy_patterns = _learn_policy_patterns(form.experiences)
        # Apply to the branch
        _apply_learned_policy(branch, policy_patterns)

        learned_patterns["policy_patterns"] = policy_patterns
        improvements["pattern_count"] = float(len(policy_patterns))

    elif form.target == LearnTarget.RESPONSE:
        # Placeholder approach
        # Could do advanced approach: group responses, produce new template, etc.
        count_positive = sum(1 for e in form.experiences if e.reward > 0)
        learned_patterns["response_templates"] = [
            f"Template_{i}" for i in range(count_positive)
        ]
        improvements["template_count"] = float(count_positive)

    elif form.target == LearnTarget.TOOL:
        # Possibly see which tools lead to higher reward and store that knowledge
        tool_usage_map = {}
        for e in form.experiences:
            tused = e.action_taken.get("tools_used", [])
            for t in tused:
                if t not in tool_usage_map:
                    tool_usage_map[t] = {"count": 0, "reward": 0.0}
                tool_usage_map[t]["count"] += 1
                tool_usage_map[t]["reward"] += e.reward

        # Just store as metadata
        branch.metadata["learned_tool_usage"] = tool_usage_map
        learned_patterns["tool_usage"] = tool_usage_map
        improvements["tool_pattern_count"] = float(len(tool_usage_map))

    elif form.target == LearnTarget.PLANNING:
        # Possibly do advanced analysis of multi-step planning
        planning_strats = {}
        for e in form.experiences:
            plan = e.action_taken.get("plan", "NoPlan")
            if plan not in planning_strats:
                planning_strats[plan] = {"count": 0, "reward": 0.0}
            planning_strats[plan]["count"] += 1
            planning_strats[plan]["reward"] += e.reward

        # store in branch
        branch.metadata["learned_planning"] = planning_strats
        learned_patterns["planning_strategies"] = planning_strats
        improvements["strategy_count"] = float(len(planning_strats))

    # 3. Create final response
    response = LearnResponse(
        target=form.target,
        iterations=form.max_iterations,
        improvements=improvements,
        learned_patterns=learned_patterns,
    )

    # 4. If user wants structured, cast it
    if response_format:
        return response_format(**response.dict())
    return response
