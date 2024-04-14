# react

## Table of Contents

1. [ReactTemplate](#reacttemplate)
   - [Attributes](#attributes)
   - [Methods](#methods)
     - [`__init__`](#__init__)
2. [_react](#_react)
   - [Parameters](#parameters)
   - [Returns](#returns)
3. [react](#react)
   - [Parameters](#parameters-1)
   - [Returns](#returns-1)

## ReactTemplate

The `ReactTemplate` class is a subclass of [[form#^b3aad2|ActionForm]] and provides functionality for reasoning and preparing actions based on a given sentence using a language model and specified [[tool]].

### Attributes

- `template_name` (str): The name of the react template (default: "default_react").
- `sentence` (str | list | dict | None): The given sentence(s) to reason and take actions on.

### Methods

#### `__init__`

```python
def __init__(self, sentence=None, instruction=None, confidence_score=False, **kwargs)
```

Initializes a new instance of the `ReactTemplate` class.

**Parameters:**
- `sentence` (Optional[str | list | dict]): The given sentence(s) to reason and take actions on.
- `instruction` (Optional[str]): The instruction for reasoning and preparing actions.
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `**kwargs`: Additional keyword arguments.

## _react

```python
async def _react(sentence=None, *, instruction=None, branch=None, confidence_score=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, return_branch=False, **kwargs)
```

Performs reasoning and prepares actions based on a given sentence using a language model and specified tools.

### Parameters

- `sentence` (Optional[str | list | dict]): The given sentence(s) to reason and take actions on.
- `instruction` (Optional[str]): The instruction for reasoning and preparing actions.
- `branch` (Optional[Branch]): The branch to use for reasoning and action preparation. If not provided, a new branch will be created.
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for reasoning and action preparation.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for reasoning and action preparation.
- `sender` (Optional[str]): The sender of the request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for reasoning and action preparation.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `return_branch` (bool): Whether to return the branch along with the react template (default: False).
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `Tuple[ReactTemplate, Branch] | ReactTemplate`: The react template and optionally the branch if `return_branch` is True.

## react

```python
async def react(sentence=None, *, instruction=None, num_instances=1, branch=None, confidence_score=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, return_branch=False, **kwargs)
```

Performs reasoning and prepares actions based on a given sentence using a language model and specified tools, with the option to process multiple instances.

### Parameters

- `sentence` (Optional[str | list | dict]): The given sentence(s) to reason and take actions on.
- `instruction` (Optional[str]): The instruction for reasoning and preparing actions.
- `num_instances` (int): The number of instances to process (default: 1).
- `branch` (Optional[Branch]): The branch to use for reasoning and action preparation. If not provided, a new branch will be created.
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for reasoning and action preparation.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for reasoning and action preparation.
- `sender` (Optional[str]): The sender of the request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for reasoning and action preparation.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `return_branch` (bool): Whether to return the branch along with the react template (default: False).
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `Tuple[ReactTemplate, Branch] | ReactTemplate | List[Tuple[ReactTemplate, Branch]] | List[ReactTemplate]`: The react template(s) and optionally the branch(es) if `return_branch` is True, depending on the number of instances.
