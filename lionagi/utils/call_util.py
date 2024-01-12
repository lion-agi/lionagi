from functools import lru_cache
import asyncio
import time
from typing import Any, Callable, List, Optional, Union
from .sys_util import create_copy, to_list


def hcall(input: Any, func: Callable, sleep: int = 0.1,
          message: Optional[str] = None, ignore_error: bool = False, **kwargs) -> Any:
    """
    Calls a function with an optional delay and error handling.

    Args:
        input (Any): The input to be passed to the function.
        func (Callable): The function to be called.
        sleep (int, optional): Delay before the function call in seconds.
        message (Optional[str], optional): Custom message for error handling.
        ignore_error (bool, optional): If False, re-raises the caught exception.

    Returns:
        Any: The result of the function call.
    """
    try:
        time.sleep(sleep)
        return func(input, **kwargs)
    except Exception as e:
        err_msg = f"{message} Error: {e}" if message else f"An error occurred: {e}"
        print(err_msg)
        if not ignore_error:
            raise

async def ahcall(input_: Any, func: Callable, sleep: int = 0.1,
                 message: Optional[str] = None, ignore_error: bool = False, **kwargs) -> Any:
    """
    Asynchronously calls a function with an optional delay and error handling.

    Args:
        input_ (Any): The input to be passed to the asynchronous function.
        func (Callable): The asynchronous function to be called.
        sleep (int, optional): Delay before the function call in seconds.
        message (Optional[str], optional): Custom message for error handling.
        ignore_error (bool, optional): If False, re-raises the caught exception.

    Returns:
        Any: The result of the function call.
    """
    try:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"The function {func.__name__} must be asynchronous.")
        await asyncio.sleep(sleep)
        return await func(input_, **kwargs)
    except Exception as e:
        err_msg = f"{message} Error: {e}" if message else f"An error occurred: {e}"
        print(err_msg)
        if not ignore_error:
            raise

def lcall(input_: Any, func_: Callable, flatten: bool = False,
          dropna: bool = False, **kwargs) -> List[Any]:
    """
    Applies a function to each element in a list, with options for flattening and dropping NAs.

    Args:
        input_ (Any): The input, potentially a list, to process.
        func_ (Callable): The function to be applied to each element.
        flatten (bool, optional): If True, flattens the input.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list containing the results of the function call on each element.
    """
    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        return [func_(i, **kwargs) for i in lst]
    except Exception as e:
        raise ValueError(f"Function {func_.__name__} cannot be applied: {e}")

async def alcall(input_: Any, func_: Callable, flatten: bool = False,
                 dropna: bool = True, **kwargs) -> List[Any]:
    """
    Asynchronously applies a function to each element in a list, with options for flattening and dropping NAs.

    Args:
        input_ (Any): The input, potentially a list, to process.
        func_ (Callable): The asynchronous function to be applied to each element.
        flatten (bool, optional): If True, flattens the input.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list containing the results of the asynchronous function call on each element.
    """
    try:
        lst = to_list(input_=input_, flatten=flatten, dropna=dropna)
        tasks = [func_(i, **kwargs) for i in lst]
        return await asyncio.gather(*tasks)
    except Exception as e:
        raise ValueError(f"Function {func_.__name__} cannot be applied: {e}")


def mcall(input_: Union[Any, List[Any]], 
          func_: Union[Callable, List[Callable]], 
          flatten: bool = True, 
          dropna: bool = True, **kwargs) -> List[Any]:
    """
    Applies multiple functions to corresponding inputs, potentially in a list format.

    Args:
        input_ (Union[Any, List[Any]]): Input or list of inputs.
        func_ (Union[Callable, List[Callable]]): Function or list of functions.
        flatten (bool, optional): If True, flattens the input list.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments for the function calls.

    Returns:
        List[Any]: List of results from applying each function to its corresponding input.
    """
    inputs = to_list(input_=input_, flatten=flatten, dropna=dropna)
    funcs = to_list(func_)
    if len(inputs) != len(funcs):
        raise ValueError("The number of inputs and functions must be the same.")

    return [lcall(input_=inp, func_=f, flatten=False, dropna=dropna, **kwargs)
            for inp, f in zip(inputs, funcs)]
    
