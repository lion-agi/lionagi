
### Class: `OpenRouterService`

**Description**:
The `OpenRouterService` class provides an interface to interact with the OpenRouter API endpoints. It supports chat completions and is designed to be easily extendable for additional endpoints.

**Attributes**:
- `base_url` (str): The base URL for the OpenRouter API.
- `available_endpoints` (list): A list of available API endpoints.
- `schema` (dict): The schema configuration for the API.
- `key_scheme` (str): The environment variable name for the OpenRouter API key.
- `token_encoding_name` (str): The default token encoding scheme.

**Example Usage**:
```python
# Example 1: Using chat completions endpoint
service = OpenRouterService(api_key="your_api_key")
asyncio.run(service.serve("Hello, world!", "chat/completions"))

# Example 2: Handling unsupported endpoint
service = OpenRouterService()
try:
    asyncio.run(service.serve("Convert this text to speech.", "audio_speech"))
except ValueError as e:
    print(e)  # Output: 'audio_speech' is currently not supported
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
- `api_key` (str, optional): The API key for OpenRouter.
- `key_scheme` (str, optional): The environment variable name for the API key.
- `schema` (dict, optional): The schema configuration for the API.
- `token_encoding_name` (str, optional): The token encoding scheme. Defaults to "cl100k_base".
- `**kwargs`: Additional keyword arguments.

**Description**:
Initializes a new instance of the `OpenRouterService` class.

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
service = OpenRouterService(api_key="your_api_key")
asyncio.run(service.serve("Hello, world!", "chat/completions"))
```

### Method: `serve_chat`

**Signature**:
```python
async def serve_chat(self, messages, **kwargs)
```

**Parameters**:
- `messages`: The messages to be included in the chat completion.
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
service = OpenRouterService(api_key="your_api_key")
asyncio.run(service.serve_chat(messages))
```
