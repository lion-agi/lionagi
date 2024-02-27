import copy
import os
from datetime import datetime
from hashlib import sha256
from typing import Any, Dict, List


class SysUtil:

    @staticmethod
    def change_dict_key(dict_: Dict[Any, Any], old_key: str, new_key: str) -> None:
        """Safely changes a key in a dictionary if the old key exists."""
        if old_key in dict_:
            dict_[new_key] = dict_.pop(old_key)

    @staticmethod
    def get_timestamp(separator: str = "_") -> str:
        """Returns a timestamp string with optional custom separators for ':' and '.'."""
        return (
            datetime.now().isoformat().replace(":", separator).replace(".", separator)
        )

    @staticmethod
    def is_schema(dict_: Dict[Any, Any], schema: Dict[Any, type]) -> bool:
        """Validates if the given dictionary matches the expected schema types."""
        return all(
            isinstance(dict_.get(key), expected_type)
            for key, expected_type in schema.items()
        )

    @staticmethod
    def create_copy(input_: Any, num: int = 1) -> Any | List[Any]:
        """Creates deep copies of the input, either as a single copy or a list of copies."""
        if num < 1:
            raise ValueError(f"'num' must be a positive integer: {num}")
        return (
            copy.deepcopy(input_)
            if num == 1
            else [copy.deepcopy(input_) for _ in range(num)]
        )

    @staticmethod
    def create_id(n: int = 32) -> str:
        """Generates a unique identifier based on the current time and random bytes."""
        current_time = datetime.now().isoformat().encode("utf-8")
        random_bytes = os.urandom(42)
        return sha256(current_time + random_bytes).hexdigest()[:n]

    @staticmethod
    def get_bins(input_: List[str], upper: Any = 2000) -> List[List[int]]:
        """Organizes indices of strings into bins based on a cumulative upper limit."""
        current = 0
        bins = []
        current_bin = []
        for idx, item in enumerate(input_):
            if current + len(item) < upper:
                current_bin.append(idx)
                current += len(item)
            else:
                bins.append(current_bin)
                current_bin = [idx]
                current = len(item)
        if current_bin:
            bins.append(current_bin)
        return bins
