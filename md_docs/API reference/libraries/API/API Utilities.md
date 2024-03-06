
```
from lionagi.libs.ln_api import APIUtil
```
# APIUtil

The `APIUtil` class is a utility class that provides various helper methods for working with APIs. It offers functionality for handling API requests, error checking, rate limiting, and more.

## Methods

### `api_method(http_session: aiohttp.ClientSession, method: str = "post") -> Callable`

Returns the corresponding HTTP method function from the `http_session` object.

- `http_session`: The session object from the `aiohttp` library.
- `method`: The HTTP method as a string (default is "post"). Allowed values are "post", "delete", "head", "options", and "patch".

Returns the `Callable` for the specified HTTP method.

Raises a `ValueError` if the provided `method` is not one of the allowed values.

Examples:
```python
session = aiohttp.ClientSession()
post_method = APIUtil.api_method(session, "post")
print(post_method)
# Output: <bound method ClientSession._request of <aiohttp.client.ClientSession object at 0x...>>

delete_method = APIUtil.api_method(session, "delete")
print(delete_method)
# Output: <bound method ClientSession._request of <aiohttp.client.ClientSession object at 0x...>>

invalid_method = APIUtil.api_method(session, "get")
# Raises ValueError: Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']
```

### `api_error(response_json: Mapping[str, Any]) -> bool`

Checks if the given `response_json` dictionary contains an "error" key.

- `response_json`: The JSON response as a dictionary.

Returns `True` if there is an error, `False` otherwise.

Examples:
```python
response_json_with_error = {"error": "Something went wrong"}
has_error = APIUtil.api_error(response_json_with_error)
print(has_error)
# Output: True

response_json_without_error = {"result": "Success"}
has_error = APIUtil.api_error(response_json_without_error)
print(has_error)
# Output: False

response_json_with_nested_error = {"data": {"error": "Nested error"}}
has_error = APIUtil.api_error(response_json_with_nested_error)
print(has_error)
# Output: True
```

### `api_rate_limit_error(response_json: Mapping[str, Any]) -> bool`

Checks if the error message in the `response_json` dictionary contains the phrase "Rate limit".

- `response_json`: The JSON response as a dictionary.

Returns `True` if the phrase "Rate limit" is found, `False` otherwise.

Examples:
```python
response_json_with_rate_limit = {"error": {"message": "Rate limit exceeded"}}
is_rate_limited = APIUtil.api_rate_limit_error(response_json_with_rate_limit)
print(is_rate_limited)
# Output: True

response_json_without_rate_limit = {"error": {"message": "Another error"}}
is_rate_limited = APIUtil.api_rate_limit_error(response_json_without_rate_limit)
print(is_rate_limited)
# Output: False

response_json_with_different_error = {"error": {"message": "Something went wrong"}}
is_rate_limited = APIUtil.api_rate_limit_error(response_json_with_different_error)
print(is_rate_limited)
# Output: False
```

### `api_endpoint_from_url(request_url: str) -> str`

Extracts the API endpoint from a given URL using a regular expression.

- `request_url`: The full URL to the API endpoint.

Returns the extracted endpoint or an empty string if the pattern does not match.

Examples:
```python
valid_url = "https://api.example.com/v1/users"
endpoint = APIUtil.api_endpoint_from_url(valid_url)
print(endpoint)
# Output: 'users'

invalid_url = "https://api.example.com/users"
endpoint = APIUtil.api_endpoint_from_url(invalid_url)
print(endpoint)
# Output: ''

another_valid_url = "https://api.example.com/v2/products/123"
endpoint = APIUtil.api_endpoint_from_url(another_valid_url)
print(endpoint)
# Output: 'products/123'
```

### `unified_api_call(http_session: aiohttp.ClientSession, method: str, url: str, **kwargs) -> Any`

Makes an API call and automatically retries on rate limit error.

- `http_session`: The session object from the `aiohttp` library.
- `method`: The HTTP method as a string.
- `url`: The URL to which the request is made.
- `**kwargs`: Additional keyword arguments to pass to the API call.

Returns the JSON response as a dictionary.

