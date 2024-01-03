import asyncio
import time
from typing import Any, Callable, List, Optional, Union

from .sys_util import create_copy
from .type_util import to_list


def hcall(
    input: Any, func: Callable, sleep: int = 0.1, 
    message: Optional[str] = None, 
    ignore_error: bool = False, **kwargs
    ) -> Any:
    """
    Executes a function after a specified delay, handling exceptions optionally.

    Waits for 'sleep' seconds before calling 'func' with 'input'. Handles exceptions by
    printing a message and optionally re-raising them.

    Parameters:
        input (Any): Input to the function.

        func (Callable): Function to execute.

        sleep (int, optional): Time in seconds to wait before calling the function. Defaults to 0.1.

        message (Optional[str], optional): Message to print on exception. Defaults to None.

        ignore_error (bool, optional): If True, ignores exceptions. Defaults to False.

        **kwargs: Additional keyword arguments for the function.

    Returns:
        Any: Result of the function call.

    Raises:
        Exception: Re-raises the exception unless 'ignore_error' is True.

    Example:
        >>> def add_one(x):
        ...     return x + 1
        >>> hold_call(5, add_one, sleep=2)
        6
    """
    try:
        time.sleep(sleep)
        return func(input, **kwargs)
    except Exception as e:
        if message:
            print(f"{message} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore_error:
            raise

async def ahcall(
    input_: Any, func: Callable, sleep: int = 5, 
    message: Optional[str] = None, 
    ignore_error: bool = False, **kwargs
    ) -> Any:
    """
    Asynchronously executes a function after a specified delay, handling exceptions optionally.

    Waits for 'sleep' seconds before calling 'func' with 'input'. Handles exceptions by
    printing a message and optionally re-raising them.

    Parameters:
        input (Any): Input to the function.

        func (Callable): Asynchronous function to execute.

        sleep (int, optional): Time in seconds to wait before calling the function. Defaults to 5.

        message (Optional[str], optional): Message to print on exception. Defaults to None.

        ignore_error (bool, optional): If True, ignores exceptions. Defaults to False.

        **kwargs: Additional keyword arguments for the function.

    Returns:
        Any: Result of the asynchronous function call.

    Raises:
        Exception: Re-raises the exception unless 'ignore_error' is True.

    Example:
        >>> async def async_add_one(x):
        ...     return x + 1
        >>> asyncio.run(ahold_call(5, async_add_one, sleep=2))
        6
    """
    try:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"The function {func} must be an asynchronous function.")
        await asyncio.sleep(sleep)
        return await func(input_, **kwargs)
    except Exception as e:
        if message:
            print(f"{message} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore_error:
            raise

def lcall(
    input_: Any, func_: Callable, flatten: bool = False, 
    dropna: bool = False, **kwargs
    ) -> List[Any]:
    """
    Applies a function to each element of `input`, after converting it to a list.

    This function converts the `input` to a list, with options to flatten structures 
    and lists, and then applies a given `func` to each element of the list.

    Parameters:
        input (Any): The input to be converted to a list and processed.

        func (Callable): The function to apply to each element of the list.

        flatten_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.

        flat (bool, optional): If True, flattens nested lists in the input. Defaults to False.

        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results of applying the `func` to each element.

    Raises:
        ValueError: If the `func` cannot be applied to the `input`.

    Example:
        >>> def square(x):
        ...     return x * x
        >>> l_call([1, 2, 3], square)
        [1, 4, 9]
    """
    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        return [func_(i, **kwargs) for i in lst]
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

async def alcall(
    input_: Any, func_: Callable, flatten: bool = False, dropna: bool = True, **kwargs
    ) -> List[Any]:
    """
    Asynchronously applies a function to each element of `input`, after converting it to a list.

    This function converts the `input` to a list, with options to flatten 
    dictionaries and lists, and then applies a given asynchronous `func` to 
    each element of the list asynchronously.

    Parameters:
        input (Any): The input to be converted to a list and processed.

        func (Callable): The asynchronous function to apply to each element of the list.

        flatten_dict (bool, optional): If True, flattens dictionaries in the input. Defaults to False.

        flat (bool, optional): If True, flattens nested lists in the input. Defaults to False.

        dropna (bool, optional): If True, drops None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results of applying the `func` to each element.

    Raises:
        ValueError: If the `func` cannot be applied to the `input`.

    Example:
        >>> async def async_square(x):
        ...     return x * x
        >>> asyncio.run(al_call([1, 2, 3], async_square))
        [1, 4, 9]
    """
    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        tasks = [func_(i, **kwargs) for i in lst]
        return await asyncio.gather(*tasks)
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

def mcall(
    input_: Union[Any, List[Any]], func_: Union[Callable, List[Callable]], 
    flatten: bool = True, dropna: bool = True, **kwargs
    ) -> List[Any]:
    """
    Maps multiple functions to corresponding elements of the input.

    This function applies a list of functions to a list of inputs, with each function
    being applied to its corresponding input element. It asserts that the number of inputs
    and functions are the same and raises an error if they are not.

    Parameters:
        input (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results from applying each function to its corresponding input.

    Raises:
        ValueError: If the number of provided inputs and functions are not the same.

    Example:
        >>> def add_one(x):
        ...     return x + 1
        >>> m_call([1, 2], [add_one, add_one])
        [2, 3]
    """
    input_ = to_list(input_=input_, flatten=flatten, dropna=dropna)
    func_ = to_list(func_)
    assert len(input_) == len(func_), "The number of inputs and functions must be the same."
    
    return to_list(
        [
            lcall(input_=inp, func_=f, flatten=flatten, dropna=dropna, **kwargs) 
            for f, inp in zip(func_, input_)
        ]
    )

async def amcall(
    input_: Union[Any, List[Any]], func_: Union[Callable, List[Callable]], 
    flatten: bool = True, dropna: bool = True, **kwargs
    ) -> List[Any]:
    """
    Asynchronously applies multiple functions to corresponding elements of the input.

    This asynchronous function maps a list of functions to a list of inputs, with each 
    function being applied to its corresponding input element asynchronously. It ensures 
    that the number of inputs and functions are the same, raising a `ValueError` if not.

    Parameters:
        input (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list containing the results from applying each function to its corresponding input.

    Raises:
        ValueError: If the number of inputs and functions do not match.

    Example:
        >>> async def async_add_one(x):
        ...     return x + 1
        >>> asyncio.run(am_call([1, 2], [async_add_one, async_add_one]))
        [2, 3]
    """
    input = to_list(input_=input_, flatten=flatten, dropna=dropna)
    func_ = to_list(func_)
    assert len(input) == len(func_), "Input and function counts must match."
    
    tasks = [
        alcall(input_=inp, func_=f, flatten=flatten, dropna=dropna, **kwargs) 
        for f, inp in zip(func_, input)
        ]
    
    out = await asyncio.gather(*tasks)
    return to_list(out, flat=True)

def ecall(
    input_: Union[Any, List[Any]], func_: Union[Callable, List[Callable]], 
    flatten: bool = True, dropna: bool = True, **kwargs
    ) -> List[Any]:
    """
    Applies each function in a list of functions to all elements in the input.

    This function expands the input to match the number of functions and then
    applies each function to the entire input. It is useful for applying a series
    of different transformations to the same input.

    Parameters:
        input (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Returns:
        List[Any]: A list of results after applying each function to the input.

    Example:
        >>> def square(x):
        ...     return x**2
        >>> e_call([1, 2, 3], [square])
        [[1], [4], [9]]
    """

    _f = lambda x, y: mcall(
        input_=create_copy(x, len(to_list(y))), func_=y, 
        flatten=False, dropna=dropna, **kwargs
        )
    return [_f(x=inp, y=func_) for inp in to_list(input_)]

async def aecall(
    input_: Union[Any, List[Any]], func_: Union[Callable, List[Callable]], 
    dropna: bool = True, **kwargs
    ) -> List[Any]:
    """
    Asynchronously applies each function in a list of functions to all elements in the input.

    This asynchronous function expands the input to match the number of functions and 
    then asynchronously applies each function to the entire input. It is useful for applying a series 
    of different asynchronous transformations to the same input.

    Parameters:
        input_ (Union[Any, List[Any]]): The input or list of inputs to be processed.

        func_ (Union[Callable, List[Callable]]): The function or list of functions to apply.

        flatten_dict (bool, optional): Whether to flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Whether the output list should be flattened. Defaults to True.

        dropna (bool, optional): Whether to drop None values during flattening. Defaults to True.

    Example:
        >>> async def async_square(x):
        ...     return x**2
        >>> asyncio.run(ae_call([1, 2, 3], [async_square]))
        [[1, 4, 9]]
    """
    async def _async_f(x, y):
        return await amcall(
            create_copy(x, len(to_list(y))), y, flatten=False, dropna=dropna, **kwargs
            )

    tasks = [_async_f(inp, func_) for inp in to_list(input_)]    
    return await asyncio.gather(*tasks)
