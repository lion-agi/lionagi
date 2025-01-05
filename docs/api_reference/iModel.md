# LionAGI Service Model API Reference

## Overview

The iModel class provides a unified interface for managing API calls to various LLM providers. It integrates with EndPoint for provider-specific handling and uses RateLimitedAPIExecutor for request management. The class handles:

1. Provider-specific endpoint configuration via match_endpoint
2. API key management and environment variable resolution
3. Request queuing and rate limiting through RateLimitedAPIProcessor
4. Streaming and non-streaming API calls via ChatCompletionEndPoint

## Core Concepts

1. **Provider Management**
   - Environment-based API key resolution (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY)
   - Provider detection from model names (e.g., "openai/gpt-4" -> provider="openai")
   - Custom base URLs for self-hosted or proxy endpoints
   - Dynamic endpoint matching via match_endpoint

2. **Request Processing**
   - APICalling event generation and tracking
   - Payload construction with provider-specific formatting
   - Streaming support with chunk processing
   - Response caching via litellm

3. **Rate Limiting**
   - Queue-based request management through RateLimitedAPIExecutor
   - Token counting via TokenCalculator
   - Configurable request and token limits
   - Automatic capacity refresh cycles

## API Documentation

### iModel Class

```python
class iModel:
    """
    Manages provider-specific API calls with rate limiting.
    
    Key components:
    - endpoint: Provider-specific EndPoint instance
    - executor: RateLimitedAPIExecutor for request management
    - kwargs: Provider configuration (model, temperature, etc.)
    """
```

#### Constructor

```python
def __init__(
    self,
    provider: str = None,
    base_url: str = None,
    endpoint: str | EndPoint = "chat",
    endpoint_params: list[str] | None = None,
    api_key: str = None,
    queue_capacity: int = 100,
    capacity_refresh_time: float = 60,
    interval: float | None = None,
    limit_requests: int = None,
    limit_tokens: int = None,
    invoke_with_endpoint: bool = True,
    **kwargs,
) -> None
```

Creates a new iModel instance with specified configuration.

Parameters:
- `provider`: Name of the LLM provider (e.g., 'openai', 'anthropic')
- `base_url`: Optional custom API endpoint URL
- `endpoint`: Endpoint type or EndPoint instance
- `endpoint_params`: Additional endpoint configuration parameters
- `api_key`: Explicit API key or environment variable name
- `queue_capacity`: Maximum queued requests
- `capacity_refresh_time`: Queue refresh interval in seconds
- `interval`: Request processing interval
- `limit_requests`: Maximum requests per cycle
- `limit_tokens`: Maximum tokens per cycle
- `invoke_with_endpoint`: Enable/disable actual API calls
- `**kwargs`: Additional provider-specific parameters

#### Core Methods

```python
async def invoke(self, **kwargs) -> APICalling | None:
    """Invokes a rate-limited API call with the given arguments."""
```

Executes a rate-limited API call and returns the result.

Parameters:
- `**kwargs`: Request parameters merged with instance configuration

Returns:
- `APICalling | None`: Completed API call object or None on failure

```python
async def stream(self, **kwargs) -> APICalling | None:
    """Performs a streaming API call with the given arguments."""
```

Executes a streaming API call with chunk processing.

Parameters:
- `**kwargs`: Request parameters merged with instance configuration

Returns:
- `APICalling | None`: Streaming API call object or None on failure

```python
def create_api_calling(self, **kwargs) -> APICalling:
    """Constructs an APICalling object from endpoint-specific payload."""
```

Creates an APICalling instance with proper configuration.

Parameters:
- `**kwargs`: Parameters for payload generation

Returns:
- `APICalling`: Configured API call object

#### Properties

```python
@property
def allowed_roles(self) -> set[str]:
    """Roles that are permissible for this endpoint."""
```

Returns the set of allowed message roles for the endpoint.

```python
@property
def sequential_exchange(self) -> bool:
    """Indicates whether requests must occur in a strict sequence."""
```