async def amcall(input_: Union[Any, List[Any]], 
                 func_: Union[Callable, List[Callable]], 
                 flatten: bool = True, 
                 dropna: bool = True, **kwargs) -> List[Any]:
    """
    Asynchronously applies multiple functions to corresponding inputs, potentially in a list format.

    Args:
        input_ (Union[Any, List[Any]]): Input or list of inputs.
        func_ (Union[Callable, List[Callable]]): Asynchronous function or list of functions.
        flatten (bool, optional): If True, flattens the input list.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments for the function calls.

    Returns:
        List[Any]: List of results from applying each function to its corresponding input.
    """
    inputs = to_list(input_=input_, flatten=flatten, dropna=dropna)
    funcs = to_list(func_)
    if len(inputs) != len(funcs):
        raise ValueError("Input and function counts must match.")

    tasks = [alcall(input_=inp, func_=f, flatten=False, dropna=dropna, **kwargs)
             for inp, f in zip(inputs, funcs)]
    return await asyncio.gather(*tasks)

def ecall(input_: Union[Any, List[Any]], 
          func_: Union[Callable, List[Callable]], 
          dropna: bool = True, **kwargs) -> List[Any]:
    """
    Applies a list of functions to each input element, creating expanded combinations.

    Args:
        input_ (Union[Any, List[Any]]): Input or list of inputs.
        func_ (Union[Callable, List[Callable]]): Function or list of functions.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments for the function calls.

    Returns:
        List[Any]: List of results from applying each function to each input.
    """
    inputs = to_list(input_)
    return [mcall(input_=create_copy(inp, len(funcs)), func_=funcs, 
                  flatten=False, dropna=dropna, **kwargs) 
            for inp in inputs for funcs in to_list(func_)]

async def aecall(input_: Union[Any, List[Any]], 
                 func_: Union[Callable, List[Callable]], 
                 dropna: bool = True, **kwargs) -> List[Any]:
    """
    Asynchronously applies a list of functions to each input element, creating expanded combinations.

    Args:
        input_ (Union[Any, List[Any]]): Input or list of inputs.
        func_ (Union[Callable, List[Callable]]): Asynchronous function or list of functions.
        dropna (bool, optional): If True, drops None values from the list.
        **kwargs: Additional keyword arguments for the function calls.

    Returns:
        List[Any]: List of results from applying each function to each input.
    """
    inputs = to_list(input_)
    tasks = [amcall(create_copy(inp, len(funcs)), funcs, 
                    flatten=False, dropna=dropna, **kwargs) 
             for inp in inputs for funcs in to_list(func_)]
    return await asyncio.gather(*tasks)

async def parallel_call_limited(funcs: List[Callable[..., Any]], 
                                inputs: List[Any], 
                                max_concurrent: int = 5) -> List[Any]:
    """
    Execute multiple function calls in parallel with a specified limit on concurrency.

    This function uses an asynchronous semaphore to limit the number of concurrent function 
    executions, allowing for efficient parallel processing without overloading resources.

    Args:
        funcs (List[Callable[..., Any]]): List of functions to be executed.
        inputs (List[Any]): List of inputs, each corresponding to each function.
        max_concurrent (int): Maximum number of concurrent executions.

    Returns:
        List[Any]: List of results from each function call.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def semaphore_wrapper(func, inp):
        async with semaphore:
            return await func(inp)

    tasks = [semaphore_wrapper(func, inp) for func, inp in zip(funcs, inputs)]
    return await asyncio.gather(*tasks)

def conditional_call(func: Callable[..., Any], 
                     condition: Callable[..., bool], 
                     input_: Any, **kwargs) -> Optional[Any]:
    """
    Execute a function only if a specified condition is met.

    This function allows conditional execution of another function, where the condition
    is evaluated before the function execution. If the condition returns True, the function
    is executed; otherwise, None is returned.

    Args:
        func (Callable[..., Any]): The function to be executed.
        condition (Callable[..., bool]): The condition to be evaluated.
        input_ (Any): Input to the function and condition.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        Optional[Any]: The result of the function call if condition is met, otherwise None.
    """
    if condition(input_):
        return func(input_, **kwargs)
    return None

def dynamic_chain(input_: Any, funcs: List[Callable[..., Any]], **kwargs) -> Any:
    """
    Chain multiple functions dynamically, where the output of one function becomes the input of the next.

    This function allows for the creation of a dynamic function chain. Each function in the
    chain is applied sequentially, with the output of one function becoming the input for the next.

    Args:
        input_ (Any): The initial input to the chain.
        funcs (List[Callable[..., Any]]): List of functions to chain.
        **kwargs: Additional keyword arguments to pass to each function in the chain.

    Returns:
        Any: The final output after all functions are applied.
    """
    result = input_
    for func in funcs:
        result = func(result, **kwargs)
    return result

def call_with_timeout(func: Callable[..., Any], timeout: int, *args, **kwargs) -> Any:
    """
    Executes a function call with a specified timeout. If the function execution exceeds 
    the given timeout, a TimeoutError is raised.

    Args:
        func (Callable[..., Any]): The function to be executed.
        timeout (int): Timeout in seconds after which the function call will be aborted.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call if completed within the timeout, 
        otherwise raises TimeoutError.
    """
    loop = asyncio.get_event_loop()
    try:
        return loop.run_until_complete(asyncio.wait_for(func(*args, **kwargs), timeout))
    except asyncio.TimeoutError:
        raise TimeoutError(f"Function call timed out after {timeout} seconds.")

def call_with_retry(func: Callable[..., Any], retries: int = 3, delay: int = 2, *args, **kwargs) -> Any:
    """
    Retries a function call a specified number of times with a delay between attempts. If all attempts fail, 
    the function raises the last caught exception.

    Args:
        func (Callable[..., Any]): The function to be executed.
        retries (int): Number of times to retry the function call.
        delay (int): Delay in seconds between retries.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call if successful within the retry limit, 
        otherwise raises the last caught exception.
    """
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries - 1:
                time.sleep(delay)
    raise last_exception

def call_with_default(func: Callable[..., Any], default: Any, *args, **kwargs) -> Any:
    """
    Executes a function call and returns a specified default value if an exception occurs during the function execution.

    Args:
        func (Callable[..., Any]): The function to be executed.
        default (Any): Default value to return in case of an exception.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function call if successful, otherwise the specified default value.
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return default

