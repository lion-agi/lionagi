def is_arraylike(x):
    return hasattr(x, "__getitem__")

def array_rtn(x, func):
    return [func(i) for i in x] if is_arraylike(x) else func(x)

def is_numeric(x):
    return array_rtn(np.array(x).flatten(),lambda arg: str(arg).isnumeric())

def isvalue_inset(x, set):
    return array_rtn(x,lambda arg: bool(np.isin(arg, set)))

def istype_inset(x, types):
    return isvalue_inset(type(x),types)

def istype_inset_dtype(x, dtypes):
    return isvalue_inset(np.array(x).flatten().dtype,dtypes)

def istype_valid(x,types=None,dtypes=None):
    if types is None and dtypes is None:
        pass # error handling here
    is_type = istype_inset(x,types) if types is not None else True
    is_dtype = istype_inset_dtype(x,dtypes) if dtypes is not None else True
    return is_type and is_dtype

def isvalue_inrange(x, min, max, interval=None, inclusive=True):
    funcs = {
        "int_inc": lambda arg: bool(np.isin(arg, np.linspace(min, max+interval, interval))),
        "int_ninc": lambda arg: bool(np.isin(arg, np.linspace(min+interval, max, interval))),
        "nint_inc": lambda arg: arg <= max and arg >= min,
        "nint_ninc": lambda arg: arg < max and arg > min
    }
    mtd = any
    if inclusive:
        mtd = "nint_inc" if interval is None else "int_inc"
    else:
        mtd = "nint_ninc" if interval is None else "int_ninc"
    func = funcs.get(mtd,None)
    
    return array_rtn(x,func)

def isvalid_length(x,y,ratio=1):
    return np.size(x) == np.size(y) * ratio



import re

def ensure_list_elements_pass(lst, check_func):
    if not all(check_func(item) for item in lst):
        raise ValueError("Not all elements in the list pass the custom check")
    return True

def ensure_dict_contains_subset(dct, required_subset):
    if not required_subset.items() <= dct.items():
        raise KeyError("Dictionary does not contain the required subset")
    return True


def ensure_value_in_list(value, lst):
    if value not in lst:
        raise ValueError(f"Value {value} is not in the provided list")
    return True


