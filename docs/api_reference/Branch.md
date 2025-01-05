# Branch API Reference

## Overview

Branch manages conversation threads by integrating message handling, tool execution, model operations, and inter-branch communication.

## Core Operations

### Communication Flow

```python
async def communicate(
    self,
    instruction: Instruction | JsonValue = None,
    guidance: JsonValue = None,
    context: JsonValue = None,
    request_model: type[BaseModel] | BaseModel | None = None,
    response_format: type[BaseModel] = None,
    request_fields: dict | list[str] = None,
    progression: ID.IDSeq = None,
    imodel: iModel = None,
    chat_model: iModel = None,
    parse_model: iModel = None,
    skip_validation: bool = False,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    num_parse_retries: int = 3,
    fuzzy_match_kwargs: dict = None,
    clear_messages: bool = False,
    **kwargs
) -> Any:
    """Basic communication without tool execution.
    
    Examples:
        # Simple query
        response = await branch.communicate(
            instruction="Summarize the key points",
            context={"text": long_text}
        )
        
        # With structured response
        report = await branch.communicate(
            instruction="Analyze code quality",
            response_format=QualityReport,
            context={"code": source_code}
        )
    """
```

### Tool Operations 

```python
async def operate(
    self,
    instruct: Instruct = None,
    instruction: Instruction | JsonValue = None,
    guidance: JsonValue = None,
    context: JsonValue = None,
    progression: Progression = None,
    chat_model: iModel = None,
    invoke_actions: bool = True,
    tool_schemas: list[dict] = None,
    tools: ToolRef = None,
    operative: Operative = None,
    response_format: type[BaseModel] = None,
    return_operative: bool = False,
    actions: bool = False,
    reason: bool = False,
    action_kwargs: dict = None,
    field_models: list[FieldModel] = None,
    handle_validation: Literal["raise", "return_value", "return_none"] = "return_value",
    **kwargs
) -> list | BaseModel | None | dict | str:
    """Execute operation flow with tools.
    
    Examples:
        # Code analysis with multiple tools
        results = await branch.operate(
            instruction="Fix code style issues",
            tools=["formatter", "linter", "style_checker"],
            response_format=CodeFixReport,
            invoke_actions=True
        )
        
        # Data analysis with reasoning
        insights = await branch.operate(
            instruction="Analyze performance trends",
            tools=["data_analyzer", "visualizer"],
            response_format=PerformanceReport,
            reason=True  # Include analysis reasoning
        )
    """
```

### Model Interaction

```python
async def invoke_chat(
    self,
    instruction=None,
    guidance=None,
    context=None,
    sender=None,
    recipient=None,
    request_fields=None,
    response_format: type[BaseModel] = None,
    progression=None,
    imodel: iModel = None,
    tool_schemas=None,
    images: list = None,
    image_detail: Literal["low", "high", "auto"] = None,
    **kwargs
) -> tuple[Instruction, AssistantResponse]:
    """Direct model invocation with response handling.
    
    Examples:
        # Complex instruction with context
        instruction, response = await branch.invoke_chat(
            instruction={
                "task": "Optimize database queries",
                "focus": ["performance", "indexing"]
            },
            context={
                "current_schema": schema,
                "query_logs": logs
            },
            tool_schemas=db_tools
        )
    """
```

### Branch Communication

```python
def send(
    self,
    recipient: IDType,
    category: PackageCategory | str,
    item: Any,
    request_source: IDType | None = None
) -> None:
    """Send content to another branch.
    
    Categories:
        - message: Share conversations
        - tool: Share tool access
        - imodel: Share model configurations
    """

def receive(
    self,
    sender: IDType,
    message: bool = False,
    tool: bool = False,
    imodel: bool = False
) -> None:
    """Process received content from a branch."""
```

## Common Use Patterns

### Multi-Stage Analysis

```python
# Analysis with multiple tools and reasoning
results = await branch.operate(
    instruction={
        "task": "Improve code quality",
        "aspects": ["style", "performance", "security"]
    },
    tools=["analyzer", "profiler", "security_scanner"],
    response_format=CodeAuditReport,
    reason=True,  # Include reasoning for findings
    invoke_actions=True
)

# Structured follow-up
fixes = await branch.operate(
    instruction={
        "task": "Fix identified issues",
        "priority": "high"
    },
    tools=["fixer", "formatter"],
    context={"audit": results},
    response_format=FixReport,
    invoke_actions=True
)
```

### Branch Coordination

```python
# Research and implementation coordination
findings = await research_branch.operate(
    instruction="Research optimal algorithms",
    tools=["paper_analyzer", "benchmark_tool"],
    response_format=ResearchFindings
)

# Implement based on research
implementation = await impl_branch.operate(
    instruction="Implement recommended algorithm",
    context=findings.model_dump(),
    tools=["code_generator", "test_framework"],
    response_format=Implementation
)
```
