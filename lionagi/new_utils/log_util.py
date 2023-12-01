from .sysutils import to_csv
import os
from datetime import datetime
import hashlib

class DataLogger:
    def __init__(self, dir_= None, log: list = None) -> None:
        self.dir_ = dir_
        self.log = log if log else []

    @staticmethod
    def generate_id() -> str:
        current_time = datetime.now().isoformat().encode('utf-8')
        random_bytes = os.urandom(16)
        return hashlib.sha256(current_time + random_bytes).hexdigest()[:16]
    
    @staticmethod
    def _get_timestamp() -> str:
        return datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")

    @staticmethod
    def _filepath(dir_: str, filename: str, timestamp: bool = True) -> str:
        os.makedirs(dir_, exist_ok=True)
        if timestamp:
            timestamp = DataLogger._get_timestamp()
            return f"{dir_}{timestamp}{filename}"
        else:
            return f"{dir_}{filename}"

    def __call__(self, entry):
        self.log.append(entry)

    def _to_csv(self, dir_: str, filename: str, verbose: bool, timestamp: bool):
        filepath = self._filepath(dir_=dir_, filename=filename, timestamp=timestamp)
        to_csv(self.log, filepath)
        n_logs = len(self.log)
        self.log = []
        if verbose:
            print(f"{n_logs} logs saved to {filepath}")