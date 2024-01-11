import os
import copy
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Generator, List, Dict

def create_copy(input: Any, n: int) -> Any:
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"'n' must be a positive integer: {n}")
    return copy.deepcopy(input) if n == 1 else [copy.deepcopy(input) for _ in range(n)]

def create_id(n=32) -> str:
    current_time = datetime.now().isoformat().encode('utf-8')
    random_bytes = os.urandom(2048)
    return hashlib.sha256(current_time + random_bytes).hexdigest()[:n]

def get_timestamp() -> str:
    return datetime.now().isoformat().replace(":", "_").replace(".", "_")

def create_path(dir: str, filename: str, timestamp: bool = True, dir_exist_ok: bool = True, time_prefix=False) -> str:
    
    dir = dir + '/' if str(dir)[-1] != '/' else dir
    filename, ext = filename.split('.')
    os.makedirs(dir, exist_ok=dir_exist_ok)
    
    if timestamp:
        timestamp = get_timestamp()
        return f"{dir}{timestamp}_{filename}.{ext}" if time_prefix else f"{dir}{filename}_{timestamp}.{ext}"
    else:
        return f"{dir}{filename}"

def split_path(path: Path) -> tuple:
    folder_name = path.parent.name
    file_name = path.name
    return (folder_name, file_name)

def get_bins(input: List[str], upper: int = 7500) -> List[List[int]]:
    current = 0
    bins = []
    bin = []
    
    for idx, item in enumerate(input):
        if current + len(item) < upper:
            bin.append(idx)
            current += len(item)
        elif current + len(item) >= upper:
            bins.append(bin)
            bin = [idx]
            current = len(item)
        if idx == len(input) - 1 and len(bin) > 0:
            bins.append(bin)
    return bins

def change_dict_key(dict_, old_key, new_key):
    dict_[new_key] = dict_.pop(old_key)

def timestamp_to_datetime(timestamp: int) -> str:
    if isinstance(timestamp, str):
        try:
            timestamp = int(timestamp)
        except:
            return timestamp
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def is_schema(dict_: Dict, schema: Dict):
    for key, expected_type in schema.items():
        if not isinstance(dict_[key], expected_type):
            return False
    return True

def create_hash(data: str, algorithm: str = 'sha256') -> str:
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode())
    return hasher.hexdigest()

def task_id_generator() -> Generator[int, None, None]:
    task_id = 0
    while True:
        yield task_id
        task_id += 1
