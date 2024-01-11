import json
import tempfile
# this module has no internal dependency 
import logging
import re
from typing import Callable, Any
from .sys_util import to_list
        
        
def api_method(http_session, method: str = "post") -> Callable:
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
    if "error" in response_json:
        logging.warning(f"API call failed with error: {response_json['error']}")
        return True
    return False
    
def api_rate_limit_error(response_json: dict) -> bool:
    return "Rate limit" in response_json["error"].get("message", "")

def api_endpoint_from_url(request_url: str) -> str:

    match = re.search(r"^https://[^/]+/v\d+/(.+)$", request_url)
    return match.group(1) if match else ""

def to_temp(input: Any, 
            flatten_dict: bool = False, 
            flat: bool = False, 
            dropna: bool = False):
    input = to_list(input, flatten_dict, flat, dropna)
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(input, temp_file)
    except TypeError as e:
        temp_file.close()  # Ensuring file closure before raising error
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    temp_file.close()
    return temp_file

