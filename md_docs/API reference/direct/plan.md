# Plan

This API reference provides documentation for the `PlanTemplate` class and related functions for generating a step-by-step plan based on a given sentence or context using a language model.

## Table of Contents

1. [PlanTemplate](#plantemplate)
   - [Attributes](#attributes)
   - [Methods](#methods)
     - [`__init__`](#__init__)
2. [_plan](#_plan)
   - [Parameters](#parameters)
   - [Returns](#returns)
3. [plan](#plan)
   - [Parameters](#parameters-1)
   - [Returns](#returns-1)

## PlanTemplate

The `PlanTemplate` class is a subclass of `ScoredForm` and provides functionality for generating a step-by-step plan based on a given sentence or context using a language model.

### Attributes

- `template_name` (str): The name of the plan template (default: "default_plan").
- `sentence` (str | list | dict): The given sentence(s) or context to generate a plan for.
- `plan` (dict | str): The generated step-by-step plan, returned as a dictionary following the format `{step_n: {plan: ..., reason: ...}}`.
- `signature` (str): The signature indicating the input and output fields (default: "sentence -> plan").

### Methods

#### `__init__`

```python
def __init__(self, sentence=None, instruction=None, confidence_score=False, reason=False, num_step=3, **kwargs)
```

Initializes a new instance of the `PlanTemplate` class.

**Parameters:**
- `sentence` (Optional[str | list | dict]): The given sentence(s) or context to generate a plan for.
- `instruction` (Optional[str]): The instruction for generating the plan.
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for each step in the plan (default: False).
- `num_step` (int): The number of steps in the plan (default: 3).
- `**kwargs`: Additional keyword arguments.

## _plan

```python
async def _plan(sentence, *, instruction=None, branch=None, confidence_score=False, reason=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, return_branch=False, **kwargs)
```

Generates a step-by-step plan based on a given sentence or context using a language model.

### Parameters

- `sentence` (str | list | dict): The given sentence(s) or context to generate a plan for.
- `instruction` (Optional[str]): The instruction for generating the plan.
- `branch` (Optional[Branch]): The branch to use for plan generation. If not provided, a new branch will be created.
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for each step in the plan (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for plan generation.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for plan generation.
- `sender` (Optional[str]): The sender of the request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for plan generation.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `return_branch` (bool): Whether to return the branch along with the plan template (default: False).
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `Tuple[PlanTemplate, Branch] | PlanTemplate`: The plan template and optionally the branch if `return_branch` is True.

## plan

```python
async def plan(sentence, *, instruction=None, num_instances=1, branch=None, confidence_score=False, reason=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, return_branch=False, **kwargs)
```

Generates a step-by-step plan based on a given sentence or context using a language model, with the option to process multiple instances.

### Parameters

- `sentence` (str | list | dict): The given sentence(s) or context to generate a plan for.
- `instruction` (Optional[str]): The instruction for generating the plan.
- `num_instances` (int): The number of instances to process (default: 1).
- `branch` (Optional[Branch]): The branch to use for plan generation. If not provided, a new branch will be created.
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for each step in the plan (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for plan generation.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for plan generation.
- `sender` (Optional[str]): The sender of the request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for plan generation.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `return_branch` (bool): Whether to return the branch along with the plan template (default: False).
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `Tuple[PlanTemplate, Branch] | PlanTemplate | List[Tuple[PlanTemplate, Branch]] | List[PlanTemplate]`: The plan template(s) and optionally the branch(es) if `return_branch` is True, depending on the number of instances.

