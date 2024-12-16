PLAN_PROMPT = """
Develop a high-level plan with {num_steps} distinct steps. Each step should:
1. Represent a major milestone or phase
2. Be logically sequenced for dependencies
3. Be clearly distinct from other steps
4. Have measurable completion criteria
5. Be suitable for further decomposition
"""

EXPANSION_PROMPT = """
Break down a high-level plan into detailed concrete executable actions. Each step should:
- Ensure actions are atomic and verifiable
- Include necessary context and preconditions
- Specify expected outcomes and validations
- Maintain sequential dependencies
- Be self-contained with clear scope
- Include all required context/parameters
- Have unambiguous success criteria
- Specify error handling approach
- Define expected outputs
"""
