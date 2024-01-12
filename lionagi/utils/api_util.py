import json
import tempfile

import logging
import re
import csv
from typing import Callable, Any
from .sys_util import to_list
        
        
def api_method(http_session, method: str = "post") -> Callable:
    """
    Retrieves a method (such as POST, DELETE) from the HTTP session object.

    Args:
        http_session: The session object used for making HTTP requests.
        
        method (str, optional): The HTTP method to retrieve. Default is "post".

    Returns:
        Callable: The HTTP method callable from the session object.

    Raises:
        ValueError: If the method is not one of ['post', 'delete', 'head', 'options', 'patch'].

    Example:
        >>> session = requests.Session()
        >>> post_method = api_method(session, "post")
        >>> response = post_method(url="https://api.example.com/data", json={"key": "value"})
    """

    if method not in ["post", "delete", "head", "options", "patch"]:
        raise ValueError("Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']")
    elif method == "post":
        return http_session.post
    elif method == "delete":
        return http_session.delete
    elif method == "head":
        return http_session.head
    elif method == "options":
        return http_session.options
    elif method == "patch":
        return http_session.patch
    
def api_error(response_json: dict) -> bool:
    """
    Checks if the API response contains an error.

    Args:
        response_json (dict): The JSON response returned from an API call.

    Returns:
        bool: True if the response contains an error; False otherwise.

    Logs a warning if an error is found.

    Example:
        >>> response = requests.post("https://api.example.com/data")
        >>> if api_error(response.json()):
        >>>     print("Error occurred in API call")
    """

    if "error" in response_json:
        logging.warning(f"API call failed with error: {response_json['error']}")
        return True
    return False
    
def api_rate_limit_error(response_json: dict) -> bool:
    """
    Checks if the API response contains a rate limit error.

    Args:
        response_json (dict): The JSON response returned from an API call.

    Returns:
        bool: True if the response contains a rate limit error; False otherwise.

    Example:
        >>> response = requests.post("https://api.example.com/data")
        >>> if api_rate_limit_error(response.json()):
        >>>     print("Rate limit exceeded for API call")
    """

    return "Rate limit" in response_json["error"].get("message", "")

def api_endpoint_from_url(request_url: str) -> str:
    """
    Extracts the API endpoint from a URL.

    Args:
        request_url (str): The full URL from which to extract the endpoint.

    Returns:
        str: The extracted endpoint from the URL, or an empty string if not found.

    Example:
        >>> url = "https://api.example.com/v1/users"
        >>> endpoint = api_endpoint_from_url(url)
        >>> print(endpoint)  # Output: "users"
    """
    match = re.search(r"^https://[^/]+/v\d+/(.+)$", request_url)
    return match.group(1) if match else ""

def to_temp(input: Any, 
            flatten_dict: bool = False, 
            flat: bool = False, 
            dropna: bool = False) -> tempfile.NamedTemporaryFile:
    """
    Writes input data to a temporary file in JSON format.

    Args:
        input (Any): The data to be written to the temporary file. This can be any data type.
        
        flatten_dict (bool, optional): If True, flattens dictionary structures in the input. Default is False.
        
        flat (bool, optional): If True, flattens nested lists in the input. Default is False.
        
        dropna (bool, optional): If True, removes None values from the input. Default is False.

    Returns:
        tempfile.NamedTemporaryFile: A reference to the temporary file containing the input data.

    Raises:
        TypeError: If the data provided is not JSON serializable.

    Example:
        >>> data = {"key": ["value1", "value2"], "key2": "value3"}
        >>> temp_file = to_temp(data, flatten_dict=True)
        >>> print(temp_file.name)  # Path to the temporary file
    """
    input = to_list(input, flatten=flat, dropna=dropna)
    if flatten_dict:
        input = [flatten_dict(item) if isinstance(item, dict) else item for item in input]

    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(input, temp_file)
    except TypeError as e:
        temp_file.close()  # Ensuring file closure before raising error
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    temp_file.close()
    return temp_file


