from collections import deque
from typing import Optional
from lionagi.utils import create_path, to_csv


class DataLogger:

    def __init__(self, dir= None, log: list = None) -> None:
    
        self.dir = dir
        self.log = deque(log) if log else deque()

    def __call__(self, entry):    
        self.log.append(entry)

    def to_csv(self, filename: str, dir: Optional[str] = None, verbose: bool = True, 
               timestamp: bool = True, dir_exist_ok: bool = True, file_exist_ok: bool = False) -> None:   
        dir = dir or self.dir
        filepath = create_path(
            dir=dir, filename=filename, timestamp=timestamp, dir_exist_ok=dir_exist_ok)
        to_csv(list(self.log), filepath, file_exist_ok=file_exist_ok)
        n_logs = len(list(self.log))
        self.log = deque()
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")
            
    def set_dir(self, dir: str) -> None:
        self.dir = dir
    
    def to_jsonl(self, **kwargs):
        ...
        