Returns True if messages must be processed sequentially.

#### Serialization Methods

```python
def to_dict(self) -> dict:
    """Converts the iModel instance to a dictionary representation."""
```

```python
@classmethod
def from_dict(cls, data: dict) -> 'iModel':
    """Creates an iModel instance from a dictionary configuration."""
```

## Implementation Notes

1. **Provider Resolution**
   ```python
   # From model name
   if "/" in model:  # e.g., "openai/gpt-4"
       provider = model.split("/")[0]
       model = model.replace(provider + "/", "")
   ```

2. **API Key Resolution**
   ```python
   # Environment variable mapping
   KEY_MAP = {
       "openai": "OPENAI_API_KEY",
       "anthropic": "ANTHROPIC_API_KEY",
       "perplexity": "PERPLEXITY_API_KEY",
       "groq": "GROQ_API_KEY",
       "openrouter": "OPENROUTER_API_KEY"
   }
   api_key = os.getenv(KEY_MAP.get(provider))
   ```

3. **Endpoint Configuration**
   ```python
   # Custom endpoint setup
   endpoint = match_endpoint(
       provider=provider,
       base_url=base_url,
       endpoint="chat",
       endpoint_params=["v1"]
   )
   endpoint.update_config(openai_compatible=True)
   ```

4. **Rate Limiting Setup**
   ```python
   # Configure executor
   executor = RateLimitedAPIExecutor(
       queue_capacity=queue_capacity,
       capacity_refresh_time=capacity_refresh_time,
       interval=interval,
       limit_requests=limit_requests,
       limit_tokens=limit_tokens
   )
   await executor.start()
   ```

## System Integration

### Usage Examples

1. **Basic Chat Completion**
```python
# Initialize model
model = iModel(
    provider="openai",
    model="gpt-4",
    temperature=0.7,
    queue_capacity=50
)

# Make API call
response = await model.invoke(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain async/await in Python."}
    ]
)
```

2. **Streaming with Rate Limits**
```python
model = iModel(
    provider="anthropic",
    model="claude-3-opus",
    limit_requests=10,  # Max 10 requests per interval
    limit_tokens=100000,  # Max 100k tokens per interval
    capacity_refresh_time=60  # Refresh every minute
)

async for chunk in model.stream(
    messages=[{"role": "user", "content": "Write a story..."}],
    temperature=0.9,
    max_tokens=2000
):
    print(chunk.choices[0].delta.content, end="", flush=True)
```

3. **Custom Provider Setup**
```python
# Using custom endpoint
model = iModel(
    provider="custom",
    base_url="https://api.custom-llm.com",
    endpoint="chat/completions",
    api_key="custom-key",
    model="custom-model",
    openai_compatible=True  # Uses OpenAI format
)

# Error handling
try:
    response = await model.invoke(messages=[...])
    if response and response.execution.status == EventStatus.COMPLETED:
        print(response.execution.response)
    else:
        print(f"Error: {response.execution.error}")
except Exception as e:
    print(f"Failed to invoke API: {e}")
```

## Error Handling

1. **API Errors**
   - Rate limit exceeded -> Automatic retry with backoff
   - Invalid API key -> Environment variable check
   - Model not found -> Provider/model name validation
   - Network errors -> Configurable retry logic

2. **Rate Limit Handling**
   ```python
   # Rate limit error
   if api_call.execution.status == EventStatus.FAILED:
       if "Rate limit" in api_call.execution.error:
           # Wait for capacity refresh
           await asyncio.sleep(self.executor.interval)
           return await self.invoke(**kwargs)
   ```

3. **Token Limit Protection**
   ```python
   # Check token usage before request
   required_tokens = api_call.required_tokens
   if required_tokens > self.executor.limit_tokens:
       raise ValueError(
           f"Request requires {required_tokens} tokens, "
           f"but limit is {self.executor.limit_tokens}"
       )
   ```
