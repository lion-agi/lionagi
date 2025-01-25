# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

PROMPT = """Perform a brainstorm session. Generate {num_instruct} concise and distinct instructions (Instruct), each representing a potential next step. We will run them in parallel under the same context. Ensure each idea:

1. Adheres to project guidelines and standards.
2. Maintains a unique perspective or approach.
3. Remains succinct yet sufficiently detailed.
4. Flags any step that needs deeper expansion.

Aim for clarity, practicality, and adherence to the project's core principles."""
