import csv
import json
import os
import tempfile
from typing import Any, Dict, List
from .type_util import to_list


def to_temp(input: Any, 
            flatten_dict: bool = False, 
            flat: bool = False, 
            dropna: bool = False):
    """
    Converts input to a list and writes it to a temporary file in JSON format, with flattening options.

    This function serializes data to a temporary JSON file, useful for transient storage or testing. 
    It includes options to flatten the input if it contains dictionaries or lists.

    Parameters:
        input (Any): The data to be converted and written to a file.

        flatten_dict (bool, optional): Flatten dictionaries in the input. Defaults to False.

        flat (bool, optional): Flatten lists in the input. Defaults to False.

        dropna (bool, optional): Exclude 'None' values during flattening. Defaults to False.

    Raises:
        TypeError: If the input is not JSON serializable.

    Example:
        >>> temp_file = to_temp({'a': 1, 'b': [2, 3]}, flatten_dict=True)
        >>> temp_file.name  # Doctest: +ELLIPSIS
        '/var/folders/.../tmp...'
    """
    input = to_list(input, flatten_dict, flat, dropna)
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(input, temp_file)
    except TypeError as e:
        temp_file.close()  # Ensuring file closure before raising error
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    temp_file.close()
    return temp_file

def to_csv(input: List[Dict[str, Any]]=None,
           filepath: str=None,
           file_exist_ok: bool = False) -> None:
    """
    Writes a list of dictionaries to a CSV file, with dictionary keys as headers.

    This function writes a list of dictionaries to a CSV file. It checks if the file exists 
    and handles file creation based on the 'file_exist_ok' flag.

    Parameters:
        input (List[Dict[str, Any]]): Data to write to the CSV file.

        filepath (str): Path of the output CSV file.

        file_exist_ok (bool, optional): Create the file if it doesn't exist. Defaults to False.

    Raises:
        FileExistsError: If the file already exists and 'file_exist_ok' is False.

    Example:
        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> to_csv(data, 'people.csv')
    """

    if not os.path.exists(os.path.dirname(filepath)) and os.path.dirname(filepath) != '':
        if file_exist_ok:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        else:
            raise FileNotFoundError(f"The directory {os.path.dirname(filepath)} does not exist.")

    with open(filepath, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=input[0].keys())
        writer.writeheader()
        writer.writerows(input)


def append_to_jsonl(data: Any, filepath: str) -> None:
    """
    Appends data to a JSON lines (jsonl) file.

    Serializes given data to a JSON-formatted string and appends it to a jsonl file. 
    Useful for logging or data collection where entries are added incrementally.

    Parameters:
        data (Any): Data to be serialized and appended.

        filepath (str): Path to the jsonl file.

    Example:
        >>> append_to_jsonl({"key": "value"}, "data.jsonl")
        # Appends {"key": "value"} to 'data.jsonl'
    """
    json_string = json.dumps(data)
    with open(filepath, "a") as f:
        f.write(json_string + "\n")
        