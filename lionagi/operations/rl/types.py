"""
types.py

Defines shared data classes:
- OptimizationMode
- TrainingMetrics
- TuningConfig
- Experience
- EvalResult
"""

from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OptimizationMode(str, Enum):
    """Mode for RL optimization"""

    PARAMETER_TUNING = "parameter_tuning"
    SYNTHETIC_DATA = "synthetic_data"
    HYBRID = "hybrid"


class TrainingMetrics(BaseModel):
    """Metrics tracked during training"""

    loss: float = Field(description="Current loss value")
    reward: float = Field(description="Current reward value")
    policy_kl: float | None = Field(
        None, description="KL divergence from old policy"
    )
    value_loss: float | None = Field(None, description="Value function loss")
    data_metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Metrics related to synthetic data, if any",
    )


class TuningConfig(BaseModel):
    """Configuration for RL-based tuning"""

    mode: OptimizationMode = Field(
        default=OptimizationMode.HYBRID,
        description="Which optimization mode to use",
    )
    learning_rate: float = Field(
        default=1e-5, description="Learning rate for parameter updates"
    )
    max_steps: int = Field(default=1000, description="Maximum training steps")
    batch_size: int = Field(default=32, description="Training batch size")
    target_reward: float | None = Field(
        None, description="Training stops if this reward is reached"
    )
    reward_fn: Callable[[str, str], float] | None = Field(
        None,
        description="Function to compute rewards (signature: (response, target) -> float)",
    )
    eval_interval: int = Field(
        default=100, description="Steps between evaluations"
    )


class Experience(BaseModel):
    """Training experience for RL"""

    prompt: str = Field(description="Input prompt")
    response: str = Field(description="Model response")
    reward: float = Field(
        description="Reward received from environment/heuristic"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional info about the experience",
    )


class EvalResult(BaseModel):
    """Results from evaluation"""

    metrics: dict[str, float] = Field(
        description="Evaluation metrics, e.g. {'reward': 0.9}"
    )
    examples: list[dict[str, Any]] = Field(
        description="List of example dicts (prompt, response, reward, etc.)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional evaluation info if needed",
    )
