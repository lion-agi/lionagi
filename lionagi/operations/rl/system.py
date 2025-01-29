"""
system.py

Defines the RLSystem class, which coordinates parameter tuning
and synthetic data generation. Includes checkpoint load/save,
evaluation, and overall training loop.
"""

import json
import os
from typing import Any

from lionagi.protocols.generic.log import Log
from lionagi.session.branch import Branch

from .parameter_tuning import ParameterTuner, ParameterTunerConfig
from .synthetic_data import (
    SyntheticDataGenerator,
    SyntheticDataGeneratorConfig,
)
from .types import (
    EvalResult,
    Experience,
    OptimizationMode,
    TrainingMetrics,
    TuningConfig,
)


class RLSystemConfig:
    """
    Minimal container for overall RL system config,
    including TuningConfig and checkpoint details.
    """

    def __init__(
        self,
        tuning_config: TuningConfig | None = None,
        checkpoint_interval: int = 100,
        checkpoint_dir: str = "checkpoints",
    ):
        self.tuning_config = tuning_config or TuningConfig()
        self.checkpoint_interval = checkpoint_interval
        self.checkpoint_dir = checkpoint_dir


class RLSystem:
    """
    Main orchestrator for RL-based improvement.
    - parameter_tuner: manages gradient steps
    - data_generator: manages synthetic data creation
    - training loop
    - checkpointing
    - evaluation
    """

    def __init__(self, config: TuningConfig | None = None):
        self.config_model = RLSystemConfig(
            tuning_config=config or TuningConfig()
        )
        # Create sub-components
        self.parameter_tuner = ParameterTuner(
            config=self.config_model.tuning_config
        )
        self.data_generator = SyntheticDataGenerator()

        # Track training state as plain Python attributes
        self._current_step: int = 0
        self._best_reward: float = float("-inf")
        self._eval_results: list[EvalResult] = []

    async def train(
        self,
        branch: Branch,
        initial_examples: list[dict[str, Any]],
        eval_examples: list[dict[str, Any]] | None = None,
        checkpoint_path: str | None = None,
        batch_size: int | None = None,
        learning_rate: float | None = None,
        num_variations: int | None = None,
        max_mutations: int | None = None,
        diversity_weight: float | None = None,
    ) -> dict[str, Any]:
        """
        Orchestrates the RL loop: data generation + parameter tuning + evaluation.

        :param branch: The conversation branch with the model
        :param initial_examples: Base training dataset
        :param eval_examples: For periodic evaluation
        :param checkpoint_path: If we want to load an existing checkpoint
        :param batch_size: override the standard batch size
        :param learning_rate: override the standard LR
        :param num_variations: overrides data gen config
        :param max_mutations: overrides data gen config
        :param diversity_weight: overrides data gen config
        :return: dictionary with final results
        """

        # If user provided a path, load prior state
        if checkpoint_path:
            await self._load_checkpoint(checkpoint_path)

        mode = self.config_model.tuning_config.mode
        max_steps = self.config_model.tuning_config.max_steps

        while self._current_step < max_steps:
            # Possibly generate synthetic data
            if mode in [
                OptimizationMode.SYNTHETIC_DATA,
                OptimizationMode.HYBRID,
            ]:
                generated_exps = await self.data_generator.generate(
                    branch=branch,
                    base_examples=initial_examples,
                    num_variations=num_variations,
                    max_mutations=max_mutations,
                    diversity_weight=diversity_weight,
                )
                # Add them to the training set
                for exp in generated_exps:
                    initial_examples.append(
                        {"prompt": exp.prompt, "response": exp.response}
                    )

                branch._log_manager.log(
                    Log.create(
                        {
                            "type": "data_generation",
                            "num_examples": len(generated_exps),
                            "step": self._current_step,
                        }
                    )
                )

            # Possibly do parameter tuning
            if mode in [
                OptimizationMode.PARAMETER_TUNING,
                OptimizationMode.HYBRID,
            ]:
                experiences = [
                    Experience(
                        prompt=ex.get("prompt", ""),
                        response=ex.get("response", ""),
                        reward=0.0,
                    )
                    for ex in initial_examples
                ]
                metrics = await self.parameter_tuner.optimize(
                    branch=branch,
                    experiences=experiences,
                    batch_size=batch_size,
                    learning_rate=learning_rate,
                )
                branch._log_manager.log(
                    Log.create(
                        {
                            "type": "optimization_step",
                            "metrics": metrics.model_dump(),
                            "step": self._current_step,
                        }
                    )
                )

            # Evaluate periodically
            eval_interval = self.config_model.tuning_config.eval_interval
            if eval_examples and (self._current_step % eval_interval == 0):
                eval_result = await self.evaluate(branch, eval_examples)
                self._eval_results.append(eval_result)

                # Possibly checkpoint
                if (
                    self._current_step % self.config_model.checkpoint_interval
                    == 0
                ):
                    await self._save_checkpoint()

                # Check target reward
                target_reward = self.config_model.tuning_config.target_reward
                if (
                    target_reward
                    and eval_result.metrics["reward"] >= target_reward
                ):
                    break

                # Track best reward
                if eval_result.metrics["reward"] > self._best_reward:
                    self._best_reward = eval_result.metrics["reward"]

            self._current_step += 1

        # Final checkpoint
        await self._save_checkpoint()

        return self._get_results()

    async def evaluate(
        self, branch: Branch, examples: list[dict[str, Any]]
    ) -> EvalResult:
        """
        Evaluate with current model. Basic loop that calls the model and compares with 'target'.

        :param branch: The conversation branch
        :param examples: List of dicts with 'prompt' and 'target'
        :return: EvalResult
        """
        total_reward = 0.0
        results = []

        for ex in examples:
            prompt = ex.get("prompt", "")
            target = ex.get("target", "")
            try:
                response = await branch.communicate(prompt)
                reward = await self._compute_reward(
                    branch, str(response), target
                )
                total_reward += reward
                results.append(
                    {
                        "prompt": prompt,
                        "response": str(response),
                        "target": target,
                        "reward": reward,
                    }
                )
            except Exception as e:
                branch._log_manager.log(
                    Log.create(
                        {"type": "eval_error", "error": str(e), "example": ex}
                    )
                )

        avg_reward = total_reward / len(examples)
        return EvalResult(
            metrics={"reward": avg_reward, "num_examples": len(examples)},
            examples=results,
        )

    async def _compute_reward(
        self, branch: Branch, response: str, target: str
    ) -> float:
        """
        If the user provided a custom reward_fn, call that.
        Otherwise a trivial equality check.
        """
        reward_fn = self.config_model.tuning_config.reward_fn
        if callable(reward_fn):
            return await reward_fn(response, target)

        return float(response.strip() == target.strip())

    def _get_results(self) -> dict[str, Any]:
        """
        Summarize final training results
        """
        final_metrics = (
            self._eval_results[-1].model_dump() if self._eval_results else None
        )
        return {
            "steps": self._current_step,
            "best_reward": self._best_reward,
            "eval_results": [r.model_dump() for r in self._eval_results],
            "final_metrics": final_metrics,
        }

    async def _save_checkpoint(self) -> None:
        """
        Save relevant training state to JSON file.
        """
        path = os.path.join(
            self.config_model.checkpoint_dir,
            f"checkpoint_{self._current_step}.json",
        )
        os.makedirs(self.config_model.checkpoint_dir, exist_ok=True)

        checkpoint = {
            "current_step": self._current_step,
            "best_reward": self._best_reward,
            "eval_results": [r.model_dump() for r in self._eval_results],
            "parameter_tuner": {
                "config": self.parameter_tuner.config_model.model_dump(),
                "metrics": [
                    m.model_dump()
                    for m in self.parameter_tuner.config_model.metrics
                ],
            },
            "data_generator": {
                "config": self.data_generator.config_model.model_dump()
            },
        }

        with open(path, "w") as f:
            json.dump(checkpoint, f, indent=2)

    async def _load_checkpoint(self, path: str) -> None:
        """
        Load prior training state from JSON.
        """
        if not os.path.isfile(path):
            return

        with open(path, "r") as f:
            data = json.load(f)

        self._current_step = data.get("current_step", 0)
        self._best_reward = data.get("best_reward", float("-inf"))
        self._eval_results = [
            EvalResult(**r) for r in data.get("eval_results", [])
        ]

        p_config = data.get("parameter_tuner", {}).get("config", {})
        p_metrics = data.get("parameter_tuner", {}).get("metrics", [])
        self.parameter_tuner.config_model = ParameterTunerConfig(**p_config)
        self.parameter_tuner.config_model.metrics = [
            TrainingMetrics(**m) for m in p_metrics
        ]

        dg_config = data.get("data_generator", {}).get("config", {})
        self.data_generator.config_model.config = (
            self.data_generator.config_model.config.copy(
                update=dg_config.get("config", {})
            )
        )
