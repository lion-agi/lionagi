import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import dspy
from synthlang import __version__
from synthlang.config import Config, ConfigManager
from synthlang.core import (
    FrameworkTranslator,
    PromptClassifier,
    PromptEvolver,
    PromptManager,
    PromptOptimizer,
    SystemPromptGenerator,
)


class SynthLangException(Exception):
    """Custom exception type for SynthLang errors."""

    pass


def load_config() -> Config:
    """
    Load configuration from the local environment using ConfigManager.
    Raises SynthLangException on failure.
    """
    try:
        config_manager = ConfigManager()
        return config_manager.load()
    except Exception as e:
        raise SynthLangException(f"Error loading configuration: {str(e)}")


def get_api_key() -> str:
    """
    Get the OpenAI API key from the environment variable or from the root .env file.
    Raises SynthLangException if not found.
    """
    # First check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    # Then check root .env file
    root_env = Path("/workspaces/SynthLang/.env")
    if root_env.exists():
        with open(root_env) as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    return line.strip().split("=", 1)[1]

    raise SynthLangException(
        "OPENAI_API_KEY not found in environment or .env file"
    )


def translate_prompt(
    source: str, framework: str = "synthlang", show_metrics: bool = False
) -> Dict[str, Any]:
    """
    Translate a natural language prompt to a SynthLang format (or another framework).

    :param source: The natural language prompt to translate.
    :param framework: Target framework (currently only 'synthlang' is supported).
    :param show_metrics: Whether to calculate and return token/cost metrics.
    :return: A dictionary containing:
        {
            "source": original prompt,
            "target": translated prompt,
            "explanation": reasoning or explanation,
            "metrics": optional metrics (if show_metrics=True)
        }
    :raises SynthLangException: if translation fails or invalid framework is requested.
    """
    if framework.lower() != "synthlang":
        raise SynthLangException(
            "Only 'synthlang' is supported as target framework"
        )

    config_data = load_config()
    api_key = get_api_key()

    # Create language model
    lm = dspy.LM(model=config_data.model, api_key=api_key)
    dspy.configure(lm=lm)

    instructions = """SYNTHLANG TRANSLATION FORMAT:

RULES:
1. Use ONLY these symbols: ↹ (input), ⊕ (process), Σ (output)
2. NO quotes, arrows, or descriptions
3. Use • to join related items
4. Use => for transformations
5. Maximum 30 characters per line
6. Use mathematical operators (+, >, <, ^)
7. Break complex tasks into steps

IMPORTANT: Keep translations extremely concise!

GOOD EXAMPLES:
↹ data•source
⊕ condition>5 => action
Σ result + log

↹ input•stream, params
⊕ transform => output
⊕ Σ final^2 + cache

↹ news•feed•google
⊕ sentiment>0 => pos
⊕ sentiment<0 => neg
Σ trend + factors

BAD EXAMPLES (TOO VERBOSE):
↹ data:"source" -> Parse input
⊕ process:"condition" -> Check value

Convert input to concise SynthLang format using minimal symbols.
"""

    translator = FrameworkTranslator(lm=lm)

    try:
        result = translator.translate(source, instructions)

        output_data = {
            "source": source,
            "target": result["target"],
            "explanation": result["explanation"],
        }

        if show_metrics:
            # Simple token estimation
            def calculate_tokens(text: str) -> int:
                return len(text.split())

            original_tokens = calculate_tokens(source)
            translated_tokens = calculate_tokens(result["target"])

            # Estimate cost using a nominal rate
            cost_per_1k = 0.0025  # $2.50 per million tokens
            original_cost = (original_tokens / 1000) * cost_per_1k
            translated_cost = (translated_tokens / 1000) * cost_per_1k
            savings = max(0, original_cost - translated_cost)
            if original_tokens > 0:
                reduction = (
                    (original_tokens - translated_tokens) / original_tokens
                ) * 100
            else:
                reduction = 0

            metrics_data = {
                "original_tokens": original_tokens,
                "translated_tokens": translated_tokens,
                "cost_savings": savings,
                "token_reduction_percent": reduction,
            }
            output_data["metrics"] = metrics_data

        return output_data

    except Exception as e:
        raise SynthLangException(f"Translation failed: {str(e)}")


