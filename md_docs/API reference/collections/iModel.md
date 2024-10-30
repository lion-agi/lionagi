
## Class: `iModel`

^86de48

**Description**:
`iModel` is a class for managing AI model configurations and service integrations. It handles initialization, configuration, and interaction with the service provider.

Attributes:
- `ln_id` (str): A unique identifier for the model instance.
- `timestamp` (str): The timestamp when the model instance is created.
- `endpoint` (str): The API endpoint for the model service.
- `provider_schema` (dict): The schema for the service provider.
- `provider` ([[LLM Service#^0916ce|BaseService]] | str): The service provider instance.
- `endpoint_schema` (dict): The schema for the endpoint configuration.
- `api_key` (str): The API key for the service provider.
- `status_tracker` ([[LLM Service#^deb0a1|StatusTracker]]): Instance of StatusTracker to track service status.
- `service` (BaseService): Configured service instance.
- `config` (dict): Configuration dictionary for the model.
- `iModel_name` (str): Name of the model.

### `__init__`

**Signature**:
```python
def __init__(
    self,
    model: str = None,
    config: dict = None,
    provider: str = None,
    provider_schema: dict = None,
    endpoint: str = "chat/completions",
    token_encoding_name: str = None,
    api_key: str = None,
    api_key_schema: str = None,
    interval_tokens: int = None,
    interval_requests: int = None,
    interval: int = None,
    service: BaseService = None,
    **kwargs
)
```

**Parameters**:
- `model` (str, optional): Name of the model.
- `config` (dict, optional): Configuration dictionary.
- `provider` (str, optional): Name or class of the provider.
- `provider_schema` (dict, optional): Schema dictionary for the provider.
- `endpoint` (str, optional): Endpoint string, default is "chat/completions".
- `token_encoding_name` (str, optional): Name of the token encoding, default is "cl100k_base".
- `api_key` (str, optional): API key for the provider.
- `api_key_schema` (str, optional): Schema for the API key.
- `interval_tokens` (int, optional): Token interval limit, default is 100,000.
- `interval_requests` (int, optional): Request interval limit, default is 1,000.
- `interval` (int, optional): Time interval in seconds, default is 60.
- `service` ([[LLM Service#^0916ce|BaseService]], optional): An instance of BaseService.
- `**kwargs`: Additional parameters for the model.

**Usage Examples**:
```python
# Example: Initialize an iModel instance
imodel_instance = iModel(
    model="gpt-4",
    config={"temperature": 0.7},
    provider="openai",
    api_key="your_api_key_here"
)
```

### `update_config`

**Signature**:
```python
def update_config(self, **kwargs)
```

**Parameters**:
- `**kwargs`: Additional parameters to update the configuration.

**Return Values**:
- `None`

**Description**:
Updates the configuration with additional parameters.

**Usage Examples**:
```python
# Example: Update the model configuration
imodel_instance.update_config(temperature=0.6, max_tokens=200)
```

### `call_chat_completion`

**Signature**:
```python
async def call_chat_completion(self, messages, **kwargs) -> dict
```

**Parameters**:
- `messages` (list): List of messages for the chat completion.
- `**kwargs`: Additional parameters for the service call.

**Return Values**:
- `dict`: Response from the chat completion service.

**Exceptions Raised**:
- [[Exceptions#^f38868|ModelLimitExceededError]]: If the number of tokens exceeds the limit.

**Description**:
Asynchronous method to call the chat completion service.

**Usage Examples**:
```python
# Example: Call chat completion service
response = await imodel_instance.call_chat_completion(messages)
```

### `call_embedding`

**Signature**:
```python
async def call_embedding(self, embed_str, **kwargs) -> dict
```

**Parameters**:
- `embed_str` (str): The string to be embedded.
- `**kwargs`: Additional parameters for the service call.

**Return Values**:
- `dict`: Response from the embedding service.

**Description**:
Asynchronous method to call the embedding service.

**Usage Examples**:
```python
# Example: Call embedding service
response = await imodel_instance.call_embedding(embed_str="text to embed")
```

### `embed_node`

**Signature**:
```python
async def embed_node(self, node, field="content", **kwargs) -> bool
```

**Parameters**:
- `node` ([[Component#^ce462d|Component]]): The node to embed.
- `field` (str, optional): The field to embed. Defaults to "content".
- `**kwargs`: Additional parameters for the embedding.

**Return Values**:
- `bool`: True if embedding was successful, False otherwise.

**Exceptions Raised**:
- `ValueError`: If the node is not a valid LionAGI item.
- [[Exceptions#^f38868|ModelLimitExceededError]]: If the number of tokens exceeds the limit.

**Description**:
Asynchronously embeds the specified field of the node.

**Usage Examples**:
```python
# Example: Embed a node
success = await imodel_instance.embed_node(node_instance, field="content")
print("Embedding successful:", success)
```

### `to_dict`

**Signature**:
```python
def to_dict() -> dict
```

**Return Values**:
- `dict`: Dictionary representation of the model instance.

**Description**:
Converts the model instance to a dictionary representation.

**Usage Examples**:
```python
# Example: Convert model instance to a dictionary
model_dict = imodel_instance.to_dict()
print(model_dict)
```
