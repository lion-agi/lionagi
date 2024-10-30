
### Class: `Services`

**Description**:
The `Services` class provides static methods to initialize various service providers for interacting with different API endpoints. Each provider is responsible for specific tasks such as interacting with OpenAI, OpenRouter, Hugging Face Transformers, Ollama, LiteLLM, and MLX.

### Method: `OpenAI`

**Signature**:
```python
def OpenAI(**kwargs)
```

**Parameters**:
- `**kwargs` (dict): Additional keyword arguments to be passed to the `OpenAIService` constructor.

**Returns**:
- `OpenAIService`: An instance of the `OpenAIService` class.

**Description**:
Initializes and returns an instance of the `OpenAIService` class, which provides methods to interact with OpenAI's API endpoints.

**Usage Example**:
```python
service = Services.OpenAI(api_key="your_api_key")
asyncio.run(service.serve("Hello, world!", "chat/completions"))
```

### Method: `OpenRouter`

**Signature**:
```python
def OpenRouter(**kwargs)
```

**Parameters**:
- `**kwargs` (dict): Additional keyword arguments to be passed to the `OpenRouterService` constructor.

**Returns**:
- `OpenRouterService`: An instance of the `OpenRouterService` class.

**Description**:
Initializes and returns an instance of the `OpenRouterService` class, which provides methods to interact with OpenRouter's API endpoints.

**Usage Example**:
```python
service = Services.OpenRouter(api_key="your_api_key")
asyncio.run(service.serve("Hello, world!", "chat/completions"))
```

### Method: `Transformers`

**Signature**:
```python
def Transformers(**kwargs)
```

**Parameters**:
- `**kwargs` (dict): Additional keyword arguments to be passed to the `TransformersService` constructor.

**Returns**:
- `TransformersService`: An instance of the `TransformersService` class.

**Description**:
Initializes and returns an instance of the `TransformersService` class, which provides methods to interact with Hugging Face's Transformers library for various NLP tasks.

**Usage Example**:
```python
service = Services.Transformers(task="conversational", model="gpt-2")
asyncio.run(service.serve_chat("Hello, world!"))
```

### Method: `Ollama`

**Signature**:
```python
def Ollama(**kwargs)
```

**Parameters**:
- `**kwargs` (dict): Additional keyword arguments to be passed to the `OllamaService` constructor.

**Returns**:
- `OllamaService`: An instance of the `OllamaService` class.

**Description**:
Initializes and returns an instance of the `OllamaService` class, which provides methods to interact with Ollama's API endpoints.

**Usage Example**:
```python
service = Services.Ollama(model="your_model")
asyncio.run(service.serve_chat("Hello, world!"))
```

### Method: `LiteLLM`

**Signature**:
```python
def LiteLLM(**kwargs)
```

**Parameters**:
- `**kwargs` (dict): Additional keyword arguments to be passed to the `LiteLLMService` constructor.

**Returns**:
- `LiteLLMService`: An instance of the `LiteLLMService` class.

**Description**:
Initializes and returns an instance of the `LiteLLMService` class, which provides methods to interact with LiteLLM's API endpoints.

**Usage Example**:
```python
service = Services.LiteLLM(model="your_model")
asyncio.run(service.serve_chat("Hello, world!"))
```

### Method: `MLX`

**Signature**:
```python
def MLX(**kwargs)
```

**Parameters**:
- `**kwargs` (dict): Additional keyword arguments to be passed to the `MLXService` constructor.

**Returns**:
- `MLXService`: An instance of the `MLXService` class.

**Description**:
Initializes and returns an instance of the `MLXService` class, which provides methods to interact with MLX's API endpoints.

**Usage Example**:
```python
service = Services.MLX(model="your_model")
asyncio.run(service.serve_chat("Hello, world!"))
```

### Attributes for Each Service

**Attributes**:
- `api_key` (Optional[str]): The API key used for authentication.
- `schema` (Dict[str, Any]): The schema defining the provider's endpoints.
- `status_tracker` (StatusTracker): The object tracking the status of API calls.
- `endpoints` (Dict[str, EndPoint]): A dictionary of endpoint objects.
- `base_url` (str): The base URL for the API.
- `available_endpoints` (list): A list of available API endpoints, including 'chat/completions'.
- `key_scheme` (str): The environment variable name for API key.
- `token_encoding_name` (str): The default token encoding scheme.

**Warnings**:
- Ensure the selected model is suitable for the specified tasks to avoid unexpected behavior.
- As some providers heavily rely on external libraries (e.g., Hugging Face's Transformers), ensure they are installed and updated to compatible versions.

**Dependencies**:
- Requires the respective library (e.g., `transformers`, `ollama`, `litellm`, `mlx_lm`) for the chosen provider.
- Requires `asyncio` for asynchronous operations.
