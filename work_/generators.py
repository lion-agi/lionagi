from typing import (Any, Callable, Dict, Generator, Iterable, 
                    List, Optional, Tuple, Type, Union)

from dateutil import parser

def _task_id_generator() -> Generator[int, None, None]:
    """Generate an incremental sequence of integers starting from 0.

    Yields:
        The next integer in the sequence.

    Examples:
        gen = _task_id_generator()
        next(gen)  # Yields 0
        next(gen)  # Yields 1
    """
    task_id = 0
    while True:
        yield task_id
        task_id += 1
        
def _flatten_dict_generator(d: Dict, parent_key: str = '', sep: str = '_'
                            ) -> Generator[Tuple[str, Any], None, None]:
    for k, v in d.items():
        new_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, dict):
            yield from _flatten_dict_generator(v, new_key, sep=sep)
        else:
            yield new_key, v
            
def _flatten_iterable_generator(iterable: Iterable, max_depth: int = None) -> Generator[Any, None, None]:
    """
    A generator function that flattens a nested iterable up to a specified max_depth.

    Args:
        iterable: An iterable that may contain nested iterables.
        max_depth: An optional integer specifying the maximum depth to flatten. If None, flattens completely.

    Yields:
        The next flattened item from the iterable.

    Examples:
        >>> list(_flatten_iterable_generator([1, [2, [3, 4]], 5]))
        [1, 2, 3, 4, 5]
        >>> list(_flatten_iterable_generator([1, [2, [3, 4]], 5], max_depth=1))
        [1, 2, [3, 4], 5]
    """
    stack = [(iter(iterable), 0)]
    while stack:
        iterator, current_depth = stack.pop()
        for item in iterator:
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                if max_depth is None or current_depth < max_depth:
                    # Process nested iterables by adding them to the stack
                    stack.append((iter(item), current_depth + 1))
                else:
                    yield item
            else:
                yield item
            

def _dynamic_flatten_generator(obj: Any, parent_key: Tuple[str, ...] = (), 
                               sep: str = '_', max_depth: Union[int, None] = None, 
                               current_depth: int = 0
                               ) -> Generator[Tuple[str, Any], None, None]:
    """
    A generator function that recursively flattens a nested dictionary or list.

    Args:
        obj: The object to flatten, which can be a dictionary, list, or any other type.
        parent_key: A tuple representing the path to the current object.
        sep: The separator to use when joining keys.
        max_depth: The maximum depth to flatten. If None, flattens completely.
        current_depth: The current depth in the recursive call stack.

    Yields:
        Tuples of (key, value) where key is a string representing the path to the value.

    Examples:
        >>> list(_dynamic_flatten_generator({'a': {'b': 'c'}}))
        [('a_b', 'c')]
        >>> list(_dynamic_flatten_generator([1, [2, 3]], sep='/'))
        [('0', 1), ('1/0', 2), ('1/1', 3)]
    """
    if max_depth is not None and current_depth > max_depth:
        yield sep.join(parent_key), obj
        return

    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = parent_key + (k,)
            yield from _dynamic_flatten_generator(v, new_key, sep, 
                                                  max_depth, current_depth + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_key = parent_key + (str(i),)
            yield from _dynamic_flatten_generator(item, new_key, sep, 
                                                  max_depth, current_depth + 1)
    else:
        yield sep.join(parent_key), obj
        
def _flatten_list_generator(l: List, dropna: bool = True) -> Generator[Any, None, None]:
    for i in l:
        if isinstance(i, list):
            yield from _flatten_list_generator(i, dropna)
        elif i is not None or not dropna:
            yield i