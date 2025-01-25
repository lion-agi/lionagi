# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""deprecated"""

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
