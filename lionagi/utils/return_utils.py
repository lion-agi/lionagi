from .sys_utils import to_lst, create_copies
from typing import Callable, Any, List
import time
import asyncio

# Hold call, a delayed call with error handling
def hold_call(input_, func_, hold=5, msg=None, ignore=False, **kwargs):
    """
    Executes a function after a specified hold time and handles exceptions.

    Args:
        x (Any): The input to the function.
        f (Callable): The function to execute.
        hold (int, optional): The time in seconds to wait before executing the function. Defaults to 5.
        msg (str, optional): The message to display in case of an error.
        ignore (bool, optional): Whether to ignore errors and print the message. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function execution.

    Raises:
        Exception: If any error occurs during function execution and ignore is False.
    """
    try: 
        time.sleep(hold)
        return func_(input_, **kwargs)
    except Exception as e:
        msg = msg if msg else ''
        msg += f"Error: {e}"
        if ignore:
            print(msg)
            return None
        else:
            raise Exception(msg)
        
# hold call async
# Correct the implementation of async_hold_call to handle non-callable functions
async def async_hold_call(input_, func_, hold=5, msg=None, ignore=False, **kwargs):
    """
    Asynchronously executes a function after a specified hold time and handles exceptions.

    Args:
        x (Any): The input to the function.
        f (Callable): The async function to execute.
        hold (int, optional): The time in seconds to wait before executing the function. Defaults to 5.
        msg (str, optional): The message to display in case of an error.
        ignore (bool, optional): Whether to ignore errors and print the message. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Any: The result of the function execution.

    Raises:
        Exception: If any error occurs during function execution and ignore is False.
    """
    try: 
        if not asyncio.iscoroutinefunction(func_):
            raise Exception(f"Given function {func_} is not a coroutine function.")
        await asyncio.sleep(hold)
        return await func_(input_, **kwargs)
    except Exception as e:
        msg = msg if msg else ''
        msg += f"Error: {e}"
        if ignore:
            print(msg)
            return None
        else:
            raise Exception(msg)

# list return, takes list of variable and apply function on each element
def l_return(input_: Any, func_: Any, 
             flat_d: bool = False, flat: bool = False, 
             dropna: bool=True) -> List[Any]:
    """
    Applies a function to each element in a list, where the list is created from the input.

    Args:
        input_ (Any): The input to convert into a list.
        func_ (Callable): The function to apply to each element in the list.
        flat_d (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to True.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after applying the function.

    Raises:
        ValueError: If the given function is not callable or cannot be applied to the input.
    """
    if isinstance(func_, Callable):
        try:
            return [func_(i) for i in to_lst(input_=input_, flat_d=flat_d, flat=flat, dropna=dropna)]
        except Exception as e:
            raise ValueError(f"Given function cannot be applied to the input. Error: {e}")
    else:
        raise ValueError(f"Given function is not callable.")
    
# list return async
async def async_l_return(input_: Any, func_: Any, 
                         flat_d: bool = False, flat: bool = False, 
                         dropna: bool=True) -> list:
    """
    Asynchronously applies a function to each element in a list, where the list is created from the input.

    Args:
        input_ (Any): The input to convert into a list.
        func_ (Callable): The async function to apply to each element in the list.
        flat_d (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to True.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        list: A list of results after asynchronously applying the function.

    Raises:
        ValueError: If the given function is not callable or cannot be applied to the input.
    """
    if isinstance(func_, Callable):
        try:
            tasks = [func_(i) for i in to_lst(input_=input_, flat_d=flat_d, flat=flat, dropna=dropna)]
            return await asyncio.gather(*tasks)
        except Exception as e:
            raise ValueError(f"Given function cannot be applied to the input. Error: {e}")
    else:
        raise ValueError(f"Given function is not callable.")

# map return, return a list of results, element wise mapped 
def m_return(input_: Any, func_: Callable, 
             flat_d: bool = False, flat: bool = False, 
             dropna: bool=True) -> List[Any]:
    """
    Applies multiple functions to multiple inputs. Each function is applied to its corresponding input.

    Args:
        input_ (Any): The inputs to be converted into a list.
        func_ (Callable): The functions to be converted into a list.
        flat_d (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to True.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after applying the functions to the inputs.

    Raises:
        AssertionError: If the number of inputs and functions are not the same.
    """
    input_ = to_lst(input_)
    func_ = to_lst(func_)
    assert len(input_) == len(func_), "The number of inputs and functions must be the same."
    return to_lst([l_return(inp, func, flat_d=flat_d, flat=flat, dropna=dropna) for func, inp in zip(func_, input_)])

# map return async
async def async_m_return(input_: Any, func_: Callable, 
                         flat_d: bool = False, flat: bool = False, 
                         dropna: bool=True) -> List[Any]:
    """
    Asynchronously applies multiple functions to multiple inputs. Each function is applied to its corresponding input.

    Args:
        input_ (Any): The inputs to be converted into a list.
        func_ (Callable): The functions to be converted into a list.
        flat_d (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to True.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after asynchronously applying the functions to the inputs.

    Raises:
        AssertionError: If the number of inputs and functions are not the same.
    """
    input_ = to_lst(input_)
    func_ = to_lst(func_)
    assert len(input_) == len(func_), "The number of inputs and functions must be the same."
    
    tasks = [async_l_return(inp, func, flat_d=flat_d, flat=flat, dropna=dropna) for func, inp in zip(func_, input_)]
    return await asyncio.gather(*tasks)

# explode return, return a 2d list of each function apply to each element, order by element
def e_return(_input: Any, _func: Callable, 
             flat_d: bool = False, flat: bool = False, 
             dropna: bool=True) -> List[Any]:
    """
    Applies a list of functions to each element in the input list.

    Args:
        _input (Any): The input to be converted into a list.
        _func (Callable): The functions to be converted into a list.
        flat_d (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to True.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after applying the functions to the inputs.
    """
    f = lambda x, y: m_return(create_copies(x,len(to_lst(y))), y, flat_d=flat_d, flat=flat, dropna=dropna)
    return to_lst([f(inp, _func) for inp in to_lst(_input)], flat=flat)

# explode return async
async def async_e_return(_input: Any, _func: Callable, 
                         flat_d: bool = False, flat: bool = False, 
                         dropna: bool=True) -> List[Any]:
    """
    Asynchronously applies a list of functions to each element in the input list.

    Args:
        _input (Any): The input to be converted into a list.
        _func (Callable): The functions to be converted into a list.
        flat_d (bool, optional): Whether to flatten dictionaries. Defaults to False.
        flat (bool, optional): Whether to flatten lists. Defaults to True.
        dropna (bool, optional): Whether to drop None values. Defaults to True.

    Returns:
        List[Any]: A list of results after asynchronously applying the functions to the inputs.
    """
    async def async_f(x, y):
        return await async_m_return(create_copies(x,len(to_lst(y))), y, flat_d=flat_d, flat=flat, dropna=dropna)

    tasks = [async_f(inp, _func) for inp in to_lst(_input)]
    return await asyncio.gather(*tasks)