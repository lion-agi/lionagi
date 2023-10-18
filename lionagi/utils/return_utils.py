from lionagi.utils.sys_utils import to_list, flatten_list
from typing import Callable, Any, List
import copy
import time

# various utils for convinient return value handling
# l_return: apply a function to each element in the list converted from the input
# m_return: apply a list of functions to a list of inputs element-wise
# e_return: generate multiple outputs by applying list of function to each element in a list of inputs
# hold_call: executes a function with a delay and handles any exceptions that occur during execution


def create_copies(_input: Any, n: int) -> List[Any]:
    """
    Create 'n' deep copies of the given input.
    
    Parameters:
        _input: Any
            The input object to be copied.
        n: int
            The number of copies to create.
            
    Returns:
        List[Any]
            A list containing 'n' deep copies of the input.
    """
    return [copy.deepcopy(_input) for _ in range(n)]


def l_return(_input: Any, _func: Any, flatten_dict: bool = False, flatten_list: bool=False) -> List[Any]:
    """
    Apply a function to each element in the list converted from the input.
    
    Parameters:
        _input: Any
            The input on which the function is to be applied.
        _func: Any (Callable)
            The function to apply to the elements of the list.
        flatten_dict: bool, optional
            If True, flattens the dictionary before converting to list.
            
    Returns:
        List[Any]
            A list containing the return values of the applied function.
            
    Raises:
        ValueError: If the given function is not callable or cannot be applied.
    """
    if isinstance(_func, Callable):
        try:
            if flatten_list: 
                return flatten_list([_func(i) for i in to_list(_input, flatten_dict=flatten_dict)])
            else:
                return [_func(i) for i in to_list(_input, flatten_dict=flatten_dict)]
        except Exception as e:
            raise ValueError(f"Given function cannot be applied to the input. Error: {e}")
    else:
        raise ValueError(f"Given function is not callable.")

def m_return(_input: Any, _func: Any):
    """
    Apply a list of functions to a list of inputs element-wise.
    
    Parameters:
        _input: Any
            List of inputs.
        _func: Any
            List of functions to apply.
            
    Returns:
        List[List[Any]]
            A list containing lists of return values for each function applied.
            
    Raises:
        AssertionError: If the number of inputs and functions are not the same.
    """
    _input = to_list(_input)
    _func = to_list(_func)
    assert len(_input) == len(_func), "The number of inputs and functions must be the same."
    return flatten_list([l_return(inp, func) for func, inp in zip(_func, _input)])

def e_return(_input, _func, flatten_dict=False):
    """
    Generate multiple outputs by applying multiple functions to multiple copies of the input.
    
    Parameters:
        _input: Any
            The input on which the functions are to be applied.
        _func: Any
            The functions to apply.
        flatten_dict: bool, optional
            If True, flattens the dictionary before converting to list.
            
    Returns:
        List[List[Any]]
            A list containing lists of return values for each function applied.
    """
    f = lambda x, y: m_return(create_copies(x,len(to_list(y))), y)
    return [f(inp, _func) for inp in to_list(_input, flatten_dict=flatten_dict)]


def hold_call(x, f, hold=5, msg=None, ignore=False, **kwags):
    """
    Executes a function with a delay and handles any exceptions that occur during execution.
    
    Args:
        x: The argument to be passed to the function f.
        f (func): The function to be executed.
        hold (int, optional): The amount of delay before function execution, in seconds. Defaults to 5.
        msg (str, optional): Additional error message to be included when an exception occurs. Defaults to None.
        ignore (bool, optional): If true, exceptions are printed and the function will return None. If false, exceptions will be raised. Defaults to False.
        **kwags : Variable list of arguments to be passed to function f.

    Returns:
        Output of the function f or None if an exception occurred and ignore is set to True.

    Raises:
        Exception: If an exception occurs during function execution and ignore is False.
    """    
    try: 
        time.sleep(hold)
        return f(x, **kwags)
    except Exception as e:
        msg = msg if msg else ''
        msg+=f"Error: {e}"
        if ignore:
            print(msg)
            return None
        else:
            raise Exception(msg)