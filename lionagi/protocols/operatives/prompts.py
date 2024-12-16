from pydantic import JsonValue

function_field_description = (
    "Specify the name of the function to execute. **Choose "
    "from the provided `tool_schemas`; do not invent function names.**"
    "Only provide function names if tool_schemas are provided. Otherwise, "
    "must leave blank or set to None."
)

arguments_field_description = (
    "Provide the arguments to pass to the function as a "
    "dictionary. **Use argument names and types as specified in the "
    "`tool_schemas`; do not invent argument names.**"
)

action_required_field_description = (
    "Specify whether the step requires actions to be "
    "performed. If **True**, the actions in `action_requests` "
    "must be performed. If **False**, the actions in "
    "`action_requests` are optional. If no tool_schemas"
    " are provided, this field is ignored."
)

action_requests_field_description = (
    "List of actions to be performed if `action_required` "
    "is **True**. Leave empty if no action is required. "
    "**When providing actions, you must choose from the "
    "provided `tool_schemas`. Do not invent function or "
    "argument names.**"
)

confidence_description = (
    "Provide an objective numeric confidence score between 0 and 1 (with 3 "
    "decimal places) indicating how likely you successfully achieved the task"
    " according to user expectation. Interpret the score as:\n"
    "- **1**: Very confident in a good job.\n"
    "- **0**: Not confident at all.\n"
    "- **[0.8, 1]**: You can continue the path of reasoning if needed.\n"
    "- **[0.5, 0.8)**: Recheck your reasoning and consider reverting to a "
    "previous, more confident reasoning path.\n"
    "- **[0, 0.5)**: Stop because the reasoning is starting to be off track."
)

instruction_field_description = (
    "Define the core task or instruction to be executed. Your instruction should:\n\n"
    "1. Be specific and actionable\n"
    "2. Clearly state the expected outcome\n"
    "3. Include any critical constraints or requirements\n\n"
    "**Guidelines for writing effective instructions:**\n"
    "- Start with a clear action verb (e.g., analyze, create, evaluate)\n"
    "- Specify the scope and boundaries of the task\n"
    "- Include success criteria when applicable\n"
    "- Break complex tasks into distinct steps\n\n"
    "**Examples:**\n"
    "- 'Analyze the provided sales data and identify top 3 performing products'\n"
    "- 'Generate a Python function that validates email addresses'\n"
    "- 'Create a data visualization showing monthly revenue trends'"
)

guidance_field_description = (
    "Provide strategic direction and constraints for task execution.\n\n"
    "**Key components to include:**\n"
    "1. Methodological preferences\n"
    "2. Quality standards and requirements\n"
    "3. Specific limitations or boundaries\n"
    "4. Performance expectations\n\n"
    "**Best practices:**\n"
    "- Be explicit about any assumptions that should be made\n"
    "- Specify preferred approaches or techniques\n"
    "- Detail any constraints on resources or methods\n"
    "- Include relevant standards or compliance requirements\n\n"
    "Leave as None if no specific guidance is needed beyond the instruction."
)

context_field_description = (
    "Supply essential background information and current state data required for "
    "task execution.\n\n"
    "**Include relevant details about:**\n"
    "1. Environmental conditions\n"
    "2. Historical context\n"
    "3. Related systems or processes\n"
    "4. Previous outcomes or decisions\n\n"
    "**Context should:**\n"
    "- Be directly relevant to the task\n"
    "- Provide necessary background without excess detail\n"
    "- Include any dependencies or prerequisites\n"
    "- Specify the current state of the system\n\n"
    "Set to None if no additional context is required."
)

reason_field_description = (
    "Control whether detailed reasoning should be included in the response.\n\n"
    "**When set to True:**\n"
    "- Must include a ReasonModel explaining decision rationale\n"
    "- Should detail key decision points\n"
    "- Must provide confidence scores for decisions\n"
    "- Should explain trade-offs considered\n\n"
    "**When set to False:**\n"
    "- Skip detailed reasoning\n"
    "- Focus on direct results\n"
    "- Omit confidence scoring\n\n"
    "Set to None to make reasoning optional based on context."
)

actions_field_description = (
    "Specify whether concrete actions should be taken as part of task execution.\n\n"
    "**When set to True:**\n"
    "- Must include appropriate ActionRequestModels\n"
    "- Actions should directly relate to task goals\n"
    "- Each action must be properly structured and validated\n"
    "- Actions must use available tool schemas\n\n"
    "**When set to False:**\n"
    "- No actions should be included\n"
    "- Focus on analysis and recommendations\n\n"
    "Set to None to make actions optional based on requirements."
)

# Example structures for each field to demonstrate proper formatting
instruction_examples: list[JsonValue] = [
    "Analyze the dataset 'sales_2023.csv' and identify revenue trends",
    "Create a Python function to process customer feedback data",
    {
        "task": "data_analysis",
        "target": "sales_performance",
        "scope": ["revenue", "growth", "seasonality"],
    },
]

guidance_examples: list[JsonValue] = [
    "Use statistical methods for trend analysis",
    "Optimize for readability and maintainability",
    {
        "methods": ["regression", "time_series"],
        "constraints": {"memory": "2GB", "time": "5min"},
    },
]

context_examples: list[JsonValue] = [
    "Previous analysis showed seasonal patterns",
    {
        "prior_results": {"accuracy": 0.95},
        "system_state": "production",
        "dependencies": ["numpy", "pandas"],
    },
]

"""Field description for InstructModel."""

instruct_model_description = (
    "Generate structured instructions for task execution.\n\n"
    "**Key Components:**\n"
    "1. Task Definition: Clear description of what needs to be accomplished\n"
    "2. Execution Parameters: How the task should be performed\n"
    "3. Success Criteria: What constitutes successful completion\n"
    "4. Scope and Boundaries: Limits and constraints of the task\n\n"
    "**Structure Guidelines:**\n"
    "- `instruction`: Core task or objective to accomplish\n"
    "- `guidance`: Parameters, preferences, and constraints\n"
    "- `context`: Relevant background and environmental information\n"
    "- `reason`: Whether to include reasoning in output\n"
    "- `actions`: Whether specific actions are required\n\n"
    "**Best Practices:**\n"
    "- Keep instructions clear and specific\n"
    "- Provide necessary but not excessive detail\n"
    "- Define measurable outcomes\n"
    "- Include relevant dependencies\n"
    "- Specify critical constraints\n\n"
    "**Common Issues to Avoid:**\n"
    "- Vague or ambiguous directives\n"
    "- Missing essential context\n"
    "- Undefined success criteria\n"
    "- Incomplete requirements\n"
    "- Conflicting parameters\n\n"
    "Structure instructions to enable successful task execution while maintaining "
    "appropriate flexibility for implementation details."
)

instruct_model_examples = [
    {
        "instruction": "Process the input data according to specified requirements",
        "guidance": {
            "requirements": ["validation", "transformation", "aggregation"],
            "output_format": "structured_report",
            "quality_metrics": ["accuracy", "completeness"],
        },
        "context": {
            "input_source": "data_stream",
            "domain": "general",
            "priority": "standard",
        },
        "reason": True,
        "actions": True,
    },
    {
        "instruction": "Evaluate system performance against baseline metrics",
        "guidance": {
            "evaluation_criteria": [
                "response_time",
                "resource_usage",
                "error_rate",
            ],
            "methodology": "standard",
            "reporting": "detailed",
        },
        "context": {
            "environment": "test",
            "criticality": "medium",
            "constraints": {"time": "bounded"},
        },
        "reason": True,
        "actions": False,
    },
]


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
]
