# score

This API reference provides documentation for the `ScoreTemplate` class and related functions for scoring a given context using a language model.

## Table of Contents

1. [ScoreTemplate](#scoretemplate)
   - [Attributes](#attributes)
   - [Methods](#methods)
     - [`__init__`](#__init__)
2. [_score](#_score)
   - [Parameters](#parameters)
   - [Returns](#returns)
3. [score](#score)
   - [Parameters](#parameters-1)
   - [Returns](#returns-1)

## ScoreTemplate

The `ScoreTemplate` class is a subclass of [[form#^ffad5b|ScoreForm]] and provides functionality for scoring a given context based on specified instructions, score range, and other parameters. It includes fields for the input sentence, score range, inclusive flag, number of digits, confidence score, and reason for the score.

### Attributes

- `template_name` (str): The name of the score template (default: "default_score").
- `sentence` (str | list | dict): The given context to score.
- `answer` (float): The numeric score for the context.
- `signature` (str): The signature indicating the input and output fields (default: "sentence -> answer").

### Methods

#### `__init__`

```python
def __init__(self, sentence=None, instruction=None, score_range=(1, 10), inclusive=True, num_digit=0, confidence_score=False, reason=False, **kwargs)
```

Initializes a new instance of the `ScoreTemplate` class.

**Parameters:**
- `sentence` (Optional[str | list | dict]): The given context to score.
- `instruction` (Optional[str]): The instruction for scoring the context.
- `score_range` (tuple): The range of valid scores (default: (1, 10)).
- `inclusive` (bool): Whether to include the endpoints of the score range (default: True).
- `num_digit` (int): The number of digits after the decimal point for the score (default: 0).
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for the score in the output (default: False).
- `**kwargs`: Additional keyword arguments.

## _score

```python
async def _score(sentence, instruction=None, score_range=(1, 10), inclusive=True, num_digit=0, confidence_score=False, reason=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, **kwargs)
```

Scores a given context using a language model.

### Parameters

- `sentence` (str | list | dict): The given context to score.
- `instruction` (Optional[str]): The instruction for scoring the context.
- `score_range` (tuple): The range of valid scores (default: (1, 10)).
- `inclusive` (bool): Whether to include the endpoints of the score range (default: True).
- `num_digit` (int): The number of digits after the decimal point for the score (default: 0).
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for the score in the output (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for scoring.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for scoring.
- `sender` (Optional[str]): The sender of the scoring request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for scoring.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `ScoreTemplate`: The score template with the scored context.

## score

```python
async def score(sentence, *, num_instances=1, instruction=None, score_range=(1, 10), inclusive=True, num_digit=0, confidence_score=False, reason=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, return_template=True, **kwargs) -> ScoreTemplate | float
```

Scores a given context using a language model, with the option to score multiple instances.

### Parameters

- `sentence` (str | list | dict): The given context to score.
- `num_instances` (int): The number of instances to score (default: 1).
- `instruction` (Optional[str]): The instruction for scoring the context.
- `score_range` (tuple): The range of valid scores (default: (1, 10)).
- `inclusive` (bool): Whether to include the endpoints of the score range (default: True).
- `num_digit` (int): The number of digits after the decimal point for the score (default: 0).
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for the score in the output (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for scoring.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for scoring.
- `sender` (Optional[str]): The sender of the scoring request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for scoring.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `return_template` (bool): Whether to return the score template or only the score (default: True).
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `ScoreTemplate | float`: The score template with the scored context or the average score if `return_template` is False.