def ensure_iterable(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        raise TypeError("Object is not iterable")


def is_numeric():
    ...
    
def ensure_valid_url(value):
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    return ensure_string_matches_pattern(value, url_pattern)

def ensure_dict_values_type(dct, value_type):
    if not all(isinstance(val, value_type) for val in dct.values()):
        raise TypeError(f"All values in the dictionary must be of type {value_type}")
    return True


def ensure_no_duplicates(lst):
    if len(lst) != len(set(lst)):
        raise ValueError("List contains duplicate elements")
    return True


def ensure_list_types(lst, allowed_types):
    if not all(isinstance(item, allowed_types) for item in lst):
        raise TypeError(f"All elements in the list must be of types {allowed_types}")
    return True


def ensure_positive_number(value):
    if value <= 0:
        raise ValueError("Value must be a positive number")
    return True

def ensure_list_length(lst, expected_length):
    if len(lst) != expected_length:
        raise ValueError(f"List must contain exactly {expected_length} elements")
    return True




def have_keys(dct, required_keys):
    missing_keys = [key for key in required_keys if key not in dct]
    if missing_keys:
        raise KeyError(f"Missing required keys: {missing_keys}")
    return True

def is_empty(value):
    if not value:
        raise ValueError("Value cannot be empty")
    return True

def check_value_in_range(value, min_value, max_value):
    if not (min_value <= value <= max_value):
        raise ValueError(f"Value {value} is not within range {min_value} to {max_value}")
    return True

def ensure_value_one_of(value, allowed_values):
    if value not in allowed_values:
        raise ValueError(f"Value {value} is not an allowed value: {allowed_values}")
    return True

def ensure_string_matches_pattern(value, pattern):
    if not re.match(pattern, value):
        raise ValueError(f"Value does not match pattern: {pattern}")
    return True

def ensure_type(value, expected_type):
    if not isinstance(value, expected_type):
        raise TypeError(f"Expected type {expected_type}, got {type(value)}")
    return True



import re
from typing import Any, Callable, Dict, Iterable, List, Tuple, Type, Union


def list_return():
    
    
    
    
    ...


def type_is_valid():
    ...
    



def is_list_elements_valid(lst: List[Any], check_func: Callable[[Any], bool], error_msg: str) -> bool:
    if not all(check_func(item) for item in lst):
        raise ValueError(error_msg)
    return True


def is_dict_contains_subset(dct: Dict[Any, Any], required_subset: Dict[Any, Any], error_msg: str) -> bool:
    if not required_subset.items() <= dct.items():
        raise KeyError(error_msg)
    return True


def is_value_in_list(value: Any, lst: List[Any], error_msg: str) -> bool:
    if value not in lst:
        raise ValueError(error_msg)
    return True


def is_iterable(obj: Any, error_msg: str) -> bool:
    if not isinstance(obj, Iterable):
        raise TypeError(error_msg)
    return True


def is_valid_url(value: str, error_msg: str) -> bool:
    url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    if not re.match(url_pattern, value):
        raise ValueError(error_msg)
    return True


def is_dict_values_type(dct: Dict[Any, Any], value_type: Type, error_msg: str) -> bool:
    if not all(isinstance(val, value_type) for val in dct.values()):
        raise TypeError(error_msg)
    return True


def is_no_duplicates(lst: List[Any], error_msg: str) -> bool:
    if len(lst) != len(set(lst)):
        raise ValueError(error_msg)
    return True


def is_list_types(lst: List[Any], allowed_types: Union[Tuple[Type, ...], Type], error_msg: str) -> bool:
    if not all(isinstance(item, allowed_types) for item in lst):
        raise TypeError(error_msg)
    return True


def is_positive_number(value: Union[int, float], error_msg: str) -> bool:
    if value <= 0:
        raise ValueError(error_msg)
    return True


def is_list_length(lst: List[Any], expected_length: int, error_msg: str) -> bool:
    if len(lst) != expected_length:
        raise ValueError(error_msg)
    return True


def is_dict_has_keys(dct: Dict[Any, Any], required_keys: List[str], error_msg: str) -> bool:
    missing_keys = [key for key in required_keys if key not in dct]
    if missing_keys:
        raise KeyError(error_msg)
    return True


def is_not_empty(value: Any, error_msg: str) -> bool:
    if not value:
        raise ValueError(error_msg)
    return True


def is_value_in_range(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float], error_msg: str) -> bool:
    if not (min_value <= value <= max_value):
        raise ValueError(error_msg)
    return True


def is_value_one_of(value: Any, allowed_values: Iterable[Any], error_msg: str) -> bool:
    if value not in allowed_values:
        raise ValueError(error_msg)
    return True


def is_string_matches_pattern(value: str, pattern: str, error_msg: str) -> bool:
    if not re.match(pattern, value):
        raise ValueError(error_msg)
    return True


def is_type(value: Any, expected_type: Type, error_msg: str) -> bool:
    if not isinstance(value, expected_type):
        raise TypeError(error_msg)
    return True


def is_arraylike(x):
    return hasattr(x, "__getitem__")

def array_rtn(x, func):
    return [func(i) for i in x] if is_arraylike(x) else func(x)

def istype_numeric(x):
    return array_rtn(np.array(x).flatten(),lambda arg: str(arg).isnumeric())

def isvalue_inset(x, set):
    return array_rtn(x,lambda arg: bool(np.isin(arg, set)))

def istype_inset(x, types):
    return isvalue_inset(type(x),types)

def istype_inset_dtype(x, dtypes):
    return isvalue_inset(np.array(x).flatten().dtype,dtypes)

def istype_valid(x,types=None,dtypes=None):
    if types is None and dtypes is None:
        pass # error handling here
    is_type = istype_inset(x,types) if types is not None else True
    is_dtype = istype_inset_dtype(x,dtypes) if dtypes is not None else True
    return is_dtype and is_dtype

def isvalue_inrange(x, min, max, interval=None, inclusive=True):
    funcs = {
        "int_inc": lambda arg: bool(np.isin(arg, np.linspace(min, max+interval, interval))),
        "int_ninc": lambda arg: bool(np.isin(arg, np.linspace(min+interval, max, interval))),
        "nint_inc": lambda arg: arg <= max and arg >= min,
        "nint_ninc": lambda arg: arg < max and arg > min
    }
    mtd = any
    if inclusive:
        mtd = "nint_inc" if interval is None else "int_inc"
    else:
        mtd = "nint_ninc" if interval is None else "int_ninc"
    func = funcs.get(mtd,None)
    
    return array_rtn(x,func)


import numpy as np