Examples:
```python
session = aiohttp.ClientSession()
success_url = "https://api.example.com/v1/success"
response = await APIUtil.unified_api_call(session, 'get', success_url)
print(response)
# Output: {'result': 'Success'}

rate_limit_url = "https://api.example.com/v1/rate_limit"
response = await APIUtil.unified_api_call(session, 'get', rate_limit_url)
print(response)
# Output: {'error': {'message': 'Rate limit exceeded'}}

url_with_params = "https://api.example.com/v1/data"
params = {"page": 1, "limit": 10}
response = await APIUtil.unified_api_call(session, 'get', url_with_params, params=params)
print(response)
# Output: {'data': [...]}
```

### `get_cache_key(url: str, params: Mapping[str, Any] | None) -> str`

Creates a unique cache key based on the URL and parameters.

- `url`: The URL of the request.
- `params`: The parameters of the request as a dictionary.

Returns the cache key as a string.

Examples:
```python
url = "https://api.example.com/v1/data"
params = {"page": 1, "limit": 10}
cache_key = APIUtil.get_cache_key(url, params)
print(cache_key)
# Output: 'a1b2c3d4e5f6g7h8i9j0'

url_without_params = "https://api.example.com/v1/users"
cache_key = APIUtil.get_cache_key(url_without_params, None)
print(cache_key)
# Output: 'k1l2m3n4o5p6q7r8s9t0'

url_with_different_params = "https://api.example.com/v1/products"
different_params = {"category": "electronics", "sort": "price"}
cache_key = APIUtil.get_cache_key(url_with_different_params, different_params)
print(cache_key)
# Output: 'u1v2w3x4y5z6a7b8c9d0'
```

### `retry_api_call(http_session: aiohttp.ClientSession, url: str, retries: int = 3, backoff_factor: float = 0.5, **kwargs) -> Any`

Retries an API call on failure, with exponential backoff.

- `http_session`: The `aiohttp` client session.
- `url`: The URL to make the API call.
- `retries`: The number of times to retry (default is 3).
- `backoff_factor`: The backoff factor for retries (default is 0.5).
- `**kwargs`: Additional arguments for the API call.

Returns the response from the API call, if successful; otherwise, returns `None`.

Examples:
```python
session = aiohttp.ClientSession()
url = "https://api.example.com/v1/data"
response = await APIUtil.retry_api_call(session, url)
print(response)
# Output: {'data': [...]}

url_with_params = "https://api.example.com/v1/products"
params = {"category": "electronics"}
response = await APIUtil.retry_api_call(session, url_with_params, params=params)
print(response)
# Output: {'products': [...]}

url_with_failure = "https://api.example.com/v1/failure"
response = await APIUtil.retry_api_call(session, url_with_failure, retries=5, backoff_factor=1.0)
print(response)
# Output: None
```

### `upload_file_with_retry(http_session: aiohttp.ClientSession, url: str, file_path: str, param_name: str = "file", additional_data: Mapping[str, Any] = None, retries: int = 3) -> Any`

Uploads a file to a specified URL with a retry mechanism for handling failures.

- `http_session`: The HTTP session object to use for making the request.
- `url`: The URL to which the file will be uploaded.
- `file_path`: The path to the file that will be uploaded.
- `param_name`: The name of the parameter expected by the server for the file upload (default is "file").
- `additional_data`: Additional data to be sent with the upload (default is `None`).
- `retries`: The number of times to retry the upload in case of failure (default is 3).

Returns the HTTP response object.

Examples:
```python
session = aiohttp.ClientSession()
url = "https://api.example.com/v1/upload"
file_path = "path/to/file.txt"
response = await APIUtil.upload_file_with_retry(session, url, file_path)
print(response.status)
# Output: 200

url_with_additional_data = "https://api.example.com/v1/upload"
file_path = "path/to/image.jpg"
additional_data = {"description": "An example image"}
response = await APIUtil.upload_file_with_retry(session, url_with_additional_data, file_path, additional_data=additional_data)
print(response.status)
# Output: 200

url_with_custom_param = "https://api.example.com/v1/upload"
file_path = "path/to/document.pdf"
response = await APIUtil.upload_file_with_retry(session, url_with_custom_param, file_path, param_name="document")
print(response.status)
# Output: 200
```

