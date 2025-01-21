import logging
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from lionagi.operatives.forms.form import Form
from lionagi.session.branch import Branch


class OptimizationType(str, Enum):
    PROMPT = "prompt"  # Optimize system/instruction text
    OPERATION = "operation"  # Optimize operation usage
    FLOW = "flow"  # Optimize flow definitions
    TOOLS = "tools"  # Optimize tool usage patterns


class OptimizationForm(Form):
    """
    Defines how a user requests an optimization.
    `output_fields` ensures required fields are validated.
    """

    target: OptimizationType
    metrics: list[str] = Field(
        default_factory=list
    )  # e.g. ["response_quality", "token_usage"]
    constraints: dict[str, Any] = Field(default_factory=dict)
    max_attempts: int = 5

    # Depending on target, we can store relevant data:
    template: Optional[str] = None  # For PROMPT
    flow_def: Optional[str] = None  # For FLOW
    tools: Optional[list[str]] = None  # For TOOLS

    # For evaluating improvements
    eval_instruction: Optional[str] = None
    response_format: Optional[Any] = None

    # Indicate which fields must be set for "completeness"
    output_fields = ["target", "metrics"]


class OptimizationResponse(BaseModel):
    """
    Outcome of the optimization attempt:
    - original: Original config or data
    - optimized: The improved config
    - improvements: Key metric changes
    - steps_taken: Attempts made
    - metadata: Additional info
    """

    original: dict[str, Any]
    optimized: dict[str, Any]
    improvements: dict[str, float]
    steps_taken: int
    metadata: dict[str, Any] = Field(default_factory=dict)


def _generate_prompt_variations(
    original: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Placeholder: Generate variations of prompt/system messages for optimization.
    'original' might contain:
       - system
       - instruction_template
       - guidance_template
    Return a list of possible improved configs.
    """
    variations = [original]

    # Variation #1: more structured instructions
    enhanced = {
        "system": original["system"],
        "instruction_template": (
            original["instruction_template"] + "\n[Structured Steps Required]"
        ),
        "guidance_template": original["guidance_template"],
    }
    variations.append(enhanced)

    # Variation #2: more or fewer tokens in system guidance
    guided = {
        "system": original["system"],
        "instruction_template": original["instruction_template"],
        "guidance_template": (
            original["guidance_template"]
            + "\nFocus on brevity while ensuring clarity."
        ),
    }
    variations.append(guided)

    return variations


async def _evaluate_prompt(
    branch: Branch,
    prompt_config: dict[str, Any],
    eval_instruction: Optional[str],
    metrics: list[str],
) -> dict[str, float]:
    """
    Evaluate how well a prompt configuration performs on the given metrics.
    - prompt_config: { system, instruction_template, guidance_template, ... }
    - eval_instruction: The user or system test query
    - metrics: e.g. ["response_quality", "token_usage"]

    For simplicity, we'll do a single test with `branch.communicate`.
    In practice you might run multiple queries or a scoring tool.
    """
    if not eval_instruction:
        # No test means no real measure
        return {m: 0.0 for m in metrics}

    # Temporarily store old system
    original_system = branch.msgs.system

    # Temporarily set new system
    new_system = prompt_config.get("system", "")
    branch.msgs.add_message(system=new_system)

    # Attempt to do a single conversation
    result_text = ""
    try:
        # Chat with custom 'instruction_template' or 'guidance_template' if needed
        response = await branch.communicate(
            instruction=(
                prompt_config.get("instruction_template") or eval_instruction
            ),
            guidance=prompt_config.get("guidance_template", ""),
            skip_validation=True,  # Just get raw text
        )
        if isinstance(response, str):
            result_text = response
        else:
            result_text = str(response)
    except Exception as ex:
        logging.warning(f"Prompt evaluation failed: {ex}")

    # Revert system back
    branch.msgs.set_system(original_system)

    # Evaluate metrics
    # We'll do a trivial approach for demonstration
    scores = {}
    for m in metrics:
        if m == "response_quality":
            # a naive approach: length-based or containing certain words
            scores[m] = 1.0 if "ERROR" not in result_text else 0.2
        elif m == "token_usage":
            # We'll guess short response is better => 1.0 - scaled by length
            length = len(result_text)
            scores[m] = max(0.0, 1.0 - (length / 1000.0))
        else:
            # default
            scores[m] = 0.5
    return scores


def _apply_prompt_improvement(branch: Branch, best_config: dict[str, Any]):
    """
    Actually update the Branch with the best prompt config discovered.
    e.g. set new system message, or store metadata for instruction template.
    """
    if "system" in best_config:
        branch.msgs.set_system(best_config["system"])
    # Optionally store the instruction/guidance as metadata
    branch.metadata["optim_instruction_template"] = best_config.get(
        "instruction_template", ""
    )
    branch.metadata["optim_guidance_template"] = best_config.get(
        "guidance_template", ""
    )
