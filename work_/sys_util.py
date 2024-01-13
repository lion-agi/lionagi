import base64

import binascii
import hashlib
from collections import OrderedDict
from functools import reduce, wraps
from typing import Any, Callable, Dict, List, Optional, Type


def find_depth(nested_obj, depth_strategy='uniform', ignore_non_iterable=False):
    """
    Calculates the maximum depth of a nested list, dictionary, or a combination of both.

    Args:
        nested_obj (list | dict): The nested object (list or dictionary) to find the depth of.
        depth_strategy (str): Strategy to calculate depth. 
                              'uniform' for consistent data types, 'mixed' for mixed types.
        ignore_non_iterable (bool): If True, non-iterable elements do not count towards depth.

    Returns:
        int: The maximum depth of the nested structure.

    Raises:
        ValueError: If an unsupported depth strategy is specified.
    """

    def uniform_depth(obj, current_depth=0):
        """Calculates depth assuming uniform data types in nested_obj."""
        if isinstance(obj, (list, tuple)):
            return max((uniform_depth(item, current_depth + 1) for item in obj), default=current_depth)
        elif isinstance(obj, dict):
            return max((uniform_depth(value, current_depth + 1) for value in obj.values()), default=current_depth)
        else:
            return current_depth if ignore_non_iterable else 1

    def mixed_depth(obj, current_depth=0):
        """Calculates depth allowing for mixed data types in nested_obj."""
        if isinstance(obj, (list, tuple, dict)):
            if isinstance(obj, dict):
                obj = obj.values()
            return max((mixed_depth(item, current_depth + 1) for item in obj), default=current_depth)
        else:
            return current_depth if ignore_non_iterable else 1

    if depth_strategy == 'uniform':
        return uniform_depth(nested_obj)
    elif depth_strategy == 'mixed':
        return mixed_depth(nested_obj)
    else:
        raise ValueError("Unsupported depth strategy. Choose 'uniform' or 'mixed'.")

def binary_to_hex(data: bytes) -> str:
    """Convert binary data to a hexadecimal string representation.
    
    Args:
        data: A bytes object containing binary data.

    Returns:
        A string containing the hexadecimal representation of the binary data.

    Examples:
        >>> binary_to_hex(b'\x00\x0F')
        '000f'
        >>> binary_to_hex(b'hello')
        '68656c6c6f'
    """
    return binascii.hexlify(data).decode()


def create_hash(data: str, algorithm: str = 'sha256') -> str:
    """Create a hash of the given data using the specified algorithm.

    Args:
        data: The string to hash.
        algorithm: The hashing algorithm to use (default is 'sha256').

    Returns:
        The hexadecimal digest of the hash.

    Examples:
        >>> create_hash('hello')
        '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode())
    return hasher.hexdigest()

def decode_base64(data: str) -> str:
    """Decode a base64 encoded string.

    Args:
        data: A base64 encoded string.

    Returns:
        A decoded string.

    Examples:
        >>> decode_base64('SGVsbG8sIFdvcmxkIQ==')
        'Hello, World!'
    """
    return base64.b64decode(data).decode()

def encode_base64(data: str) -> str:
    """Encode a string using base64 encoding.

    Args:
        data: A string to be encoded.

    Returns:
        A base64 encoded string.

    Examples:
        >>> encode_base64("Hello, World!")
        'SGVsbG8sIFdvcmxkIQ=='
    """
    return base64.b64encode(data.encode()).decode()

# decorators
def filter_decorator(predicate: Callable[[Any], bool]) -> Callable:
    """
    Decorator factory to filter values returned by a function based on a predicate.

    Args:
        predicate (Callable[[Any], bool]): Predicate function to filter values.

    Returns:
        Callable: Decorated function that filters its return values.
    """
    def decorator(func: Callable[..., List[Any]]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> List[Any]:
            values = func(*args, **kwargs)
            return [value for value in values if predicate(value)]
        return wrapper
    return decorator

def map_decorator(function: Callable[[Any], Any]) -> Callable:
    """
    Decorator factory to map values returned by a function using a provided function.

    Args:
        function (Callable[[Any], Any]): Function to map values.

    Returns:
        Callable: Decorated function that maps its return values.
    """
    def decorator(func: Callable[..., List[Any]]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> List[Any]:
            values = func(*args, **kwargs)
            return [function(value) for value in values]
        return wrapper
    return decorator

def reduce_decorator(function: Callable[[Any, Any], Any], initial: Any) -> Callable:
    """
    Decorator factory to reduce values returned by a function to a single value using the provided function.

    Args:
        function (Callable[[Any, Any], Any]): Reducing function.
        initial (Any): Initial value for reduction.

    Returns:
        Callable: Decorated function that reduces its return values.
    """
    def decorator(func: Callable[..., List[Any]]) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            values = func(*args, **kwargs)
            return reduce(function, values, initial)
        return wrapper
    return decorator

def compose(*functions: Callable[[Any], Any]) -> Callable:
    """
    Decorator factory that composes multiple functions. The output of each function is passed as 
    the input to the next, in the order they are provided.

    Args:
        *functions: Variable length list of functions to compose.

    Returns:
        Callable: A new function that is the composition of the given functions.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = func(*args, **kwargs)
            for function in reversed(functions):
                try:
                    value = function(value)
                except Exception as e:
                    print(f"Error in function {function.__name__}: {e}")
                    return None
            return value
        return wrapper
    return decorator