def build_api_request(http_session, method: str, url: str, headers: dict = None, 
                      params: dict = None, data: Any = None, json: dict = None
                      ):
    """
    Builds and sends an API request based on specified parameters.

    Args:
        http_session: The HTTP session object for making requests.
        
        method (str): The HTTP method (e.g., 'GET', 'POST').
        
        url (str): The URL for the API request.
        
        headers (dict, optional): Headers to include in the request.
        
        params (dict, optional): Query parameters to include in the request.
        
        data (Any, optional): Data to include in the request body.
        
        json (dict, optional): JSON data to include in the request body.

    Returns:
        The response from the API request.
    """
    if method not in ["post", "delete", "head", "options", "patch", "get"]:
        raise ValueError("Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch', 'get']")
    request_func = getattr(http_session, method.lower())
    return request_func(url, headers=headers, params=params, data=data, json=json)

def api_call_with_error_handling(http_session, url, **kwargs):
    """
    Performs an API call with enhanced error handling and logging.

    Args:
        http_session: The HTTP session object for making requests.
        
        url (str): The URL for the API request.
        
        **kwargs: Additional arguments for the API request (e.g., method, headers).

    Returns:
        The API response, or None if an error occurs.

    Logs errors instead of raising them for better error management.
    """
    try:
        response = http_session.request(url=url, **kwargs)
        response.raise_for_status()
        return response
    except Exception as e:
        logging.error(f"API call to {url} failed: {e}")
        return None

def upload_file(http_session, url: str, file_path: str, param_name: str = 'file', additional_data: dict = None):
    """
    Uploads a file to an API.

    Args:
        http_session: The HTTP session object for making requests.
        
        url (str): The URL for the file upload API.
        
        file_path (str): The path to the file to be uploaded.
        
        param_name (str, optional): The name of the parameter for the file in the API.
        
        additional_data (dict, optional): Additional data to include in the request.

    Returns:
        The response from the file upload request.
    """
    with open(file_path, 'rb') as file:
        files = {param_name: file}
        return http_session.post(url, files=files, data=additional_data)

def transform_response_to_csv(response: dict, output_file: str) -> None:
    """
    Transforms a JSON response to a CSV file.

    Args:
        response (dict): The JSON response from an API call.
        
        output_file (str): The path to the output CSV file.

    Writes the transformed CSV to the specified output file.
    """
    if not isinstance(response, (list, dict)):
        raise ValueError("Response must be a list or dictionary.")

    # Assume the response is a list of dictionaries if it's a list
    rows = response if isinstance(response, list) else [response]
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def handle_webhook(request_data: dict, validation_func: Callable = None) -> dict:
    """
    Handles incoming webhook data with optional validation.

    Args:
        request_data (dict): The data received from the webhook.
        
        validation_func (Callable, optional): A function to validate the webhook data.

    Returns:
        dict: The processed response data, or an error message if validation fails.
    """
    if validation_func and not validation_func(request_data):
        return {"error": "Invalid webhook data"}

    # Process the webhook data
    # This is just a placeholder, actual processing depends on webhook requirements
    processed_data = {"message": "Webhook received successfully", "data": request_data}
    return processed_data

def get_oauth_token(http_session, auth_url: str, client_id: str, client_secret: str, scope: str) -> str:
    """
    Retrieves an OAuth token for API authentication.

    Args:
        http_session: The HTTP session object for making requests.
        
        auth_url (str): The URL to obtain the OAuth token.
        
        client_id (str): The client ID for OAuth.
        
        client_secret (str): The client secret for OAuth.
        
        scope (str): The scope of the access request.

    Returns:
        str: The obtained OAuth token.
    """
    auth_response = http_session.post(auth_url, data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': scope
    })
    auth_response.raise_for_status()
    return auth_response.json().get('access_token')
