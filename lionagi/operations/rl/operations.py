"""
operations.py

Defines the top-level RL(...) and operate_rl(...) functions for
easy user-facing usage. These wrap around an RLSystem instance
to orchestrate training, synthetic data generation, and so forth.
"""

from typing import Any

from lionagi.session.branch import Branch

from .system import RLSystem
from .types import OptimizationMode, TuningConfig


async def RL(
    branch: Branch,
    training_data: list[dict[str, Any]],
    eval_data: list[dict[str, Any]] | None = None,
    mode: str | OptimizationMode = OptimizationMode.HYBRID,
    tuning_config: dict[str, Any] | None = None,
    reward_fn: Any | None = None,
    checkpoint_path: str | None = None,
    checkpoint_dir: str | None = None,
    checkpoint_interval: int | None = None,
    batch_size: int | None = None,
    learning_rate: float | None = None,
    num_variations: int | None = None,
    max_mutations: int | None = None,
    diversity_weight: float | None = None,
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Main RL operation for improving model performance through
    parameter tuning and/or synthetic data generation.

    :param branch: Branch containing model
    :param training_data: List of training examples as dict
    :param eval_data: Optional list of eval examples
    :param mode: 'parameter_tuning', 'synthetic_data', or 'hybrid'
    :param tuning_config: Dict of TuningConfig overrides
    :param reward_fn: Custom function to compute reward
    :param checkpoint_path: If provided, load from checkpoint
    :param checkpoint_dir: Directory for saving new checkpoints
    :param checkpoint_interval: Steps between checkpoints
    :param batch_size: Override for batch size
    :param learning_rate: Override for learning rate
    :param num_variations: For SyntheticDataGenerator
    :param max_mutations: For SyntheticDataGenerator
    :param diversity_weight: For SyntheticDataGenerator
    :param verbose: Whether to print logs
    :return: Dict of training results
    """
    # Build a TuningConfig from input
    base_config = {"mode": mode, **(tuning_config or {})}
    if reward_fn:
        base_config["reward_fn"] = reward_fn

    system_config = TuningConfig(**base_config)

    # Create RLSystem
    system = RLSystem(config=system_config)

    # If user sets checkpoint_dir/interval, store them
    if checkpoint_dir:
        system.config_model.checkpoint_dir = checkpoint_dir
    if checkpoint_interval:
        system.config_model.checkpoint_interval = checkpoint_interval

    # Run the RLSystem training
    results = await system.train(
        branch=branch,
        initial_examples=training_data,
        eval_examples=eval_data,
        checkpoint_path=checkpoint_path,
        batch_size=batch_size,
        learning_rate=learning_rate,
        num_variations=num_variations,
        max_mutations=max_mutations,
        diversity_weight=diversity_weight,
    )

    # Optional console prints
    if verbose:
        print(f"\nTraining completed after {results['steps']} steps")
        print(f"Best reward achieved: {results['best_reward']:.3f}")
        if results["final_metrics"]:
            print("\nFinal Evaluation Metrics:")
            for k, v in results["final_metrics"]["metrics"].items():
                print(f"{k}: {v:.3f}")

    return results


async def operate_rl(
    branch: Branch,
    training_data: list[dict[str, Any]] | dict[str, Any],
    **kwargs,
) -> dict[str, Any]:
    """
    Convenience wrapper around RL. If user passes a single example
    as a dict, convert it to a list before calling RL().

    :param branch: The conversation Branch
    :param training_data: Single or list of dict examples
    :param kwargs: Forwarded to RL
    :return: dict of results
    """
    if isinstance(training_data, dict):
        training_data = [training_data]

    return await RL(branch=branch, training_data=training_data, **kwargs)
