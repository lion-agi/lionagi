"""
Example Generation System

This module provides classes and utilities for generating, validating,
and managing training examples for parameter tuning.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type


@dataclass
class Example:
    """Container for training examples.

    Attributes:
        input_data: The input data for the example
        expected_output: The expected output/target
        metadata: Optional metadata about the example
    """

    input_data: Any
    expected_output: Any
    metadata: dict[str, Any] | None = None


class ExampleGenerator(ABC):
    """Base class for example generation strategies."""

    @abstractmethod
    def generate(self, num_examples: int = 1) -> list[Example]:
        """Generate new training examples.

        Args:
            num_examples: Number of examples to generate

        Returns:
            List of generated examples
        """
        pass

    @abstractmethod
    def validate(self, example: Example) -> bool:
        """Validate example quality.

        Args:
            example: Example to validate

        Returns:
            True if example is valid, False otherwise
        """
        pass

    def refine(self, example: Example) -> Example:
        """Improve example quality if needed.

        Args:
            example: Example to refine

        Returns:
            Refined example
        """
        if not self.validate(example):
            # Apply refinement logic
            pass
        return example


class TemplateExampleGenerator(ExampleGenerator):
    """Generate examples from templates.

    Attributes:
        templates: List of template dictionaries defining example structure
    """

    def __init__(self, templates: list[dict[str, Any]]):
        self.templates = templates

    def generate(self, num_examples: int = 1) -> list[Example]:
        """Generate examples from templates with random variations."""
        # TODO: Implement template-based generation
        return []

    def validate(self, example: Example) -> bool:
        """Validate example against template constraints."""
        # TODO: Implement template validation
        return True


class SemanticExampleGenerator(ExampleGenerator):
    """Generate examples using semantic rules.

    Attributes:
        rules: List of semantic rules for generating examples
    """

    def __init__(self, rules: list[dict[str, Any]]):
        self.rules = rules

    def generate(self, num_examples: int = 1) -> list[Example]:
        """Apply semantic rules to generate examples."""
        # TODO: Implement semantic rule-based generation
        return []

    def validate(self, example: Example) -> bool:
        """Validate example against semantic rules."""
        # TODO: Implement semantic validation
        return True


class ExampleStore:
    """Manage example storage and retrieval.

    Attributes:
        examples: List of stored examples
    """

    def __init__(self):
        self.examples: list[Example] = []

    def add(self, example: Example):
        """Add an example to storage.

        Args:
            example: Example to store
        """
        if isinstance(example, Example):
            self.examples.append(example)

    def get(self, index: int) -> Example | None:
        """Get example by index.

        Args:
            index: Index of example to retrieve

        Returns:
            Example if found, None otherwise
        """
        try:
            return self.examples[index]
        except IndexError:
            return None

    def load(self, filepath: str):
        """Load examples from JSON file.

        Args:
            filepath: Path to JSON file
        """
        path = Path(filepath)
        if path.exists() and path.suffix == ".json":
            with open(path) as f:
                data = json.load(f)
                for item in data:
                    self.examples.append(
                        Example(
                            input_data=item["input"],
                            expected_output=item["output"],
                            metadata=item.get("metadata"),
                        )
                    )

    def save(self, filepath: str):
        """Save examples to JSON file.

        Args:
            filepath: Path to save JSON file
        """
        path = Path(filepath)
        data = [
            {
                "input": ex.input_data,
                "output": ex.expected_output,
                "metadata": ex.metadata,
            }
            for ex in self.examples
        ]
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
