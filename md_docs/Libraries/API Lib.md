
This module contains the `APIUtil` class, which provides utility methods for assisting with common API usage patterns.

### Class: `APIUtil`

A utility class for assisting with common API usage patterns.

##### `api_method`
`(http_session: aiohttp.ClientSession, method: str = "post") -> Callable`
Returns the corresponding HTTP method function from the `http_session` object.

Parameters:
- `http_session` (aiohttp.ClientSession): The session object from the `aiohttp` library.
- `method` (str): The HTTP method as a string (default: "post").

Returns:
Callable: The callable for the specified HTTP method.

Raises:
- `ValueError`: If the method is not one of the allowed ones.

##### `api_error`
`(response_json: Mapping[str, Any]) -> bool`
Checks if the given `response_json` dictionary contains an "error" key.

Parameters:
- `response_json` (Mapping[str, Any]): The JSON response as a dictionary.

Returns:
bool: True if there is an error, False otherwise.

##### `api_rate_limit_error`
`(response_json: Mapping[str, Any]) -> bool`
Checks if the error message in the `response_json` dictionary contains the phrase "Rate limit".

Parameters:
- `response_json` (Mapping[str, Any]): The JSON response as a dictionary.

Returns:
bool: True if the phrase "Rate limit" is found, False otherwise.

##### `api_endpoint_from_url`
`(request_url: str) -> str`
Extracts the API endpoint from a given URL using a regular expression.

Parameters:
- `request_url` (str): The full URL to the API endpoint.

Returns:
str: The extracted endpoint or an empty string if the pattern does not match.

##### `async unified_api_call`
`(http_session: aiohttp.ClientSession, method: str, url: str, **kwargs) -> Any`
Makes an API call and automatically retries on rate limit error.

Parameters:
- `http_session` (aiohttp.ClientSession): The session object from the `aiohttp` library.
- `method` (str): The HTTP method as a string.
- `url` (str): The URL to which the request is made.
- `**kwargs`: Additional keyword arguments to pass to the API call.

Returns:
Any: The JSON response as a dictionary.

##### `get_cache_key`
`(url: str, params: Mapping[str, Any] | None) -> str`
Creates a unique cache key based on the URL and parameters.

Parameters:
- `url` (str): The URL for the API call.
- `params` (Mapping[str, Any] | None): The parameters for the API call.

Returns:
str: The cache key as a string.

##### `async retry_api_call`
`(http_session: aiohttp.ClientSession, url: str, retries: int = 3, backoff_factor: float = 0.5, **kwargs) -> Any`
Retries an API call on failure, with exponential backoff.

Parameters:
- `http_session` (aiohttp.ClientSession): The `aiohttp` client session.
- `url` (str): The URL to make the API call.
- `retries` (int): The number of times to retry (default: 3).
- `backoff_factor` (float): The backoff factor for retries (default: 0.5).
- `**kwargs`: Additional arguments for the API call.

Returns:
Any: The response from the API call, if successful; otherwise, None.

##### `async upload_file_with_retry`
`(http_session: aiohttp.ClientSession, url: str, file_path: str, param_name: str = "file", additional_data: Mapping[str, Any] = None, retries: int = 3) -> Any`
Uploads a file to a specified URL with a retry mechanism for handling failures.

Parameters:
- `http_session` (aiohttp.ClientSession): The HTTP session object to use for making the request.
- `url` (str): The URL to which the file will be uploaded.
- `file_path` (str): The path to the file that will be uploaded.
- `param_name` (str): The name of the parameter expected by the server for the file upload (default: "file").
- `additional_data` (Mapping[str, Any]): Additional data to be sent with the upload (default: None).
- `retries` (int): The number of times to retry the upload in case of failure (default: 3).

Returns:
Any: The HTTP response object.

##### `async get_oauth_token_with_cache`
`(http_session: aiohttp.ClientSession, auth_url: str, client_id: str, client_secret: str, scope: str) -> str`
Retrieves an OAuth token from the authentication server and caches it to avoid unnecessary requests.

Parameters:
- `http_session` (aiohttp.ClientSession): The HTTP session object to use for making the request.
- `auth_url` (str): The URL of the authentication server.
- `client_id` (str): The client ID for OAuth authentication.
- `client_secret` (str): The client secret for OAuth authentication.
- `scope` (str): The scope for which the OAuth token is requested.

Returns:
str: The OAuth token as a string.

##### `async cached_api_call`
`(http_session: aiohttp.ClientSession, url: str, **kwargs) -> Any`
Makes an API call and caches the response for a specified duration.

Parameters:
- `http_session` (aiohttp.ClientSession): The `aiohttp` client session.
- `url` (str): The URL for the API call.
- `**kwargs`: Additional arguments for the API call.

Returns:
Any: The response from the API call, if successful; otherwise, None.

##### `calculate_num_token`
`(payload: Mapping[str, Any] = None, api_endpoint: str = None, token_encoding_name: str = None) -> int`
Calculates the number of tokens required for a request based on the payload and API endpoint.

Parameters:
- `payload` (Mapping[str, Any]): The payload of the request (default: None).
- `api_endpoint` (str): The specific API endpoint for the request (default: None).
- `token_encoding_name` (str): The name of the token encoding method (default: None).

Returns:
int: The estimated number of tokens required for the request.

##### `create_payload`
`(input_, config, required_, optional_, input_key, **kwargs)`
Creates a payload dictionary based on the provided input, configuration, and required/optional fields.

Parameters:
- `input_` (Any): The input value for the payload.
- `config` (Mapping[str, Any]): The configuration dictionary.
- `required_` (Sequence[str]): The required fields for the payload.
- `optional_` (Sequence[str]): The optional fields for the payload.
- `input_key` (str): The key for the input value in the payload.
- `**kwargs`: Additional keyword arguments to update the configuration.

Returns:
dict: The created payload dictionary.

### Usage Example
```python
import aiohttp
from lionagi.libs.api_util import APIUtil

async def main():
    async with aiohttp.ClientSession() as session:
        # Make an API call using the unified_api_call method
        response = await APIUtil.unified_api_call(
            session,
            "get",
            "https://api.example.com/v1/data",
            params={"key": "value"}
        )
        print(response)

        # Extract the API endpoint from a URL
        url = "https://api.example.com/v1/users"
        endpoint = APIUtil.api_endpoint_from_url(url)
        print(endpoint)

        # Retry an API call on failure
        response = await APIUtil.retry_api_call(
            session,
            "https://api.example.com/v1/data",
            retries=3,
            backoff_factor=0.5
        )
        print(response)

        # Upload a file with retry
        response = await APIUtil.upload_file_with_retry(
            session,
            "https://api.example.com/v1/upload",
            "path/to/file.txt",
            param_name="file",
            additional_data={"key": "value"},
            retries=3
        )
        print(response)

asyncio.run(main())
```

In this example, we demonstrate the usage of various utility methods provided by the `APIUtil` class.

We create an `aiohttp.ClientSession` and use it to make API calls using the `unified_api_call`, `retry_api_call`, and `upload_file_with_retry` methods. We also extract the API endpoint from a URL using the `api_endpoint_from_url` method.

The responses from the API calls are printed to the console.
