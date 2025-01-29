"""
parameter_tuning.py

Provides classes for PPO-style parameter tuning, including:
- ParameterTunerConfig (Pydantic for stored metrics and base config)
- ParameterTuner (core logic to manage an experience buffer and perform "updates")
"""

import asyncio

from pydantic import BaseModel, Field

from lionagi.protocols.generic.log import Log
from lionagi.session.branch import Branch

from .types import Experience, TrainingMetrics, TuningConfig


class ParameterTunerConfig(BaseModel):
    """
    Configuration/State container for ParameterTuner.
    Tracks:
      - 'config': base TuningConfig
      - 'metrics': list of TrainingMetrics after each update
    """

    config: TuningConfig = Field(default_factory=TuningConfig)
    metrics: list[TrainingMetrics] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class ParameterTuner:
    """
    Performs PPO-style parameter updates based on a buffer of Experiences.
    Actual gradient steps are placeholders for now, but logs relevant data.
    """

    def __init__(self, config: TuningConfig | None = None):
        # Store Pydantic config for typed settings
        self.config_model = ParameterTunerConfig(
            config=config or TuningConfig()
        )
        # Buffer is a plain Python attribute (avoid large storage in Pydantic)
        self._buffer: list[Experience] = []
        self._buffer_size: int = 0
        self._max_buffer_size: int = 10000  # Arbitrary default

    async def optimize(
        self,
        branch: Branch,
        experiences: list[Experience],
        batch_size: int | None = None,
        learning_rate: float | None = None,
        max_grad_norm: float | None = None,
    ) -> TrainingMetrics:
        """
        Main entry to run a "training step" with experiences.

        :param branch: Branch containing the LLM model and logs
        :param experiences: Newly collected experiences
        :param batch_size: Override for batch_size
        :param learning_rate: Override for LR
        :param max_grad_norm: If we had real gradient steps, we might clip them
        :return: TrainingMetrics with final loss/reward
        """
        if not experiences:
            return TrainingMetrics(loss=0.0, reward=0.0)

        # Add new experiences to buffer
        self._add_to_buffer(experiences)

        # Determine effective batch size
        effective_batch_size = (
            batch_size or self.config_model.config.batch_size
        )

        # Only train if enough experiences are accumulated
        if self._buffer_size < effective_batch_size:
            return TrainingMetrics(loss=0.0, reward=0.0)

        # Grab a batch from the buffer
        batch = self._get_batch(effective_batch_size)

        # Collect prompts, responses, rewards
        prompts, responses, rewards = zip(
            *[(exp.prompt, exp.response, exp.reward) for exp in batch]
        )

        # Estimate values asynchronously
        values = await asyncio.gather(
            *[self._estimate_value(branch, exp) for exp in batch]
        )

        # Calculate advantages (simple: advantage = reward - value)
        advantages = [r - v for r, v in zip(rewards, values)]

        # Perform the "update"
        metrics = await self._optimize_step(
            branch=branch,
            prompts=prompts,
            responses=responses,
            advantages=advantages,
            values=values,
            learning_rate=learning_rate
            or self.config_model.config.learning_rate,
            max_grad_norm=max_grad_norm,
        )

        self.config_model.metrics.append(metrics)
        return metrics

    def _add_to_buffer(self, experiences: list[Experience]) -> None:
        """Extend buffer with new experiences, prune if above max size."""
        self._buffer.extend(experiences)
        self._buffer_size = len(self._buffer)
        if self._buffer_size > self._max_buffer_size:
            excess = self._buffer_size - self._max_buffer_size
            self._buffer = self._buffer[excess:]
            self._buffer_size = len(self._buffer)

    def _get_batch(self, batch_size: int) -> list[Experience]:
        """Pop and return 'batch_size' items from the front of the buffer."""
        batch = self._buffer[:batch_size]
        self._buffer = self._buffer[batch_size:]
        self._buffer_size = len(self._buffer)
        return batch

    async def _estimate_value(
        self, branch: Branch, experience: Experience
    ) -> float:
        """
        For RL, we might have a separate value network or approach.
        Currently, just returns the experience's reward as a naive value.
        """
        return float(experience.reward)

    async def _optimize_step(
        self,
        branch: Branch,
        prompts: list[str],
        responses: list[str],
        advantages: list[float],
        values: list[float],
        learning_rate: float,
        max_grad_norm: float | None = None,
        **kwargs,
    ) -> TrainingMetrics:
        """
        Stub for the "policy and value" update. Real logic would do gradient steps.
        Logs relevant info for debugging.
        """
        # In principle, we'd do forward/back pass on a local or remote model.
        # For now, just pretend policy_loss and value_loss are zero.
        policy_loss = 0.0
        value_loss = 0.0

        # Log the "update"
        branch._log_manager.log(
            Log.create(
                {
                    "type": "parameter_update",
                    "policy_loss": policy_loss,
                    "value_loss": value_loss,
                    "advantages": advantages,
                    "batch_size": len(prompts),
                    "learning_rate": learning_rate,
                    "max_grad_norm": max_grad_norm,
                }
            )
        )

        return TrainingMetrics(
            loss=policy_loss + value_loss,
            reward=sum(advantages) / len(advantages),
            policy_kl=0.0,  # place holder
            value_loss=value_loss,
        )
