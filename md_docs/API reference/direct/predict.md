# Predict

This API reference provides documentation for the `PredictTemplate` class and the `predict` function, which are used for predicting the next sentence(s) based on a given sentence using a language model.

## Table of Contents

1. [PredictTemplate](#predicttemplate)
   - [Attributes](#attributes)
   - [Methods](#methods)
     - [`__init__`](#__init__)
2. [predict](#predict)
   - [Parameters](#parameters)
   - [Returns](#returns)

## PredictTemplate

The `PredictTemplate` class is a subclass of [[form#^ffad5b|Score Form]] and provides functionality for predicting the next sentence(s) using a language model. It includes fields for the input sentence, number of sentences to predict, predicted answer, confidence score, and reason for the prediction.

### Attributes

- `template_name` (str): The name of the predict template (default: "default_predict_template").
- `sentence` (str | list | dict): The given sentence(s) to predict.
- `num_sentences` (int): The number of sentences to predict.
- `answer` (str | list): The predicted sentence(s).
- `signature` (str): The signature indicating the input and output fields (default: "sentence -> answer").

### Methods

#### `__init__`

```python
def __init__(self, sentence=None, instruction=None, num_sentences=1, confidence_score=False, reason=False, **kwargs)
```

Initializes a new instance of the `PredictTemplate` class.

**Parameters:**
- `sentence` (Optional[str | list | dict]): The given sentence(s) to predict.
- `instruction` (Optional[str]): The instruction for the prediction task.
- `num_sentences` (int): The number of sentences to predict (default: 1).
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `reason` (bool): Whether to include the reason for the prediction in the output (default: False).
- `**kwargs`: Additional keyword arguments.

## predict

```python
async def predict(sentence=None, num_sentences=1, confidence_score=False, instruction=None, branch=None, reason=False, retries=2, delay=0.5, backoff_factor=2, default_value=None, timeout=None, branch_name=None, system=None, messages=None, service=None, sender=None, llmconfig=None, tools=None, datalogger=None, persist_path=None, tool_manager=None, **kwargs) -> "PredictTemplate"
```

Predicts the next sentence(s) based on the given sentence using a language model.

### Parameters

- `sentence` (Optional[str | list | dict]): The given sentence(s) to predict.
- `num_sentences` (int): The number of sentences to predict (default: 1).
- `confidence_score` (bool): Whether to include the confidence score in the output (default: False).
- `instruction` (Optional[str]): The instruction for the prediction task.
- `branch` (Optional[Branch]): The branch to use for prediction. If not provided, a new branch will be created.
- `reason` (bool): Whether to include the reason for the prediction in the output (default: False).
- `retries` (int): The number of retries for the API call (default: 2).
- `delay` (float): The initial delay between retries in seconds (default: 0.5).
- `backoff_factor` (float): The backoff factor for exponential delay between retries (default: 2).
- `default_value` (Optional[Any]): The default value to return if the API call fails (default: None).
- `timeout` (Optional[float]): The timeout for the API call in seconds (default: None).
- `branch_name` (Optional[str]): The name of the branch to use for prediction.
- `system` (Optional[Any]): The system configuration for the branch.
- `messages` (Optional[Any]): The messages to initialize the branch with.
- `service` (Optional[Any]): The service to use for prediction.
- `sender` (Optional[str]): The sender of the prediction request.
- `llmconfig` (Optional[Any]): The configuration for the language model.
- `tools` (Optional[Any]): The tools to use for prediction.
- `datalogger` (Optional[Any]): The data logger for the branch.
- `persist_path` (Optional[str]): The path to persist the branch data.
- `tool_manager` (Optional[Any]): The tool manager for the branch.
- `**kwargs`: Additional keyword arguments for the API call.

### Returns

- `PredictTemplate`: The predict template with the predicted sentence(s).
