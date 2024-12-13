# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0


# Field Descriptions for LLM Task Execution
## Core Fields

function_field_description = """
Specify the exact name of the function to call from available tool_schemas.

Requirements:
1. Choose only from provided tool_schemas
2. Set to None if no tool_schemas available
3. Do not invent or modify function names

Validation:
- Verify function exists in schema before calling
- Confirm all required parameters are available
- Check function compatibility with current context

Error Handling:
- Report immediately if function not found
- Provide clear error context if validation fails
"""

arguments_field_description = """
Provide function arguments as a schema-compliant dictionary.

Requirements:
1. Use only schema-specified argument names and types
2. Validate all arguments before submission
3. Handle missing or default values explicitly

Validation Steps:
- Type checking for all arguments
- Range/boundary validation where applicable
- Format verification for structured data
- Null/empty value handling

Error Cases:
- Invalid argument types
- Missing required arguments
- Out-of-range values
"""

action_required_field_description = """
Indicate whether actions must be performed (True/False).

Decision Matrix:
| Condition          | Value | Behavior                   |
|--------------------| ------|----------------------------|
| Mandatory actions  | True  | Must complete all actions  |
| Optional actions   | False | Actions at discretion      |
| No tool_schemas    | None  | Field ignored              |

Validation:
1. Verify consistency with available tools
2. Confirm action feasibility
3. Check dependencies satisfied
"""

action_requests_field_description = """
List specific actions required for task completion.

Requirements:
1. Only use actions from tool_schemas
2. Verify prerequisites met
3. Validate action sequence feasibility

Validation Steps:
- Confirm each action exists in schema
- Verify action sequence logic
- Check resource availability
- Validate dependencies

Error Handling:
- Report invalid actions
- Handle missing dependencies
- Manage sequence conflicts
"""


## Quality Assurance

confidence_description = """
Provide numeric confidence score (0 to 1, 3 decimal places).

Scoring Matrix:
| Range         | Interpretation                   | Required Action            |
|---------------|----------------------------------|----------------------------|
| 1.000         | Complete confidence              | Proceed                    |
| 0.800-0.999   | High confidence                  | Continue with monitoring   |
| 0.500-0.799   | Moderate confidence              | Review and validate        |
| 0.000-0.499   | Low confidence                   | Stop and reassess          |

Validation Requirements:
1. Score must be justified with specific criteria
2. Include uncertainty factors
3. Document confidence calculation method

Quality Gates:
- Below 0.500: Must stop and reassess
- Below 0.800: Requires additional validation
- Below 1.000: Document any assumptions
"""

## Task Definition

instruction_field_description = """
Define primary task and success criteria.

Structure:
1. Action verb (e.g., Analyze, Create, Evaluate)
2. Clear deliverables
3. Success metrics
4. Completion criteria

Validation Requirements:
- Verify task clarity and scope
- Confirm measurable outcomes
- Check resource availability
- Validate timeline feasibility

Example Template:
"{Action} {Target} to achieve {Outcome} meeting {Criteria}"
"""

guidance_field_description = """
Provide strategic direction and constraints.

Required Components:
1. Methodology specification
2. Quality standards
3. Resource constraints
4. Performance requirements

Validation Steps:
- Verify methodology feasibility
- Confirm resource availability
- Check constraint consistency
- Validate quality metrics

Documentation:
- Record all assumptions
- Document trade-offs
- Track constraint impacts
"""


context_field_description = """
Supply essential background and current state.

Required Elements:
1. Historical context
2. Current state
3. Dependencies
4. Constraints

Validation:
- Verify context completeness
- Check dependency availability
- Confirm state currency
- Validate constraint applicability

Quality Requirements:
- Context must be relevant
- Information must be current
- Dependencies must be available
- Constraints must be valid
"""

## Execution Control

reason_field_description = """
Control reasoning detail inclusion.

Behavior Matrix:
| Value | Required Components               | Validation Steps               |
|-------|-----------------------------------|--------------------------------|
| True  | Full reasoning, confidence scores | Verify completeness, logic     |
| False | Results only                      | Validate outputs               |
| None  | Optional reasoning                | Check if included reasoning    |

Quality Requirements:
1. Logic must be clear and traceable
2. Decisions must be justified
3. Assumptions must be documented
4. Confidence scores must be supported
"""

