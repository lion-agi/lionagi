# lionagi/strategies/operations.py

from typing import Any, Dict, Optional

from pydantic import Field

from ..protocols.operatives.tasks import Task


class BrainstormOperation(Task):
    """
    Represents a brainstorming operation, generating or collecting ideas.
    """

    topic: str = Field(
        ..., description="The topic or question to brainstorm about"
    )
    ideas: dict[str, Any] | None = Field(
        default_factory=dict, description="Collected ideas"
    )


class ReflectOperation(Task):
    """
    Represents a reflection operation, reviewing past actions or decisions.
    """

    subject: str = Field(..., description="Subject or area to reflect upon")
    insights: dict[str, Any] | None = Field(
        default_factory=dict, description="Reflected insights"
    )


class PlanOperation(Task):
    """
    Represents a planning operation, structuring tasks, resources, and timelines.
    """

    objective: str = Field(..., description="Overall goal of the plan")
    timeline: str = Field(
        ..., description="Proposed schedule or timeline for execution"
    )
    resources: dict[str, Any] = Field(
        default_factory=dict, description="Key resources or constraints"
    )


class CritiqueOperation(Task):
    """
    Represents a critique operation, evaluating and providing feedback.
    """

    subject: str = Field(..., description="Subject or artifact to critique")
    feedback: dict[str, Any] | None = Field(
        default_factory=dict, description="Critique feedback"
    )


class ReasonOperation(Task):
    """
    Represents a reasoning operation, explaining the rationale behind decisions.
    """

    decision: str = Field(..., description="Decision to reason about")
    rationale: str | None = Field(
        None, description="Reasoning behind the decision"
    )


class BacktrackOperation(Task):
    """
    Represents a backtracking operation, reverting to previous states or steps.
    """

    step_id: str | None = Field(
        None, description="ID of the step to backtrack to"
    )
    reason: str | None = Field(None, description="Reason for backtracking")


class EvaluateOperation(Task):
    """
    Represents an evaluation operation, assessing performance or outcomes.
    """

    target: str = Field(..., description="Target or metric to evaluate")
    result: Any | None = Field(None, description="Evaluation result")


class JudgeOperation(Task):
    """
    Represents a judgment operation, making decisions based on evaluations.
    """

    criteria: str = Field(..., description="Criteria for judgment")
    verdict: str | None = Field(None, description="Judgment decision")


class AnalyzeOperation(Task):
    """
    Represents an analysis operation, breaking down complex information.
    """

    data: Any = Field(..., description="Data or information to analyze")
    findings: dict[str, Any] | None = Field(
        default_factory=dict, description="Analysis findings"
    )
