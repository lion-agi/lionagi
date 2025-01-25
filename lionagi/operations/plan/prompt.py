# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

PLAN_PROMPT = """
Develop a high-level plan containing {num_steps} distinct steps. Each step must:
1. Represent a clear milestone or phase.
2. Follow a logical sequence, respecting inter-step dependencies.
3. Differ clearly from other steps.
4. Have measurable completion criteria.
5. Be open to further breakdown if needed.

Keep each step concise yet actionable, ensuring the overall plan remains coherent.
"""

EXPANSION_PROMPT = """
Transform each high-level plan step into detailed, executable actions. For every step:

1. Keep actions atomic, verifiable, and clearly scoped.
2. Include essential context and preconditions.
3. Define expected outcomes, success criteria, and validations.
4. Respect sequential dependencies and error handling.
5. Provide all necessary parameters and specify outputs.

Ensure each action is self-contained yet fits within the larger plan.
"""
