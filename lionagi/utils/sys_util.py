"""   
Copyright 2023 HaiyangLi <ocean@lionagi.ai>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import asyncio
import copy
import csv
import json
import os
import re
import tempfile
import time
import hashlib
import datetime
from collections.abc import Generator, Iterable, MutableMapping
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_'):
    for k, v in d.items():
        new_key = f'{parent_key}{sep}{k}' if parent_key else k
        if isinstance(v, MutableMapping):
            yield from _flatten_dict(v, new_key, sep=sep)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, MutableMapping):
                    yield from _flatten_dict(item, f'{new_key}{sep}{i}', sep=sep)
                else:
                    yield (f'{new_key}{sep}{i}', item)
        else:
            yield (new_key, v)
            
def _flatten_list(lst: List[Any], dropna: bool = True):
    for el in lst:
        if isinstance(el, list):
            yield from _flatten_list(el, dropna=dropna)
        else:
            if el is not None or not dropna:
                yield el

def to_list(input_: Union[Iterable, Any], flat_dict: bool = False, flat: bool = True, dropna: bool = True) -> List[Any]:
    if input_ is None or callable(input_):
        raise ValueError("Unsupported type: None or callable types are not convertable to a list.")
    
    try:
        if isinstance(input_, dict):
            if flat_dict:
                input_ = dict(_flatten_dict(input_))  # Flatten and convert to dictionary first
                return [{k: v} for k, v in input_.items()]
            out = [input_]
        elif isinstance(input_, Iterable) and not isinstance(input_, str):
            out = list(input_)
        else:
            out = [input_]
        
        if flat: # Flatten if necessary
            out = list(_flatten_list(out, dropna=dropna))

        return out
    except TypeError as e:
        raise ValueError(f"Unable to convert input to list. Error: {e}")
    
def str_to_num(str_: str, 
               upper_bound: Union[int, float] = 100, 
               lower_bound: Union[int, float] = 1, 
               type_: type = int, 
               precision: int = None) -> Union[int, float, str]:
    if upper_bound < lower_bound:
        raise ValueError("upper_bound must be greater than or equal to lower_bound")

    numbers = re.findall(r'-?\d+\.?\d*', str_)
    if not numbers:
        raise ValueError(f"No numeric values found in the string: {str_}")

    num_str = numbers[0]  # Take the first numeric string match
    
    # Corrected type conversion logic
    try:
        if type_ == float:
            num = float(num_str)
            if precision is not None:
                num = round(num, precision)
        else:
            num = int(float(num_str))  # Convert via float for strings like "123.45"

        if lower_bound <= num <= upper_bound:
            return num
        elif num < lower_bound:
            return f"Number {num} is less than the lower bound of {lower_bound}."
        elif num > upper_bound:
            return f"Number {num} is greater than the upper bound of {upper_bound}."
    except ValueError as e:
        raise ValueError(f"Error converting string to number: {e}")

def make_copy(input_: Any, n: int) -> Any:
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"n must be a positive integer: {n}")
    if n == 1: 
        return copy.deepcopy(input_)
    else:
        return [copy.deepcopy(input_) for _ in range(n)]

def to_temp(input_, flat_dict=False, flat=False, dropna=False):
    input_ = to_list(input_, flat_dict, flat, dropna)
    
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(input_, temp)
    except TypeError as e:
        temp.close()  # Ensure the file is closed before raising the error
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    temp.close()
    return temp

def to_csv(input_: List[Dict[str, Any]],
           filename: str,
           out: bool = False,
           file_exist_ok: bool = False) -> Optional[List[Dict[str, Any]]]:
    if not os.path.exists(os.path.dirname(filename)) and os.path.dirname(filename) != '':
        if file_exist_ok:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        else:
            raise FileNotFoundError(f"The directory {os.path.dirname(filename)} does not exist.")

    with open(filename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=input_[0].keys())
        writer.writeheader()
        writer.writerows(input_)

    return input_ if out else None

def hold_call(input_: Any, 
              func_: Callable, 
              hold: int = 5, 
              msg: Optional[str] = None, 
              ignore: bool = False, 
              **kwargs) -> Any:
    try:
        time.sleep(hold)
        return func_(*input_, **kwargs)
    except Exception as e:
        if msg:
            print(f"{msg} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore:
            raise

async def ahold_call(input_: Any, 
                     func_: Callable, 
                     hold: int = 5, 
                     msg: Optional[str] = None, 
                     ignore: bool = False, 
                     **kwargs) -> Any:
    try:
        if not asyncio.iscoroutinefunction(func_):
            raise TypeError(f"The function {func_} must be an asynchronous function.")
        await asyncio.sleep(hold)
        return await func_(*input_, **kwargs)
    except Exception as e:
        if msg:
            print(f"{msg} Error: {e}")
        else:
            print(f"An error occurred: {e}")
        if not ignore:
            raise

def l_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True) -> List[Any]:
    try:
        lst = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
        return [func_(i) for i in lst]
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

async def al_call(input_: Any, 
                  func_: Callable, 
                  flat_dict: bool = False, 
                  flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    try:
        lst = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
        tasks = [func_(i) for i in lst]
        return await asyncio.gather(*tasks)
    except Exception as e:
        raise ValueError(f"Given function cannot be applied to the input. Error: {e}")

def m_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool=True) -> List[Any]:
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "The number of inputs and functions must be the same."
    return to_list([l_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) 
                    for f, inp in zip(lst_func, lst_input)], flat=True)

async def am_call(input_: Any, func_: Callable, 
                  flat_dict: bool = False, flat: bool = False, 
                  dropna: bool=True) -> List[Any]:
    lst_input = to_list(input_, flat_dict=flat_dict, flat=flat, dropna=dropna)
    lst_func = to_list(func_)
    assert len(lst_input) == len(lst_func), "Input and function counts must match."
    
    tasks = [al_call(inp, f, flat_dict=flat_dict, flat=flat, dropna=dropna) 
             for f, inp in zip(lst_func, lst_input)]
    out = await asyncio.gather(*tasks)
    return to_list(out, flat=True)

def e_call(input_: Any, 
           func_: Callable, 
           flat_dict: bool = False, 
           flat: bool = False, 
           dropna: bool = True) -> List[Any]:

    f = lambda x, y: m_call(make_copy(x, len(to_list(y))), y, 
                            flat_dict=flat_dict, flat=flat, dropna=dropna)
    return to_list([f(inp, func_) for inp in to_list(input_)], flat=flat)

async def ae_call(input_: Any, func_: Callable, 
                  flat_dict: bool = False, flat: bool = False, 
                  dropna: bool = True) -> List[Any]:
    async def async_f(x, y):
        return await am_call(make_copy(x, len(to_list(y))), y, flat_dict=flat_dict, flat=flat, dropna=dropna)

    tasks = [async_f(inp, func_) for inp in to_list(input_)]
    return await asyncio.gather(*tasks)

def get_timestamp() -> str:
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")

def generate_id() -> str:
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(16)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:16]

def make_filepath(dir_: str, filename: str, timestamp: bool = True, dir_exist_ok=True) -> str:
    os.makedirs(dir_, exist_ok=dir_exist_ok)
    if timestamp:
        timestamp = get_timestamp()
        return f"{dir_}{timestamp}{filename}"
    else:
        return f"{dir_}{filename}"
    
def append_to_jsonl(data: Any, filename: str) -> None:
    json_string = json.dumps(data)
    with open(filename, "a") as f:
        f.write(json_string + "\n")