actions_field_description = """
Control action execution requirements.

Behavior Matrix:
| Value | Required Components              | Validation Steps               |
|-------|----------------------------------|--------------------------------|
| True  | ActionRequestModels required     | Verify completeness            |
| False | No actions allowed               | Confirm no actions included    |
| None  | Actions optional                 | Validate if included           |

Quality Gates:
1. All actions must be schema-compliant
2. Dependencies must be satisfied
3. Resource requirements met
4. Success criteria defined
"""

# Example structures for each field to demonstrate proper formatting
instruction_examples = [
    "Analyze the sales_2023.csv dataset to identify revenue trends, focusing on month-over-month growth and seasonal patterns. Success criteria: identify top 3 growth periods and any statistically significant patterns.",
    "Create a Python function that validates email addresses with the following requirements: RFC 5322 compliance, DNS validation, and no disposable domains. Must complete validation within 100ms.",
    "Generate a weekly sales performance dashboard comparing actual vs target metrics, highlighting variances above 10% and tracking year-to-date progress.",
]

guidance_examples = [
    "Use statistical regression methods for trend analysis. Required accuracy >= 95%. Maximum processing time: 5 minutes. Output should include confidence intervals.",
    "Optimize code for readability and maintainability. Follow PEP 8 standards. Include docstrings and type hints. Minimum test coverage: 90%.",
    "Apply time series analysis with seasonal adjustment. Handle missing data using forward fill. Flag outliers beyond 3 standard deviations.",
]

context_examples = [
    "Previous analysis showed strong seasonal patterns in Q4. System is running in production environment with full resource allocation. Required dependencies: pandas 1.5+, numpy 1.20+",
    "Current system load is at 60% capacity. All monitoring systems are active. Recent data quality audit shows 99.9% completeness.",
    "Operating in test environment during non-peak hours. Baseline metrics from last month available for comparison. All dependencies up to date.",
]


instruct_model_examples = [
    {
        "instruction": "Process daily sales data and generate trending report",
        "guidance": "Use 7-day moving average. Flag anomalies. Maximum runtime: 10 minutes",
        "context": "Production environment. Previous day's data verified. All systems operational",
    },
    {
        "instruction": "Evaluate API endpoint performance under load",
        "guidance": "Measure latency, error rates, and throughput. Alert if p95 latency > 200ms",
        "context": "Testing environment. Baseline metrics available. Normal business hours",
    },
]

operation_instruct_model_examples = [
    {
        "instruction": "Process daily sales data and generate trending report",
        "guidance": "Use 7-day moving average. Flag anomalies. Maximum runtime: 10 minutes",
        "context": "Production environment. Previous day's data verified. All systems operational",
        "reason": True,
        "actions": True,
    },
    {
        "instruction": "Evaluate API endpoint performance under load",
        "guidance": "Measure latency, error rates, and throughput. Alert if p95 latency > 200ms",
        "context": "Testing environment. Baseline metrics available. Normal business hours",
        "reason": True,
        "actions": False,
    },
]


"""Field description for InstructModel."""
# The model description can stay detailed but should use natural language
instruct_model_description = """
Define clear, actionable instructions for task execution following these key principles:

1. Task Definition
   - Start with a clear objective
   - Specify measurable outcomes
   - Define success criteria
   - List any constraints

2. Execution Guidelines
   - Specify preferred methods
   - Set quality requirements
   - Define validation steps
   - Include error handling

3. Required Context
   - Note environmental conditions
   - List dependencies
   - Specify resource needs
   - Mention any prerequisites

4. Quality Standards
   - Define acceptance criteria
   - Specify validation points
   - Set performance targets
   - List required checks

Best Practices:
- Use clear, direct language
- Include specific metrics
- Define clear pass/fail criteria
- Note any assumptions
- Specify validation requirements

Each instruction should be:
- Specific and actionable
- Measurable and verifiable
- Clear about constraints
- Complete with success criteria
"""


__all__ = [
    "function_field_description",
    "arguments_field_description",
    "action_required_field_description",
    "action_requests_field_description",
    "confidence_description",
    "instruction_field_description",
    "guidance_field_description",
    "context_field_description",
    "reason_field_description",
    "actions_field_description",
    "instruction_examples",
    "guidance_examples",
    "context_examples",
    "instruct_model_description",
    "instruct_model_examples",
    "operation_instruct_model_examples",
]
