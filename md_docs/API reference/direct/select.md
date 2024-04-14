# select

This API reference provides documentation for the `SelectTemplate` class and related functions for selecting an item from given choices based on a given context using a language model.

## Table of Contents

1. [SelectTemplate](#selecttemplate)
   - [Attributes](#attributes)
   - [Methods](#methods)
     - [`__init__`](#__init__)
2. [select](#select)
   - [Parameters](#parameters)
   - [Returns](#returns)

## SelectTemplate

The `SelectTemplate` class is a subclass of [[form#^ffad5b|ScoreForm]] and provides functionality for selecting an item from given choices using a language model. It includes fields for the input sentence, choices, selected answer, confidence score, and reason for the selection.

### Attributes

- `template_name` (str): The name of the select template (default: "default_select").
- `sentence` (str | list | dict): The given context.
- `answer` (Enum | str): The selected item from the given choices.
- `choices` (list): The given choices.
- `signature` (str): The signature indicating the input and output fields (default: "sentence -> answer").

### Methods

#### `__init__`

```python
def __init__(self, sentence=None, choices=None, instruction=None, reason=False, confidence_score=False, **kwargs)
```

Initializes a new instance of the `SelectTemplate` class.

**Parameters:**
- `sentence` (Optional[str | list | dict]): The given context.
- `choices` (Optional[list]): The list of choices to select from. which will be validated by [[Parse Lib#^b73a5b|force correct dict]]
- `instruction` (Optional[str]): The [[messages#^69c0d6|instruction]] for selection.
- `reason` (bool): Whether to include the reason for the selection in the output (default: False).
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `**kwargs`: Additional keyword arguments.

## select

```python
async def select(sentence, choices=None, instruction=None, confidence_score=False, reason=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, **kwargs)
```

Selects an item from given choices based on a given context using a language model.

### Parameters

- `sentence` (str | list | dict): The given context.
- `choices` (Optional[list]): The list of choices to select from.
- `instruction` (Optional[str]): The instruction for selection.
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for the selection in the output (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for selection.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for selection.
- `sender` (Optional[str]): The sender of the selection request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for selection.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `SelectTemplate`: The select template with the selected item.