def generate_system_prompt(task: str) -> Dict[str, Any]:
    """
    Generate a system prompt based on a given task.

    :param task: Description of the task for which the system prompt is generated.
    :return: Dictionary with "prompt", "rationale", and "metadata".
    :raises SynthLangException: if generation fails.
    """
    config_data = load_config()
    api_key = get_api_key()

    lm = dspy.LM(model=config_data.model, api_key=api_key)
    dspy.configure(lm=lm)

    generator = SystemPromptGenerator(lm=lm)
    try:
        result = generator.generate(task)
        return {
            "prompt": result["prompt"],
            "rationale": result["rationale"],
            "metadata": result["metadata"],
        }
    except Exception as e:
        raise SynthLangException(f"Generation failed: {str(e)}")


def evolve_prompt(
    seed: str,
    generations: int = 10,
    population: int = 5,
    mutation_rate: float = 0.3,
    tournament_size: int = 3,
    fitness: str = "hybrid",
    save_lineage: bool = False,
    test_cases: Optional[str] = None,
    save_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evolve prompts using genetic algorithms and self-play tournaments.

    :param seed: Initial prompt to evolve.
    :param generations: Number of generations to run the evolution.
    :param population: Population size per generation.
    :param mutation_rate: Rate of mutation (0.0 - 1.0).
    :param tournament_size: Number of prompts to compete in each tournament.
    :param fitness: Fitness function type ('clarity', 'specificity', 'task', 'hybrid').
    :param save_lineage: Whether to save the full lineage (history) of the evolution.
    :param test_cases: Path to a JSON file with test cases for task-based fitness (optional).
    :param save_prompt: If provided, save the best prompt under this name.
    :return: A dictionary with details about the best prompt, fitness scores, and evolution metrics.
    :raises SynthLangException: if evolution fails.
    """
    config_data = load_config()
    api_key = get_api_key()

    lm = dspy.LM(model=config_data.model, api_key=api_key)
    dspy.configure(lm=lm)

    test_suite = None
    if test_cases:
        with open(test_cases) as f:
            data = json.load(f)
            test_suite = data.get("test_cases", [])

    optimizer = PromptEvolver(
        lm=lm,
        population_size=population,
        mutation_rate=mutation_rate,
        tournament_size=tournament_size,
        fitness_type=fitness,
        test_cases=test_suite,
    )

    try:
        result = optimizer.evolve(seed_prompt=seed, n_generations=generations)

        output_data = {
            "best_prompt": result["best_prompt"],
            "fitness": result["fitness"],
            "generations": result["generations"],
            "total_variants": result["total_variants"],
            "successful_mutations": result["successful_mutations"],
            "tournament_winners": result["tournament_winners"],
        }

        if save_lineage:
            lineage_file = f"prompt_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(lineage_file, "w") as f:
                json.dump(result["lineage"], f, indent=2)
            output_data["lineage_file"] = lineage_file

        if save_prompt:
            manager = PromptManager()
            manager.save(
                save_prompt,
                result["best_prompt"],
                {
                    "fitness": result["fitness"],
                    "generations": generations,
                    "evolution_metrics": {
                        "total_variants": result["total_variants"],
                        "successful_mutations": result["successful_mutations"],
                        "tournament_winners": result["tournament_winners"],
                    },
                },
            )
            output_data["saved_prompt_name"] = save_prompt

        return output_data

    except Exception as e:
        raise SynthLangException(f"Evolution failed: {str(e)}")


def optimize_prompt(prompt: str) -> Dict[str, Any]:
    """
    Optimize a given prompt using DSPy techniques.

    :param prompt: The prompt to be optimized.
    :return: Dictionary with "original", "optimized", "improvements", "metrics".
    :raises SynthLangException: if optimization fails.
    """
    config_data = load_config()
    api_key = get_api_key()

    lm = dspy.LM(model=config_data.model, api_key=api_key)
    dspy.configure(lm=lm)

    optimizer = PromptOptimizer(lm=lm)
    try:
        result = optimizer.optimize(prompt)
        return {
            "original": result["original"],
            "optimized": result["optimized"],
            "improvements": result["improvements"],
            "metrics": result["metrics"],
        }
    except Exception as e:
        raise SynthLangException(f"Optimization failed: {str(e)}")


def save_prompt(
    name: str, prompt_content: str, metadata: Optional[str] = None
) -> None:
    """
    Save a prompt with optional metadata.

    :param name: Name to save the prompt under.
    :param prompt_content: The prompt content itself.
    :param metadata: JSON string containing metadata (optional).
    :raises SynthLangException: if save fails.
    """
    try:
        manager = PromptManager()
        meta_dict = json.loads(metadata) if metadata else None
        manager.save(name, prompt_content, meta_dict)
    except Exception as e:
        raise SynthLangException(f"Failed to save prompt: {str(e)}")


def load_prompt(name: str) -> Dict[str, Any]:
    """
    Load a saved prompt by name.

    :param name: Name of the prompt to load.
    :return: A dictionary containing the prompt data:
        {
            "name": ...,
            "prompt": ...,
            "metadata": ...
        }
    :raises SynthLangException: if load fails.
    """
    try:
        manager = PromptManager()
        data = manager.load(name)
        return data
    except Exception as e:
        raise SynthLangException(f"Failed to load prompt: {str(e)}")


def list_prompts() -> List[Dict[str, Any]]:
    """
    List all saved prompts.

    :return: A list of dictionaries, each containing:
        {
            "name": ...,
            "prompt": ...,
            "metadata": ...
        }
    :raises SynthLangException: if listing fails.
    """
    try:
        manager = PromptManager()
        prompts = manager.list()
        return prompts
    except Exception as e:
        raise SynthLangException(f"Failed to list prompts: {str(e)}")


def delete_prompt(name: str) -> None:
    """
    Delete a saved prompt by name.

    :param name: Name of prompt to delete.
    :raises SynthLangException: if deletion fails.
    """
    try:
        manager = PromptManager()
        manager.delete(name)
    except Exception as e:
        raise SynthLangException(f"Failed to delete prompt: {str(e)}")


def compare_prompts(prompt1: str, prompt2: str) -> Dict[str, Any]:
    """
    Compare two saved prompts by name.

    :param prompt1: Name of the first prompt.
    :param prompt2: Name of the second prompt.
    :return: A dictionary containing comparison details, including differences in fitness and more.
    :raises SynthLangException: if comparison fails.
    """
    try:
        manager = PromptManager()
        result = manager.compare(prompt1, prompt2)
        return result
    except Exception as e:
        raise SynthLangException(f"Failed to compare prompts: {str(e)}")


def classify_text(
    text: str, labels: List[str], model_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Classify a given piece of text using a (possibly trained) PromptClassifier.

    :param text: The text to classify.
    :param labels: List of possible labels.
    :param model_path: Path to a saved classifier model (optional).
    :return: Dictionary with "input", "label", and "explanation".
    :raises SynthLangException: if classification fails.
    """
    config_data = load_config()
    api_key = get_api_key()

    lm = dspy.LM(model=config_data.model, api_key=api_key)
    dspy.configure(lm=lm)

    classifier = PromptClassifier(lm=lm, labels=labels)
    if model_path:
        classifier.load(model_path)

    try:
        result = classifier.classify(text)
        return {
            "input": result["input"],
            "label": result["label"],
            "explanation": result["explanation"],
        }
    except Exception as e:
        raise SynthLangException(f"Classification failed: {str(e)}")


def train_classifier(
    train_data_path: str,
    labels: List[str],
    save_model_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Train a classifier with the given training data.

    :param train_data_path: Path to a JSON file with training examples.
    :param labels: List of possible labels.
    :param save_model_path: If provided, save the trained classifier to this path.
    :return: A dictionary with keys like "examples_used" and "final_accuracy".
    :raises SynthLangException: if training fails.
    """
    config_data = load_config()
    api_key = get_api_key()

    lm = dspy.LM(model=config_data.model, api_key=api_key)
    dspy.configure(lm=lm)

    with open(train_data_path) as f:
        data = json.load(f)
        examples = data.get("examples", [])

    classifier = PromptClassifier(lm=lm, labels=labels)

    try:
        result = classifier.train(examples)
        output_data = {
            "examples_used": result["examples_used"],
            "final_accuracy": result["final_accuracy"],
        }
        if save_model_path:
            classifier.save(save_model_path)
            output_data["model_saved_to"] = save_model_path
        return output_data
    except Exception as e:
        raise SynthLangException(f"Training failed: {str(e)}")


def evaluate_classifier(
    test_data_path: str, model_path: str
) -> Dict[str, Any]:
    """
    Evaluate a trained classifier on test data.

    :param test_data_path: Path to a JSON file with test examples.
    :param model_path: Path to the saved classifier model.
    :return: A dictionary with "examples" and "accuracy".
    :raises SynthLangException: if evaluation fails.
    """
    config_data = load_config()
    api_key = get_api_key()

    lm = dspy.LM(model=config_data.model, api_key=api_key)
    dspy.configure(lm=lm)

    with open(test_data_path) as f:
        data = json.load(f)
        examples = data.get("examples", [])

    classifier = PromptClassifier(lm=lm, labels=[])
    classifier.load(model_path)

    try:
        result = classifier.evaluate(examples)
        return {"examples": result["examples"], "accuracy": result["accuracy"]}
    except Exception as e:
        raise SynthLangException(f"Evaluation failed: {str(e)}")


def show_config() -> Dict[str, Any]:
    """
    Return the current configuration (as a dictionary).
    :raises SynthLangException: if configuration cannot be loaded.
    """
    config_data = load_config()
    return config_data.model_dump()


def set_config_value(key: str, value: str) -> Dict[str, Any]:
    """
    Update a configuration value by key.

    :param key: The configuration key to update.
    :param value: The new value to set.
    :return: The updated configuration (as a dictionary).
    :raises SynthLangException: if update fails.
    """
    config_manager = ConfigManager()
    try:
        updated_config = config_manager.update({key: value})
        return updated_config.model_dump()
    except Exception as e:
        raise SynthLangException(f"Failed to update configuration: {str(e)}")


import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from pydantic import BaseModel

# Suppose these come from your "refactored" SynthLang code
# (the new Python functions that do not rely on click)
from synthlang.core_refactored import (
    SynthLangException,
    classify_text,
    compare_prompts,
    delete_prompt,
    evaluate_classifier,
    evolve_prompt,
    generate_system_prompt,
    list_prompts,
    load_prompt,
    optimize_prompt,
    save_prompt,
    set_config_value,
    show_config,
    train_classifier,
    translate_prompt,
)

from lionagi.protocols.generic.event import EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.service.imodel import APICalling, iModel


@dataclass
class SynthLangResult:
    """
    Container for storing results from a SynthLang method call.
    You can attach additional metrics, perplexity, cost, logs, etc.
    """

    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


class SynthLangIntegration:
    """
    Demonstrates how to integrate the "refactored" SynthLang functions into
    your lionagi-based asynchronous architecture.

    This class expects a lionagi `iModel` for logging/queuing calls, but
    you can also pass in separate ones for 'chat_model' vs. 'parse_model' or
    do your own concurrency if you prefer.
    """

    def __init__(self, chat_model: iModel):
        self.chat_model = chat_model

    async def _run_synthlang_call(
        self, func_name: str, func, *args, **kwargs
    ) -> SynthLangResult:
        """
        A helper that wraps any SynthLang function call into an async event,
        logs the outcome, and returns a structured SynthLangResult.

        func_name: e.g., "translate_prompt", for logging
        func: the actual function to call
        """
        # Create an APICalling to track this operation in your event pipeline
        api_call = APICalling(
            payload={"function": func_name, "args": args, "kwargs": kwargs},
            headers={},
            endpoint=self.chat_model.endpoint,
            is_cached=False,
            should_invoke_endpoint=False,  # We won't do a real HTTP call for local function
        )
        api_call.execution.status = EventStatus.PENDING
        self.chat_model.executor.pile_[api_call.id] = api_call

        try:
            # Mark it "RUNNING"
            api_call.execution.status = EventStatus.RUNNING

            # Actual synchronous call to the refactored SynthLang function
            result = func(*args, **kwargs)

            # Mark success
            api_call.execution.status = EventStatus.COMPLETED
            api_call.response_obj = result
            api_call.execution.response = (
                result if isinstance(result, dict) else {}
            )

            return SynthLangResult(success=True, data=result)

        except SynthLangException as e:
            api_call.execution.status = EventStatus.FAILED
            api_call.execution.error = str(e)
            logging.error(f"[SynthLangIntegration] {func_name} failed: {e}")
            return SynthLangResult(success=False, data={}, error=str(e))

        except Exception as e:
            api_call.execution.status = EventStatus.FAILED
            api_call.execution.error = str(e)
            logging.error(
                f"[SynthLangIntegration] {func_name} unexpected error: {e}"
            )
            return SynthLangResult(success=False, data={}, error=str(e))

        finally:
            # Log the event; you could also store perplexity or cost metrics here
            log_msg = Log(
                content={
                    "function": func_name,
                    "payload": api_call.payload,
                    "status": str(api_call.execution.status),
                    "error": api_call.execution.error,
                }
            )
            self.chat_model.executor.log(log_msg)

    # -------------------------------------------------------------------------
    # Examples of async methods that wrap each refactored function
    # -------------------------------------------------------------------------

    async def translate(
        self,
        source: str,
        framework: str = "synthlang",
        show_metrics: bool = False,
        config_overrides: Dict[str, Any] = None,
        **kwargs,
    ) -> SynthLangResult:
        """
        Translate a natural language prompt to SynthLang or another framework.
        """
        # You can incorporate config overrides, i.e., set_config_value(...) if needed
        if config_overrides:
            for key, value in config_overrides.items():
                set_config_value(key, value)

        return await self._run_synthlang_call(
            "translate_prompt",
            translate_prompt,
            source=source,
            framework=framework,
            show_metrics=show_metrics,
            **kwargs,
        )

    async def generate(self, task: str, **kwargs) -> SynthLangResult:
        """
        Generate a system prompt based on a task description.
        """
        return await self._run_synthlang_call(
            "generate_system_prompt",
            generate_system_prompt,
            task=task,
            **kwargs,
        )

    async def evolve(
        self,
        seed: str,
        generations: int = 10,
        population: int = 5,
        mutation_rate: float = 0.3,
        tournament_size: int = 3,
        fitness: str = "hybrid",
        save_lineage: bool = False,
        test_cases: Optional[str] = None,
        save_prompt: Optional[str] = None,
        **kwargs,
    ) -> SynthLangResult:
        """
        Evolve a prompt using genetic algorithms & self-play tournaments.
        """
        return await self._run_synthlang_call(
            "evolve_prompt",
            evolve_prompt,
            seed=seed,
            generations=generations,
            population=population,
            mutation_rate=mutation_rate,
            tournament_size=tournament_size,
            fitness=fitness,
            save_lineage=save_lineage,
            test_cases=test_cases,
            save_prompt=save_prompt,
            **kwargs,
        )

    async def optimize(self, prompt: str, **kwargs) -> SynthLangResult:
        """
        Optimize a prompt using DSPy-based improvements.
        """
        return await self._run_synthlang_call(
            "optimize_prompt", optimize_prompt, prompt=prompt, **kwargs
        )

    # -------------------------------------------------------------------------
    # Prompt Manager Methods (save, load, list, delete, compare)
    # -------------------------------------------------------------------------
    async def prompt_save(
        self, name: str, prompt_content: str, metadata: str = None
    ) -> SynthLangResult:
        return await self._run_synthlang_call(
            "save_prompt",
            save_prompt,
            name=name,
            prompt_content=prompt_content,
            metadata=metadata,
        )

    async def prompt_load(self, name: str) -> SynthLangResult:
        return await self._run_synthlang_call(
            "load_prompt", load_prompt, name=name
        )

    async def prompt_list(self) -> SynthLangResult:
        return await self._run_synthlang_call("list_prompts", list_prompts)

    async def prompt_delete(self, name: str) -> SynthLangResult:
        return await self._run_synthlang_call(
            "delete_prompt", delete_prompt, name=name
        )

    async def prompt_compare(
        self, prompt1: str, prompt2: str
    ) -> SynthLangResult:
        return await self._run_synthlang_call(
            "compare_prompts",
            compare_prompts,
            prompt1=prompt1,
            prompt2=prompt2,
        )

    # -------------------------------------------------------------------------
    # Classifier Methods (classify, train, evaluate)
    # -------------------------------------------------------------------------
    async def classify_text(
        self, text: str, labels: list[str], model_path: Optional[str] = None
    ) -> SynthLangResult:
        return await self._run_synthlang_call(
            "classify_text",
            classify_text,
            text=text,
            labels=labels,
            model_path=model_path,
        )

    async def train_classifier(
        self,
        train_data_path: str,
        labels: list[str],
        save_model_path: Optional[str] = None,
    ) -> SynthLangResult:
        return await self._run_synthlang_call(
            "train_classifier",
            train_classifier,
            train_data_path=train_data_path,
            labels=labels,
            save_model_path=save_model_path,
        )

    async def evaluate_classifier(
        self, test_data_path: str, model_path: str
    ) -> SynthLangResult:
        return await self._run_synthlang_call(
            "evaluate_classifier",
            evaluate_classifier,
            test_data_path=test_data_path,
            model_path=model_path,
        )

    # -------------------------------------------------------------------------
    # Config Methods
    # -------------------------------------------------------------------------
    async def show_config(self) -> SynthLangResult:
        """
        Show current SynthLang configuration as a dictionary.
        """
        return await self._run_synthlang_call("show_config", show_config)

    async def set_config(self, key: str, value: str) -> SynthLangResult:
        """
        Update a configuration key with a new value.
        """
        return await self._run_synthlang_call(
            "set_config_value", set_config_value, key=key, value=value
        )
