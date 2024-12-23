# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

function_field_description = (
    "Name of the function to call from the provided `tool_schemas`. "
    "If no `tool_schemas` exist, set to None or leave blank. "
    "Never invent new function names outside what's given."
)

arguments_field_description = (
    "Dictionary of arguments for the chosen function. "
    "Use only argument names/types defined in `tool_schemas`. "
    "Never introduce extra argument names."
)

action_required_field_description = (
    "Whether this step strictly requires performing actions. "
    "If true, the requests in `action_requests` must be fulfilled, "
    "assuming `tool_schemas` are available. "
    "If false or no `tool_schemas` exist, actions are optional."
)

action_requests_field_description = (
    "List of actions to be executed when `action_required` is true. "
    "Each action must align with the available `tool_schemas`. "
    "Leave empty if no actions are needed."
)

confidence_description = (
    "Numeric confidence score (0.0 to 1.0, up to three decimals) indicating "
    "how well you've met user expectations. Use this guide:\n"
    "  • 1.0: Highly confident\n"
    "  • 0.8-1.0: Reasonably sure\n"
    "  • 0.5-0.8: Re-check or refine\n"
    "  • 0.0-0.5: Off track"
)

instruction_field_description = (
    "A clear, actionable task definition. Specify:\n"
    "1) The primary goal or objective\n"
    "2) Key success criteria or constraints\n"
    "\n"
    "Guidelines:\n"
    "- Start with a direct action verb (e.g., 'Analyze', 'Generate', 'Create')\n"
    "- Include scope, boundaries, or constraints\n"
    "- Provide success criteria if relevant\n"
    "- For complex tasks, break them into logical steps"
)

guidance_field_description = (
    "Strategic direction and constraints for executing the task. "
    "Include:\n"
    "1) Preferred methods or frameworks\n"
    "2) Quality benchmarks (e.g., speed, clarity)\n"
    "3) Resource or environmental constraints\n"
    "4) Relevant compliance or standards\n"
    "Use None if no special guidance."
)

context_field_description = (
    "Background information and current-state data needed for the task. "
    "Should be:\n"
    "1) Directly relevant\n"
    "2) Sufficient to perform the task\n"
    "3) Free of extraneous detail\n"
    "Include environment, prior outcomes, system states, or dependencies. "
    "Use None if no additional context is needed."
)

reason_field_description = (
    "Include a thoughtful explanation of decisions, trade-offs, "
    "and insights. Encourage deeper introspection on why certain "
    "choices were made, potential alternatives, and how confidence "
    "was shaped. If not needed, set to None."
)

actions_field_description = (
    "Controls execution mode. "
    "True: Execute specified actions. "
    "False: Analysis/recommendations only. "
    "None: Contextual execution."
)
