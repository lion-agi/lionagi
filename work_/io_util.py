import csv
import io
import csv
import json
import os
import yaml
import tempfile
from collections.abc import Iterable
from typing import Any, Dict, List

def python_obj_to_csv(data: List[dict]) -> str:
    """Convert a list of dictionaries to a CSV formatted string.

    Args:
        data: A list of dictionaries where each dictionary represents a row of data.

    Returns:
        A string containing the CSV formatted data.

    Raises:
        ValueError: If the input is not a list of dictionaries.

    Examples:
        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> print(python_obj_to_csv(data))
        name,age
        Alice,30
        Bob,25
    """
    if not data:
        return ""

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise ValueError("Input must be a list of dictionaries.")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    return output.getvalue()


def to_csv(input: List[Dict[str, Any]],
           filepath: str,
           file_exist_ok: bool = False) -> None:
    """
    Writes a list of dictionaries to a CSV file.

    Args:
        input: A list of dictionaries where each dictionary represents a row in the CSV.
        filepath: The path to the CSV file to write to.
        file_exist_ok: If True, creates the directory for the file if it does not exist.

    Raises:
        FileNotFoundError: If the directory does not exist and file_exist_ok is False.

    Examples:
        >>> data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
        >>> to_csv(data, 'people.csv', file_exist_ok=True)
    """
    if not os.path.exists(os.path.dirname(filepath)) and os.path.dirname(filepath) != '':
        if file_exist_ok:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        else:
            raise FileNotFoundError(f"The directory {os.path.dirname(filepath)} does not exist.")

    with open(filepath, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=input[0].keys())
        writer.writeheader()
        for row in input:
            writer.writerow(row)

def append_to_jsonl(data: Any, filepath: str) -> None:
    """
    Appends a data entry to a JSON Lines file.

    Args:
        data: The data to append, which can be any JSON serializable object.
        filepath: The path to the JSON Lines file to append to.

    Examples:
        >>> append_to_jsonl({'name': 'Charlie', 'age': 35}, 'people.jsonl')
    """
    json_string = json.dumps(data)
    with open(filepath, "a") as f:
        f.write(json_string + "\n")
        
def to_temp(input: Any) -> tempfile.NamedTemporaryFile:
    """
    Writes the given input to a temporary file in JSON format.

    Args:
        input: The input data to write to the file. Can be a string or an iterable.

    Returns:
        A NamedTemporaryFile object representing the temporary file.

    Raises:
        TypeError: If the input data is not JSON serializable.

    Examples:
        >>> temp_file = to_temp("test string")
        >>> with open(temp_file.name, 'r') as file:
        ...     content = json.load(file)
        >>> content
        ["test string"]

        >>> temp_file = to_temp(["test", "string"])
        >>> with open(temp_file.name, 'r') as file:
        ...     content = json.load(file)
        >>> content
        ["test", "string"]
    """
    if isinstance(input, str):
        input = [input]
    elif isinstance(input, Iterable):
        input = [item for item in input if item is not None]

    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    try:
        json.dump(input, temp_file)
    except TypeError as e:
        temp_file.close()  # Ensuring file closure before raising error
        raise TypeError(f"Data provided is not JSON serializable: {e}")
    temp_file.close()
    return temp_file

import os
import csv
import json
from typing import List, Dict, Any

# Improved to_csv function with reduced memory usage
def to_csv(input: List[Dict[str, Any]]=None,
           filepath: str=None,
           file_exist_ok: bool = False) -> None:
    if not os.path.exists(os.path.dirname(filepath)) and os.path.dirname(filepath) != '':
        if file_exist_ok:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        else:
            raise FileNotFoundError(f"The directory {os.path.dirname(filepath)} does not exist.")

    with open(filepath, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=input[0].keys())
        writer.writeheader()
        for row in input:
            writer.writerow(row)

# Existing append_to_jsonl function
def append_to_jsonl(data: Any, filepath: str) -> None:
    json_string = json.dumps(data)
    with open(filepath, "a") as f:
        f.write(json_string + "\n")

# New read_csv function
def read_csv(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, 'r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)

# New read_jsonl function
def read_jsonl(filepath: str) -> List[Any]:
    with open(filepath, 'r') as f:
        return [json.loads(line) for line in f]

# New write_json function
def write_json(data: List[Dict[str, Any]], filepath: str) -> None:
    with open(filepath, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# New read_json function
def read_json(filepath: str) -> Any:
    with open(filepath, 'r') as json_file:
        return json.load(json_file)

# New merge_csv_files function
def merge_csv_files(filepaths: List[str], output_filepath: str) -> None:
    merged_data = []
    fieldnames = set()
    for filepath in filepaths:
        with open(filepath, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            fieldnames.update(reader.fieldnames)
            for row in reader:
                merged_data.append(row)
    fieldnames = list(fieldnames)
    with open(output_filepath, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged_data)
        
def json_to_yaml(json_data: str) -> str:
    """Convert JSON formatted string to a YAML formatted string.

    Args:
        json_data: A string formatted as JSON.

    Returns:
        A string formatted as YAML.

    Examples:
        >>> json_to_yaml('{"name": "John", "age": 30}')
        'name: John\\nage: 30\\n'
    """
    parsed_json = json.loads(json_data)
    return yaml.dump(parsed_json, sort_keys=False)

def csv_to_json(csv_data: str) -> List[dict]:
    """Convert CSV formatted string to a list of dictionaries.

    Args:
        csv_data: A string formatted as CSV.

    Returns:
        A list of dictionaries representing the rows of the CSV.

    Examples:
        >>> csv_to_json("name,age\\nJohn,30")
        [{'name': 'John', 'age': '30'}]
    """
    reader = csv.DictReader(csv_data.splitlines())
    return [row for row in reader]