def memoize(maxsize: int = 10_000) -> Callable:
    """
    Decorator factory to memoize function calls. Caches the return values of the function for specific inputs.

    Args:
        maxsize (int): Maximum size of the cache. Defaults to 10,000.

    Returns:
        Callable: A memoized version of the function.
    """
    def decorator(function: Callable) -> Callable:
        cache = OrderedDict()
        
        @wraps(function)
        def memoized_function(*args):
            if args in cache:
                cache.move_to_end(args)  # Move the recently accessed item to the end
                return cache[args]

            if len(cache) >= maxsize:
                cache.popitem(last=False)  # Remove oldest cache entry

            result = function(*args)
            cache[args] = result
            return result
        
        return memoized_function
    
    return decorator

def _handle_error(value: Any, config: Dict[str, Any]) -> Any:
    """Handle an error by logging and returning a default value if provided.

    Args:
        value: The value to check for an exception.
        config: A dictionary with optional keys 'log' and 'default'.

    Returns:
        The original value or the default value from config if value is an exception.

    Examples:
        >>> handle_error(ValueError("An error"), {'log': True, 'default': 'default_value'})
        Error: An error
        'default_value'
    """
    if isinstance(value, Exception):
        if config.get('log', True):
            print(f"Error: {value}")  # Replace with appropriate logging mechanism
        return config.get('default', None)
    return value

def _validate_type(value: Any, expected_type: Type) -> Any:
    """Validate the type of value, raise TypeError if not expected type.

    Args:
        value: The value to validate.
        expected_type: The type that value is expected to be.

    Returns:
        The original value if it is of the expected type.

    Raises:
        TypeError: If value is not of the expected type.

    Examples:
        >>> validate_type(10, int)
        10
        >>> validate_type("10", int)
        Traceback (most recent call last):
        ...
        TypeError: Invalid type: expected <class 'int'>, got <class 'str'>
    """
    if not isinstance(value, expected_type):
        raise TypeError(f"Invalid type: expected {expected_type}, got {type(value)}")
    return value

def _convert_type(value: Any, target_type: Callable) -> Optional[Any]:
    """Convert the type of value to target_type, return None if conversion fails.

    Args:
        value: The value to convert.
        target_type: The type to convert value to.

    Returns:
        The converted value or None if conversion fails.

    Examples:
        >>> convert_type("10", int)
        10
        >>> convert_type("abc", int)
        Conversion error: invalid literal for int() with base 10: 'abc'
        None
    """
    try:
        return target_type(value)
    except (ValueError, TypeError) as e:
        print(f"Conversion error: {e}")  # Replace with appropriate logging mechanism
        return None

def _process_value(value: Any, config: Dict[str, Any]) -> Any:
    """
    Processes a value using a chain of functions defined in config.
    """
    processing_functions = {
        'handle_error': _handle_error,
        'validate_type': _validate_type,
        'convert_type': _convert_type
    }

    for key, func_config in config.items():
        func = processing_functions.get(key)
        if func:
            value = func(value, func_config)
    return value

def validate_return(**config):
    """
    Decorator factory to process the return value of a function using specified validation and conversion functions.

    Args:
        **config: Configuration dictionary specifying the processing functions and their settings.

    Returns:
        Callable: A decorator that applies specified processing to the function's return value.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            value = func(*args, **kwargs)
            return _process_value(value, config)

        return wrapper

    return decorator