### `get_oauth_token_with_cache(http_session: aiohttp.ClientSession, auth_url: str, client_id: str, client_secret: str, scope: str) -> str`

Retrieves an OAuth token from the authentication server and caches it to avoid unnecessary requests.

- `http_session`: The HTTP session object to use for making the request.
- `auth_url`: The URL of the authentication server.
- `client_id`: The client ID for OAuth authentication.
- `client_secret`: The client secret for OAuth authentication.
- `scope`: The scope for which the OAuth token is requested.

Returns the OAuth token as a string.

The result is cached for 10 minutes to avoid unnecessary requests.

Examples:
```python
session = aiohttp.ClientSession()
auth_url = "https://auth.example.com/token"
client_id = "your_client_id"
client_secret = "your_client_secret"
scope = "read write"
token = await APIUtil.get_oauth_token_with_cache(session, auth_url, client_id, client_secret, scope)
print(token)
# Output: 'your_oauth_token'

auth_url_with_different_scope = "https://auth.example.com/token"
scope = "read"
token = await APIUtil.get_oauth_token_with_cache(session, auth_url_with_different_scope, client_id, client_secret, scope)
print(token)
# Output: 'your_oauth_token_with_read_scope'

auth_url_with_invalid_credentials = "https://auth.example.com/token"
invalid_client_id = "invalid_client_id"
invalid_client_secret = "invalid_client_secret"
token = await APIUtil.get_oauth_token_with_cache(session, auth_url_with_invalid_credentials, invalid_client_id, invalid_client_secret, scope)
# Raises aiohttp.ClientResponseError
```

### `cached_api_call(http_session: aiohttp.ClientSession, url: str, **kwargs) -> Any`

Makes an API call and caches the result for 10 minutes.

- `http_session`: The `aiohttp` client session.
- `url`: The URL for the API call.
- `**kwargs`: Additional arguments for the API call.

Returns the response from the API call, if successful; otherwise, returns `None`.

Examples:
```python
session = aiohttp.ClientSession()
url = "https://api.example.com/v1/data"
response = await APIUtil.cached_api_call(session, url)
print(response)
# Output: {'data': [...]}

url_with_params = "https://api.example.com/v1/products"
params = {"category": "electronics"}
response = await APIUtil.cached_api_call(session, url_with_params, params=params)
print(response)
# Output: {'products': [...]}

url_with_failure = "https://api.example.com/v1/failure"
response = await APIUtil.cached_api_call(session, url_with_failure)
print(response)
# Output: None
```

### `calculate_num_token(payload: Mapping[str, Any] = None, api_endpoint: str = None, token_encoding_name: str = None) -> int`

Calculates the number of tokens required for a request based on the payload and API endpoint. This method should be implemented in a subclass to provide the specific calculation logic for the OpenAI API.

- `payload`: The payload of the request.
- `api_endpoint`: The specific API endpoint for the request.
- `token_encoding_name`: The name of the token encoding method.

Returns the estimated number of tokens required for the request.

Examples:
```python
payload = {'prompt': 'Translate the following text:', 'max_tokens': 50}
num_tokens = APIUtil.calculate_num_token(payload, 'completions', 'cl100k_base')
print(num_tokens)
# Output: 100

payload_with_multiple_prompts = {'prompt': ['Prompt 1', 'Prompt 2'], 'max_tokens': 100}
num_tokens = APIUtil.calculate_num_token(payload_with_multiple_prompts, 'completions', 'cl100k_base')
print(num_tokens)
# Output: 250

payload_with_embedding = {'input': 'This is a sample text for embedding.'}
num_tokens = APIUtil.calculate_num_token(payload_with_embedding, 'embeddings', 'cl100k_base')
print(num_tokens)
# Output: 8
```

### `create_payload(input_, config, required_, optional_, input_key, **kwargs)`

^438814

Creates a payload dictionary based on the provided input, configuration, required fields, optional fields, and input key.

- `input_`: The input data for the payload.
- `config`: The configuration dictionary.
- `required_`: A list of required fields.
- `optional_`: A list of optional fields.
- `input_key`: The key to use for the input data in the payload.
- `**kwargs`: Additional keyword arguments to update the configuration.

Returns the created payload dictionary.
