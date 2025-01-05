# lionagi.service.endpoints

"""
API endpoint configuration and request handling.

This module provides:
- Base endpoint configuration
- Provider-specific endpoint handling
- Request tracking and execution

Example:
    >>> from lionagi.service.endpoints import EndPoint, EndpointConfig
    >>> config = EndpointConfig(
    ...     provider="openai",
    ...     endpoint="chat/completions",
    ...     method="post"
    ... )
    >>> endpoint = EndPoint(config)
"""

## EndpointConfig

Configuration schema for API endpoints.

```python
class EndpointConfig(BaseModel):
    """Schema for endpoint configuration.
    
    Example:
        >>> config = EndpointConfig(
        ...     provider="openai",
        ...     endpoint="chat/completions",
        ...     method="post",
        ...     requires_tokens=True
        ... )
    """
```

### Attributes

#### provider
Provider name.

Type:
- str

#### endpoint
Endpoint path/identifier.

Type:
- str

#### method
HTTP method.

Type:
- str

#### requires_tokens
Whether endpoint requires token counting.

Type:
- bool

#### is_streamable
Whether endpoint supports streaming.

Type:
- bool

## EndPoint

Base class for API endpoints.

```python
class EndPoint(ABC):
    """Base class for provider endpoints.
    
    Example:
        >>> class OpenAIEndpoint(EndPoint):
        ...     async def _invoke(self, payload, headers):
        ...         # Provider-specific implementation
        ...         pass
    """
```

### Constructor

#### __init__(config)
Initialize endpoint configuration.

Parameters:
- **config** (*dict*) - Endpoint configuration

Example:
```python
>>> endpoint = EndPoint({
...     "provider": "openai",
...     "endpoint": "chat/completions",
...     "method": "post"
... })
```

### Properties

#### is_streamable
Whether endpoint supports streaming.

Type:
- bool

#### requires_tokens
Whether token calculation is needed.

Type:
- bool

#### full_url
Complete endpoint URL with parameters.

Type:
- str

### Methods

#### create_payload(**kwargs)
Generate request payload and headers.

Parameters:
- **kwargs** (*dict*) - Request parameters

Returns:
- dict - Request configuration

Example:
```python
>>> payload = endpoint.create_payload(
...     messages=[{"role": "user", "content": "Hello"}],
...     model="gpt-4"
... )
```

#### async invoke(payload, headers, is_cached=False, **kwargs)
Execute endpoint request.

Parameters:
- **payload** (*dict*) - Request payload
- **headers** (*dict*) - HTTP headers
- **is_cached** (*bool*) - Use caching
- **kwargs** (*dict*) - Additional options

Returns:
- Response data

Example:
```python
>>> response = await endpoint.invoke(payload, headers)
```

## ChatCompletionEndPoint

Chat completion endpoint implementation.

```python
class ChatCompletionEndPoint(EndPoint):
    """Chat completion endpoint using litellm.
    
    Example:
        >>> endpoint = ChatCompletionEndPoint({
        ...     "provider": "openai",
        ...     "endpoint": "chat/completions"
        ... })
    """
```

### Methods

#### async _invoke(payload, headers, **kwargs)
Execute chat completion.

Parameters:
- **payload** (*dict*) - Request parameters
- **headers** (*dict*) - HTTP headers
- **kwargs** (*dict*) - Additional options

Returns:
- Chat completion response

Example:
```python
>>> response = await endpoint._invoke(
...     payload={
...         "messages": [{"role": "user", "content": "Hello"}],
...         "model": "gpt-4"
...     },
...     headers={"Authorization": "Bearer sk-..."}
... )
```

#### async _stream(payload, headers, **kwargs)
Execute streaming chat completion.

Parameters:
- **payload** (*dict*) - Request parameters
- **headers** (*dict*) - HTTP headers
- **kwargs** (*dict*) - Additional options

Returns:
- AsyncGenerator yielding completion chunks

Example:
```python
>>> async for chunk in endpoint._stream(
...     payload={
...         "messages": [{"role": "user", "content": "Hello"}],
...         "model": "gpt-4",
...         "stream": True
...     },
...     headers={"Authorization": "Bearer sk-..."}
... ):
...     process_chunk(chunk)
```

## Error Handling

```python
# Handle request error
try:
    response = await endpoint.invoke(payload, headers)
except RequestError as e:
    print(f"Request failed: {e}")

# Handle validation error
try:
    config = EndpointConfig(provider="invalid")
except ValueError as e:
    print(f"Invalid config: {e}")

# Handle token limit
try:
    if endpoint.requires_tokens:
        tokens = endpoint.calculate_tokens(payload)
        if tokens > max_tokens:
            raise ValueError(f"Token limit exceeded: {tokens}")
except ValueError as e:
    print(f"Token error: {e}")
```
