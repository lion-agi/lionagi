
### Class: `OpenAIService`

**Description**:
The `OpenAIService` class provides an interface to interact with OpenAI's API endpoints. It supports various endpoints such as chat completions, fine-tuning, audio processing, and embeddings.

**Attributes**:
- `base_url` (str): The base URL for the OpenAI API.
- `available_endpoints` (list): A list of available API endpoints.
- `schema` (dict): The schema configuration for the API.
- `key_scheme` (str): The environment variable name for OpenAI API key.
- `token_encoding_name` (str): The default token encoding scheme.

**Example Usage**:
```python
# Example 1: Using chat completions endpoint
service = OpenAIService(api_key="your_api_key")
asyncio.run(service.serve("Hello, world!", "chat/completions"))

# Example 2: Using audio speech endpoint
service = OpenAIService()
asyncio.run(service.serve("Convert this text to speech.", "audio_speech"))
```

### Method: `__init__`

**Signature**:
```python
def __init__(
    self,
    api_key=None,
    key_scheme=None,
    schema=None,
    token_encoding_name: str = "cl100k_base",
    **kwargs,
)
```

**Parameters**:
- `api_key` (str, optional): The API key for OpenAI.
- `key_scheme` (str, optional): The environment variable name for the API key.
- `schema` (dict, optional): The schema configuration for the API.
- `token_encoding_name` (str, optional): The token encoding scheme. Defaults to "cl100k_base".
- `**kwargs`: Additional keyword arguments.

**Description**:
Initializes a new instance of the `OpenAIService` class.

### Method: `serve`

**Signature**:
```python
async def serve(self, input_, endpoint="chat/completions", method="post", **kwargs)
```

**Parameters**:
- `input_`: The input text to be processed.
- `endpoint` (str): The API endpoint to use for processing. Defaults to "chat/completions".
- `method` (str): The HTTP method to use for the request. Defaults to "post".
- `**kwargs`: Additional keyword arguments to pass to the payload creation.

**Returns**:
- `tuple`: A tuple containing the payload and the completion response from the API.

**Raises**:
- `ValueError`: If the specified endpoint is not supported.

**Description**:
Serves the input using the specified endpoint and method.

**Example Usage**:
```python
service = OpenAIService(api_key="your_api_key")
asyncio.run(service.serve("Hello, world!", "chat/completions"))
```

### Method: `serve_chat`

**Signature**:
```python
async def serve_chat(self, messages, required_tokens=None, **kwargs)
```

**Parameters**:
- `messages`: The messages to be included in the chat completion.
- `required_tokens` (optional): The required tokens for the request.
- `**kwargs`: Additional keyword arguments for payload creation.

**Returns**:
- `tuple`: A tuple containing the payload and the completion response from the API.

**Raises**:
- `Exception`: If the API call fails.

**Description**:
Serves the chat completion request with the given messages.

**Example Usage**:
```python
messages = [{"role": "user", "content": "Hello, world!"}]
service = OpenAIService(api_key="your_api_key")
asyncio.run(service.serve_chat(messages))
```

### Method: `serve_embedding`

**Signature**:
```python
async def serve_embedding(self, embed_str, required_tokens=None, **kwargs)
```

**Parameters**:
- `embed_str`: The string to be embedded.
- `required_tokens` (optional): The required tokens for the request.
- `**kwargs`: Additional keyword arguments for payload creation.

**Returns**:
- `tuple`: A tuple containing the payload and the embedding response from the API.

**Raises**:
- `Exception`: If the API call fails.

**Description**:
Serves the embedding request with the given string.

**Example Usage**:
```python
embed_str = "This is a test string for embedding."
service = OpenAIService(api_key="your_api_key")
asyncio.run(service.serve_embedding(embed_str))
```
