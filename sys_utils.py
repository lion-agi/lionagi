from pathlib import Path
from collections.abc import Iterable, MutableMapping
from typing import Any, Callable, List
import copy
from Logger import datalog
import math
import time
import pandas as pd


def _flatten_dict(dictionary, parent_key=False, separator='_'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(_flatten_dict(value, new_key, separator).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                items.extend(_flatten_dict({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)

def _flatten_list(xs):
    """
    A private generator function that takes in a list , 
    checks if the element in the list is also a list then recurses on that list
    if not, it yields the element.
    
    Args:
    xs (list): The list to flatten 
    
    Yields:
    Individual elements from the list
    """
    for x in xs:
        if isinstance(x, List):
            yield from _flatten_list(x)
        else:
            yield x

def flatten_list(_input):
    """
    The main function that calls the '_flatten_list' function to flatten any 
    input list and then filters out any None values.
    
    Args:
    _input (list): The list to flatten
    
    Returns:
    list: A new flattened list with no 'None' values
    """
    return [i for i in _flatten_list(_input) if i is not None]


def to_list(_input: Any, flatten_dict=False) -> List[Any]:
    """
    Function to convert the input into a list. If the input is Iterable (e.g. set, tuple),
    each item in the iterable will be an element in the list. If the input is a dictionary,
    a list of tuples (key, value) will be returned. However, when flatten_dict is True, 
    a flattened version of dictionary will be used. If the input is a regular non-iterable 
    object, a single-item list will be returned. 

    Parameters:
        _input : Any
            Any type of input that needs to be converted to list.
        flatten_dict : bool, default=False
            If True, returns a list containing the flattened version of 
            the dictionary (key, value) pairs. Otherwise, returns the 
            original (key, value) pairs of dictionary as list.
    Returns:
        List[Any]
            List representation of the input.
    Raises:
        ValueError: If input can't be converted to list.
    """
    try:
        if isinstance(_input, Iterable):
            if isinstance(_input, dict):
                if flatten_dict:
                    return [_flatten_dict(_input).items()]
                else: 
                    return [(_input).items()]
            elif isinstance(_input, str):
                return [_input]
            else:
                return [i for i in _input.__iter__()]
        else:
            return [_input]
    except Exception as e:
        raise ValueError(f"Given input cannot be converted to list. Error: {e}")

def _create_copies(_input: Any, n: int) -> List[Any]:
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

def l_return(_input: Any, _func: Any, flatten_dict: bool = False) -> List[Any]:
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
    return [l_return(inp, func) for func, inp in zip(_func, _input)]

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
    f = lambda x, y: m_return(_create_copies(x,len(to_list(y))), y)
    return [f(inp, _func) for inp in to_list(_input, flatten_dict=flatten_dict)]

       
def _get_files(_dir, _ext, flatten):
    """
    Fetches the files from the directory with the given extensions. 
    
    The function takes in a directory path, extensions, and a boolean value for flatten. If flatten is True, 
    it flattens the returned list otherwise returns as is. It first converts the extensions to a list, checks if any 
    are provided. Depending on the flatten value, it fetches all the files with the given _ext from the _dir directory, 
    and then returns the list of files. The path of each file is converted to a pathlib.Path object.
    
    Args:
        _dir (str/Pathlib.Path): The directory path where to look for files.
        _ext (list/str): The extensions of the files to include. 
        flatten (bool): If True, the returned list of files will be flattened.
        
    Returns:
        list: A list of pathlib.Path objects representing the files in the directory with the given extensions.
    """
    rtn = ''
    if len(to_list(_ext)) > 0:
        f1 = lambda x: [file for file in [x.glob('**/*' + ext) for ext in _ext]]
        f2 = lambda x: [Path(file) for file in x]
        rtn = l_return(l_return(_dir, f1)[0], f2)
        return flatten_list(rtn) if flatten else rtn


def _get_all_files(_dir, _ext, flatten_inside=True, faltten_outside=False):
    """
    Description: This function retrieves all files with the given extension from a particular directory. Results can be flatted or left nested depending on the boolean flags.

    Args:
    _dir (str): File directory.
    _ext (str): File extensions to get.
    flatten_inside (bool): If True, flattens the inner lists.
    faltten_outside (bool): If True, flattens all lists outside inner ones.

    Returns:
    list: A list of all files with the given extensions in the directory.
    """
    a = l_return(_dir, lambda x: _get_files(x, _ext, flatten=flatten_inside))
    return flatten_list(a) if faltten_outside else a

def _read_as_text(filepath, clean):
    """
    Description: Opens a file and reads its content as a text file. Option to clean file content by replacing certain characters.

    Args:
    filepath (str): Path to the file to be read.
    clean (bool): If True, cleans text by replacing '\\','\\\n','\\\t','  ','\'' characters with a space.

    Returns:
    string: File content as text.
    """
    with open(filepath, 'r') as f:
        if clean:
            a = f.read().replace('\\', ' ')
            a = a.replace('\\\n',' ')
            a = a.replace('\\\t',' ')
            a = a.replace('  ',' ')
            a = a.replace('\'',' ')
            return a
        else:
            return f.read()
        
def dir_to_dict(_dir, _ext, read_as=_read_as_text, flatten=True, clean=True, to_csv=False, 
                output_dir='data/logs/sources/', filename='autogen_py.csv', verbose=True, timestamp=True):
    """
    Description: Reads all files of required extension from source folders into a list of dictionaries.

    Args:
    _dir (str): Directory path.
    _ext (str): File extensions to read.
    read_as (function): Function to read file content, default is _read_as_text.
    flatten (bool): If True, returns a flattened list, else a nested list.
    clean (bool): If True, cleans file content as defined in the _read_as_text function.
    to_csv (bool): If True, logs the output to a csv file.
    output_dir (str): Output directory for csv file, if to_csv=True.
    filename (str): Name of output csv file, if to_csv=True.
    verbose (bool): If True, prints verbose logs.
    timestamp (bool): If True, adds timestamp to logs.

    Returns:
    list: List of dictionary objects with keys - 'folder', 'file', 'content'.
    """
    _sources = _get_all_files(_dir, _ext, faltten_outside=flatten)    
    def _split(_path):
        _folder_name =  str(_path).split('/')[-2]
        _file_name = str(_path).split('/')[-1]
        return (_folder_name, _file_name)
    def _to_dict(_path):
        _folder, _file = _split(_path)
        out = {
            "folder": _folder,
            "file": _file,
            "content": read_as(_path, clean=clean)}
        if len(out['content']) > 0:
            return out
    if to_csv:
        datalog.log = l_return(_sources, _to_dict)
        datalog.to_csv(dir=output_dir, filename=filename, verbose=verbose, timestamp=timestamp)
    if flatten:
        return l_return(_sources, _to_dict)
    else:
        return l_return(_sources, lambda x: l_return(x, _to_dict))


def _split_text(_text, chunk_size, overlap, threshold):
    """
    Splits a text string into multiple chunks of a specified size with optional overlap. 
    
    Args:
        _text (str): The text to be chunked.
        chunk_size (int, optional): The size of the chunks. Defaults to 2000.
        overlap (float, optional): The amount of desired overlap between chunks. Defaults to 0.2.
        threshold (int, optional): The minimum size for the last chunk. Defaults to 200.

    Returns:
        list: A list of text chunks from the input string.
        
    Raises:
        TypeError: When non-string input is provided and cannot be cast to a string.
        ValueError: When an error occurs during the chunking process.
    """
    if not isinstance(_text, str):
        try: 
            _text = str(_text)
        except Exception as e:
            raise TypeError(f"Expected type str, got {type(_text)}.{e}")
    try:
        chunks = []
        num_chunks = math.ceil(len(_text) / chunk_size)
        overlap_size = int(chunk_size * overlap / 2)
        
        if num_chunks == 1:
            return [_text]
        
        elif num_chunks == 2:
            chunks.append(_text[:chunk_size+overlap_size])
            if len(_text) - chunk_size > threshold:
                chunks.append(_text[chunk_size-overlap_size:])
                return chunks
            else:
                return [_text]
            
        elif num_chunks > 2:
            chunks.append(_text[:chunk_size+overlap_size])
            for i in range(1, num_chunks-1):
                chunks.append(_text[(chunk_size*i-overlap_size):(chunk_size*(i+1) + overlap_size)])
            if len(_text) - (chunk_size*(num_chunks-1)) > threshold:
                chunks.append(_text[(chunk_size*(num_chunks-1)-overlap_size):])
            else:
                chunks[-1] += _text[-(len(_text) - (chunk_size*(num_chunks-1))):]
            return chunks
    except Exception as e:
        raise ValueError(f"Error splitting text into chunks. {e}")
    
    
def get_chunks(_dict,chunk_size=2000, overlap=0.2, threshold=200):
    """
    Splits the content of a dictionary into multiple chunks of a specified size with optional overlap. 
    
    Args:
        _dict (dict): The dictionary who's 'content' key needs to be chunked.
        chunk_size (int, optional): The size of the chunks. Defaults to 2000.
        overlap (float, optional): The amount of desired overlap between chunks. Defaults to 0.2.
        threshold (int, optional): The minimum size for the last chunk. Defaults to 200.

    Returns:
        list: A list of dictionaries, each containing a separate chunk and its corresponding details.
    """
    content = _dict['content']
    splited_chunks = _split_text(content, chunk_size=chunk_size, overlap=overlap, threshold=threshold)
    out = []
    if len(splited_chunks) > 1:
        for i, j in enumerate(splited_chunks):
            out.append({'folder':_dict['folder'],'file': _dict['file'], 'chunk_id': i, 'content': j})
    elif len(splited_chunks) == 1:
        out.append({'folder':_dict['folder'],'file': _dict['file'], 'chunk_id': 0, 'content': splited_chunks[0]})
    return out

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
        
def to_csv(ouputs, filename):
    """
    Converts a list of objects to a pandas DataFrame and writes it to a csv file.
    
    Args:
        outputs (list): List of objects to be converted to a DataFrame.
        filename (str): Name of the csv file to write the DataFrame to.

    Returns:
        None
    """
    df = pd.DataFrame([i for i in ouputs if i is not None])
    df.reset_index(drop=True, inplace=True)
    df.to_csv(filename)

