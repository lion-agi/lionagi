import ast
import copy as _copy
import importlib
import importlib.metadata
import importlib.util
import os
import random
import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal, TypeVar

T = TypeVar("T")


def unique_hash(n: int = 32) -> str:
    """unique random hash"""
    current_time = datetime.now().isoformat().encode("utf-8")
    random_bytes = os.urandom(42)
    return sha256(current_time + random_bytes).hexdigest()[:n]


def is_same_dtype(
    input_: list | dict, dtype: type | None = None, return_dtype: bool = False
) -> bool | tuple[bool, type]:
    """Check if all elements in input have the same data type."""
    if not input_:
        return True if not return_dtype else (True, None)

    iterable = input_.values() if isinstance(input_, Mapping) else input_
    first_element_type = type(next(iter(iterable), None))

    dtype = dtype or first_element_type
    result = all(isinstance(element, dtype) for element in iterable)
    return (result, dtype) if return_dtype else result


def insert_random_hyphens(
    s: str,
    num_hyphens: int = 1,
    start_index: int | None = None,
    end_index: int | None = None,
) -> str:
    """Insert random hyphens into a string."""
    if len(s) < 2:
        return s

    prefix = s[:start_index] if start_index else ""
    postfix = s[end_index:] if end_index else ""
    modifiable_part = s[start_index:end_index] if start_index else s

    positions = random.sample(range(len(modifiable_part)), num_hyphens)
    positions.sort()

    for pos in reversed(positions):
        modifiable_part = modifiable_part[:pos] + "-" + modifiable_part[pos:]

    return prefix + modifiable_part + postfix


def get_file_classes(file_path):
    with open(file_path) as file:
        file_content = file.read()

    tree = ast.parse(file_content)

    class_file_dict = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_file_dict[node.name] = file_path

    return class_file_dict


def get_class_file_registry(folder_path, pattern_list):
    class_file_registry = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                if any(pattern in root for pattern in pattern_list):
                    class_file_dict = get_file_classes(
                        os.path.join(root, file)
                    )
                    class_file_registry.update(class_file_dict)
    return class_file_registry


def get_class_objects(file_path):
    class_objects = {}
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for class_name in dir(module):
        obj = getattr(module, class_name)
        if isinstance(obj, type):
            class_objects[class_name] = obj

    return class_objects


def time(
    *,
    tz: timezone = timezone.utc,
    type_: Literal["timestamp", "datetime", "iso", "custom"] = "timestamp",
    sep: str | None = "T",
    timespec: str | None = "auto",
    custom_format: str | None = None,
    custom_sep: str | None = None,
) -> float | str | datetime:
    """
    Get current time in various formats.

    Args:
        tz: Timezone for the time (default: utc).
        type_: Type of time to return (default: "timestamp").
            Options: "timestamp", "datetime", "iso", "custom".
        sep: Separator for ISO format (default: "T").
        timespec: Timespec for ISO format (default: "auto").
        custom_format: Custom strftime format string for
            type_="custom".
        custom_sep: Custom separator for type_="custom",
            replaces "-", ":", ".".

    Returns:
        Current time in the specified format.

    Raises:
        ValueError: If an invalid type_ is provided or if custom_format
            is not provided when type_="custom".
    """
    now = datetime.now(tz=tz)

    if type_ == "iso":
        return now.isoformat(sep=sep, timespec=timespec)
    elif type_ == "timestamp":
        return now.timestamp()
    elif type_ == "datetime":
        return now
    elif type_ == "custom":
        if not custom_format:
            raise ValueError(
                "custom_format must be provided when type_='custom'"
            )
        formatted_time = now.strftime(custom_format)
        if custom_sep is not None:
            for old_sep in ("-", ":", "."):
                formatted_time = formatted_time.replace(old_sep, custom_sep)
        return formatted_time

    raise ValueError(
        f"Invalid value <{type_}> for `type_`, must be"
        " one of 'timestamp', 'datetime', 'iso', or 'custom'."
    )


def copy(obj: T, /, *, deep: bool = True, num: int = 1) -> T | list[T]:
    """
    Create one or more copies of an object.

    Args:
        obj: The object to be copied.
        deep: If True, create a deep copy. Otherwise, create a shallow
            copy.
        num: The number of copies to create.

    Returns:
        A single copy if num is 1, otherwise a list of copies.

    Raises:
        ValueError: If num is less than 1.
    """
    if num < 1:
        raise ValueError("Number of copies must be at least 1")

    copy_func = _copy.deepcopy if deep else _copy.copy
    return [copy_func(obj) for _ in range(num)] if num > 1 else copy_func(obj)


def run_pip_command(
    args: Sequence[str],
) -> subprocess.CompletedProcess[bytes]:
    """Run a pip command."""
    return subprocess.run(
        [sys.executable, "-m", "pip"] + list(args),
        check=True,
        capture_output=True,
    )


def format_deprecation_msg(
    deprecated_name: str,
    type_: str,
    deprecated_version: str,
    removal_version: str,
    replacement: str | Literal["python"] | None = None,
    additional_msg: str | None = None,
) -> None:

    msg = (
        f"{type_}: <{deprecated_name}> is deprecated since "
        f"<{deprecated_version}> and will be removed in {removal_version}."
    )
    if replacement is None:
        msg += " No replacement is available."
    elif replacement == "python":
        msg += " Use the Python standard library instead."
    elif replacement:
        msg += f" Use <{replacement}> instead."
    if additional_msg:
        msg += f" {additional_msg}"
    return msg


def get_bins(input_: list[str], upper: int) -> list[list[int]]:
    """Organizes indices of strings into bins based on a cumulative upper limit.

    Args:
        input_ (List[str]): The list of strings to be binned.
        upper (int): The cumulative length upper limit for each bin.

    Returns:
        List[List[int]]: A list of bins, each bin is a list of indices from the input list.
    """
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


__all__ = [
    "unique_hash",
    "is_same_dtype",
    "insert_random_hyphens",
    "get_file_classes",
    "get_class_file_registry",
    "get_class_objects",
    "time",
    "copy",
    "run_pip_command",
    "format_deprecation_msg",
    "get_bins",
]
