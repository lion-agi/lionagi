from collections import deque
from .sys_util import to_csv, make_filepath


class DataLogger:

    def __init__(self, dir_= None, log: list = None) -> None:
        self.dir_ = dir_
        self.log = deque(log) if log else deque()

    def __call__(self, entry):
        self.log.append(entry)

    def to_csv(self, dir_: str, filename: str, verbose: bool = True, timestamp: bool = True, dir_exist_ok=True, file_exist_ok=False):
        filepath = make_filepath(dir_=dir_, filename=filename, timestamp=timestamp, dir_exist_ok=dir_exist_ok)
        to_csv(list(self.log), filepath, file_exist_ok=file_exist_ok)
        n_logs = len(list(self.log))
        self.log = deque()
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")
            
    def set_dir(self, dir_: str):
        self.dir_ = dir_