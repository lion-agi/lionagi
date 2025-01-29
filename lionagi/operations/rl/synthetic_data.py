"""
synthetic_data.py

Implements a SyntheticDataGenerator with various mutation strategies
to create synthetic training examples. Also includes separate config
classes for typed usage.
"""

import asyncio
import random
from typing import Any

from pydantic import BaseModel, Field

from lionagi.protocols.generic.log import Log
from lionagi.session.branch import Branch

from .types import Experience


class DataGenerationConfig(BaseModel):
    """Base config for synthetic data generation."""

    num_variations: int = Field(
        default=5, description="Number of variations to generate per example"
    )
    max_mutations: int = Field(
        default=3, description="Maximum mutation steps for each example"
    )
    diversity_weight: float = Field(
        default=0.3, description="Weight for diversity in final scoring"
    )
    quality_threshold: float = Field(
        default=0.7,
        description="Minimum quality score to keep a generated example",
    )


class SyntheticDataGeneratorConfig(BaseModel):
    """
    Container for DataGenerationConfig plus any extension fields,
    keeping them out of a large Pydantic model if not needed.
    """

    config: DataGenerationConfig = Field(default_factory=DataGenerationConfig)

    class Config:
        arbitrary_types_allowed = True


class MutationStrategy:
    """Base class for a single 'mutation' strategy."""

    async def apply(self, branch: Branch, prompt: str) -> str:
        """Must be overridden by concrete strategy subclasses."""
        raise NotImplementedError


class AddContextStrategy(MutationStrategy):
    async def apply(self, branch: Branch, prompt: str) -> str:
        context_prompt = f"""Add relevant context to this prompt while preserving its intent:

Prompt: {prompt}

Additional context:"""
        try:
            response = await branch.communicate(context_prompt)
            return str(response)
        except Exception:
            return prompt


class ModifyStructureStrategy(MutationStrategy):
    async def apply(self, branch: Branch, prompt: str) -> str:
        structure_prompt = f"""Restructure this prompt in a different format while preserving its meaning:

Prompt: {prompt}

Restructured:"""
        try:
            response = await branch.communicate(structure_prompt)
            return str(response)
        except Exception:
            return prompt


class ChangeStyleStrategy(MutationStrategy):
    async def apply(self, branch: Branch, prompt: str) -> str:
        style_prompt = f"""Rewrite this prompt in a different style while preserving its core request:

Prompt: {prompt}

Rewritten:"""
        try:
            response = await branch.communicate(style_prompt)
            return str(response)
        except Exception:
            return prompt


class SyntheticDataGenerator:
    """
    Generates & refines synthetic training examples by applying
    random mutation strategies, scoring them, and discarding low-quality items.
    """

    def __init__(self, config: DataGenerationConfig | None = None):
        self.config_model = SyntheticDataGeneratorConfig(
            config=config or DataGenerationConfig()
        )
        self._best_examples: list[Experience] = []
        self._max_examples: int = 100

        # Define the available mutation strategies
        self._mutation_strategies = [
            AddContextStrategy(),
            ModifyStructureStrategy(),
            ChangeStyleStrategy(),
        ]

    async def generate(
        self,
        branch: Branch,
        base_examples: list[dict[str, Any]],
        num_variations: int | None = None,
        max_mutations: int | None = None,
        diversity_weight: float | None = None,
    ) -> list[Experience]:
        """
        Generate synthetic examples from base examples.

        :param branch: The Branch for LLM calls
        :param base_examples: Starting examples (dict with 'prompt', 'response', etc.)
        :param num_variations: override for how many variations per example
        :param max_mutations: override for how many mutations per variation
        :param diversity_weight: override for how heavily 'diversity' is weighted
        :return: list of new Experiences that pass the threshold
        """
        generated = []

        cfg = self.config_model.config
        eff_variations = num_variations or cfg.num_variations
        eff_mutations = max_mutations or cfg.max_mutations
        eff_diversity = diversity_weight or cfg.diversity_weight

        # Generate variations concurrently using gather
        tasks = [
            self._generate_variations(
                branch, example, eff_variations, eff_mutations
            )
            for example in base_examples
        ]
        all_variations = await asyncio.gather(*tasks)
        generated = [var for sub in all_variations for var in sub]

        # Score & keep best
        scored_examples = await self._score_examples(
            branch, generated, eff_diversity
        )
        threshold = cfg.quality_threshold
        quality_examples = [
            ex for ex, score in scored_examples if score >= threshold
        ]

        self._add_best_examples(quality_examples)
        return quality_examples

    def _add_best_examples(self, new_ex: list[Experience]) -> None:
        """
        Add newly accepted examples to best_examples, respecting max size.
        """
        self._best_examples.extend(new_ex)
        if len(self._best_examples) > self._max_examples:
            self._best_examples = self._best_examples[-self._max_examples :]

    async def _generate_variations(
        self,
        branch: Branch,
        example: dict[str, Any],
        num_variations: int,
        max_mutations: int,
    ) -> list[Experience]:
        """
        For each example, do N variations, each with random mutation steps.
        """
        variations = []
        base_prompt = example.get("prompt", example.get("instruction", ""))

        for _ in range(num_variations):
            mutated_prompt, mutation_list = await self._mutate_prompt(
                branch, base_prompt, max_mutations
            )
            try:
                response = await branch.communicate(mutated_prompt)
                exp = Experience(
                    prompt=mutated_prompt,
                    response=str(response),
                    reward=0.0,  # scored later
                    metadata={
                        "base_example": example,
                        "mutations": mutation_list,
                    },
                )
                variations.append(exp)
            except Exception as e:
                branch._log_manager.log(
                    Log.create(
                        {
                            "type": "generation_error",
                            "error": str(e),
                            "prompt": mutated_prompt,
                        }
                    )
                )
        return variations

    async def _mutate_prompt(
        self, branch: Branch, prompt: str, max_mutations: int
    ) -> tuple[str, list[str]]:
        """
        Randomly apply up to 'max_mutations' steps from the available strategies.
        """
        mutated = prompt
        mutations = []
        steps = random.randint(1, max_mutations)

        for _ in range(steps):
            strategy = random.choice(self._mutation_strategies)
            try:
                mutated = await strategy.apply(branch, mutated)
                mutations.append(strategy.__class__.__name__)
            except Exception:
                pass  # skip if any single mutation fails

        return mutated, mutations

    async def _score_examples(
        self,
        branch: Branch,
        examples: list[Experience],
        diversity_weight: float,
    ) -> list[tuple[Experience, float]]:
        """
        Compute (experience, score) for each example, sorted desc by score.
        Score = (1 - w)*quality + w*diversity
        """
        scored = []
        for exp in examples:
            quality = await self._compute_quality(branch, exp)
            diversity = await self._compute_diversity(exp)
            final_score = (
                1 - diversity_weight
            ) * quality + diversity_weight * diversity
            exp.reward = final_score
            scored.append((exp, final_score))

        return sorted(scored, key=lambda x: x[1], reverse=True)

    async def _compute_quality(self, branch: Branch, exp: Experience) -> float:
        """User-defined or random. For now random placeholder."""
        return random.random()

    async def _compute_diversity(self, exp: Experience) -> float:
        """Compare to best_examples. For now random placeholder."""
        if not self._best_examples:
            return 1.0
        return random.random()
