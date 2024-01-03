import logging
import re
from typing import Callable
        
        
def api_method(http_session, method: str = "post") -> Callable:
    """
    Retrieves the appropriate HTTP method from an HTTP session object.

    Parameters:
        http_session: The HTTP session object from which to retrieve the method.
        method (str): The HTTP method to retrieve. Defaults to 'post'.

    Returns:
        Callable: The HTTP method function from the session object.

    Raises:
        ValueError: If the provided method is not one of ['post', 'delete', 'head', 'options', 'patch'].

    Examples:
        api_method = api_methods(session, "post") # Retrieves the 'post' method from the session
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

def api_endpoint_from_url(request_url: str) -> str:
    """
    Extracts the API endpoint from a given URL.

    Parameters:
        request_url (str): The URL from which to extract the API endpoint.

    Returns:
        str: The extracted API endpoint, or an empty string if no match is found.

    Examples:
        endpoint = api_endpoint_from_url("https://api.example.com/v1/users")
        # endpoint will be 'users'
    """
    match = re.search(r"^https://[^/]+/v\d+/(.+)$", request_url)
    return match.group(1) if match else ""
    
def api_error(response_json: dict) -> bool:
    """
    Logs a warning and returns True if an error is found in the API response.

    Parameters:
        response_json (dict): The JSON response from the API call.

    Returns:
        bool: True if an error is present in the response, False otherwise.

    Examples:
        if api_error(response):
            # Handle the error
    """
    if "error" in response_json:
        logging.warning(f"API call failed with error: {response_json['error']}")
        return True
    return False
    
def api_rate_limit_error(response_json: dict) -> bool:
    """
    Checks if the API response indicates a rate limit error.

    Parameters:
        response_json (dict): The JSON response from the API call.

    Returns:
        bool: True if the response contains a rate limit error message, False otherwise.

    Examples:
        if rate_limit_error(response):
            # Handle the rate limit error
    """
    return "Rate limit" in response_json["error"].get("message", "")