def batch_call(func: Callable[..., Any], 
               inputs: List[Any], 
               batch_size: int, 
               **kwargs) -> List[Any]:
    """
    Processes a list of inputs in batches, applying a function to each item in a batch.

    Args:
        func (Callable[..., Any]): The function to be applied to each item.
        inputs (List[Any]): The list of inputs to be processed.
        batch_size (int): The number of items to include in each batch.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results from applying the function to each item in the batches.
    """
    results = []
    for i in range(0, len(inputs), batch_size):
        batch = inputs[i:i + batch_size]
        results.extend([func(item, **kwargs) for item in batch])
    return results

@lru_cache(maxsize=128)
def cached_call(func: Callable[..., Any], *args, **kwargs) -> Any:
    """
    Caches the results of function calls to reduce redundant computations.

    This function uses a least recently used (LRU) cache to store the results of function calls,
    improving efficiency for functions with expensive computations.

    Args:
        func (Callable[..., Any]): The function whose results are to be cached.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The cached result of the function call.
    """
    return func(*args, **kwargs)

async def async_iterative_call(func: Callable[..., Any], 
                               inputs: List[Any], 
                               **kwargs) -> List[Any]:
    """
    Asynchronously iterates over a list of inputs, applying a function to each item.

    Args:
        func (Callable[..., Any]): The asynchronous function to be applied.
        inputs (List[Any]): The list of inputs to be processed.
        **kwargs: Additional keyword arguments to pass to the function.

    Returns:
        List[Any]: A list of results from the asynchronous application of the function.
    """
    return await asyncio.gather(*(func(item, **kwargs) for item in inputs))

def call_with_pre_post_processing(func: Callable[..., Any], 
                                  preprocess: Callable[..., Any], 
                                  postprocess: Callable[..., Any], 
                                  *args, **kwargs) -> Any:
    """
    Executes a function with defined preprocessing and postprocessing steps.

    Args:
        func (Callable[..., Any]): The main function to execute.
        preprocess (Callable[..., Any]): A function to preprocess each argument.
        postprocess (Callable[..., Any]): A function to postprocess the result.
        *args: Positional arguments to pass to the main function.
        **kwargs: Keyword arguments to pass to the main function.

    Returns:
        Any: The result of the main function after preprocessing and postprocessing.
    """
    preprocessed_args = [preprocess(arg) for arg in args]
    preprocessed_kwargs = {k: preprocess(v) for k, v in kwargs.items()}
    result = func(*preprocessed_args, **preprocessed_kwargs)
    return postprocess(result)
