from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel, Field

from lionagi.operatives.forms.form import Form
from lionagi.session.branch import Branch

T = TypeVar("T", bound=BaseModel)


class Experience(BaseModel):
    """
    Individual experience for learning.
    - context: State or partial environment
    - action_taken: Which action or approach was used
    - result: The outcome of that action
    - reward: The reward or performance signal
    - metadata: Additional data
    """

    context: dict[str, Any] = Field(default_factory=dict)
    action_taken: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] = Field(default_factory=dict)
    reward: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class LearnTarget(str, Enum):
    POLICY = "policy"  # Learn decision-making
    RESPONSE = "response"  # Learn better response patterns
    TOOL = "tool"  # Learn tool usage patterns
    PLANNING = "planning"  # Learn planning strategies


class LearnForm(Form):
    """
    The user or system calls `learn(branch, target=..., experiences=...)`.
    """

    target: LearnTarget
    experiences: list[Experience] = Field(default_factory=list)
    max_iterations: int = 5
    success_threshold: float = 0.8

    # Additional hyperparameters
    batch_size: int | None = 32
    learning_rate: float = 0.001

    # For evaluating results
    eval_instruction: str | None = None
    response_format: Any = None

    # Required fields
    output_fields = ["target", "experiences"]


class LearnResponse(BaseModel):
    """
    The outcome of a learning process.
    - target: Which aspect was learned
    - iterations: # of training iterations
    - improvements: Key metric changes
    - learned_patterns: The discovered or updated knowledge
    - metadata: Extra info
    """

    target: LearnTarget
    iterations: int
    improvements: dict[str, float]
    learned_patterns: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


def _get_context_key(context: dict[str, Any]) -> str:
    """
    Simplified hashing of context.
    Could do more advanced logic if needed.
    """
    return str(sorted(context.items()))


def _learn_policy_patterns(experiences: list[Experience]) -> list[str]:
    """
    Learn from experiences to derive 'policy patterns': e.g. if context X -> do action Y
    We look for successful experiences with positive reward.
    """
    if not experiences:
        return []

    # Group by context
    context_map = {}
    for exp in experiences:
        ckey = _get_context_key(exp.context)
        if ckey not in context_map:
            context_map[ckey] = []
        context_map[ckey].append(exp)

    patterns = []
    for ckey, exps in context_map.items():
        # pick best experience for that context
        best_exp = max(exps, key=lambda e: e.reward)
        if best_exp.reward > 0:
            patterns.append(
                f"For context={ckey}, action={best_exp.action_taken} yields reward={best_exp.reward}"
            )
    return patterns


def _apply_learned_policy(branch: Branch, patterns: list[str]):
    """
    Example of applying learned patterns to the Branch's system or metadata.
    For instance, appending them to a policy section in the system message.
    """
    old_system = branch.msgs.get_system()
    new_system = (
        old_system + "\n[Learned Policy Patterns]\n" + "\n".join(patterns)
    )
    branch.msgs.set_system(new_system)
