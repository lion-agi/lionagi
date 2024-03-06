```
from lionagi.libs.ln_api import PayloadPackage
```

# PayloadPackage

The `PayloadPackage` class provides methods for creating payloads for different API operations.

## Methods

### `chat_completion(messages, llmconfig, schema, **kwargs)`

Creates a payload for the chat completion operation.

- `messages`: The messages to include in the chat completion.
- `llmconfig`: Configuration for the language model.
- `schema`: The schema describing required and optional fields.
- `**kwargs`: Additional keyword arguments.

Returns the constructed payload.

Examples:
```python
messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': 'How can I improve my coding skills?'}
]
llmconfig = {'model': 'gpt-3.5-turbo', 'temperature': 0.7}
schema = {
    'required': ['model', 'messages'],
    'optional': ['temperature', 'max_tokens']
}
payload = PayloadPackage.chat_completion(messages, llmconfig, schema)
```

### `fine_tuning(training_file, llmconfig, schema, **kwargs)`

Creates a payload for the fine-tuning operation.

- `training_file`: The file containing training data.
- `llmconfig`: Configuration for the language model.
- `schema`: The schema describing required and optional fields.
- `**kwargs`: Additional keyword arguments.

Returns the constructed payload.

Examples:
```python
training_file = 'path/to/training_data.jsonl'
llmconfig = {'model': 'curie', 'epochs': 3}
schema = {
    'required': ['training_file', 'model'],
    'optional': ['epochs', 'batch_size']
}
payload = PayloadPackage.fine_tuning(training_file, llmconfig, schema)
```
