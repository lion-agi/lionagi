from pathlib import Path
import logging
import re

from pathlib import Path
from typing import Any, Dict
import logging

from typing import Optional
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET

number_regex = re.compile(r'-?\d+\.?\d*')


class ImportUtil:

    @staticmethod
    def get_cpu_architecture() -> str:
        arch: str = platform.machine().lower()
        if 'arm' in arch or 'aarch64' in arch:
            return 'apple_silicon'
        return 'other_cpu'

    @staticmethod
    def install_import(package_name: str, module_name: str | None = None,
                       import_name: str | None = None,
                       pip_name: str | None = None) -> None:
        pip_name: str = pip_name or package_name
        full_import_path: str = f"{package_name}.{module_name}" if module_name else package_name

        try:
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)
            print(f"Successfully imported {import_name or full_import_path}.")
        except ImportError:
            print(
                f"Module {full_import_path} or attribute {import_name} not found. Installing {pip_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

            # Retry the import after installation
            if import_name:
                module = __import__(full_import_path, fromlist=[import_name])
                getattr(module, import_name)
            else:
                __import__(full_import_path)

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        package_spec = importlib.util.find_spec(package_name)
        return package_spec is not None

    @staticmethod
    def check_import(package_name: str, module_name: str | None = None,
                     import_name: str | None = None, pip_name: str | None = None) -> None:
        try:
            if not SysUtil.is_package_installed(package_name):
                logging.info(f"Package {package_name} not found. Attempting to install.")
                SysUtil.install_import(package_name, module_name, import_name, pip_name)
        except ImportError as e:  # More specific exception handling
            logging.error(f'Failed to import {package_name}. Error: {e}')
            raise ValueError(f'Failed to import {package_name}. Error: {e}') from e


class PathUtil:
    @staticmethod
    def clear_dir(dir_path: Path | str, recursive: bool = False,
                  exclude: list[str] = None) -> None:
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"The specified directory {dir_path} does not exist.")

        exclude = exclude or []
        exclude_pattern = re.compile("|".join(exclude)) if exclude else None

        for file_path in dir_path.iterdir():
            if exclude_pattern and exclude_pattern.search(file_path.name):
                logging.info(f"Excluded from deletion: {file_path}")
                continue

            if recursive and file_path.is_dir():
                PathUtil.clear_dir(file_path, recursive=True, exclude=exclude)
            elif file_path.is_file() or file_path.is_symlink():
                try:
                    file_path.unlink()
                    logging.info(f"Successfully deleted {file_path}")
                except Exception as e:
                    logging.error(f"Failed to delete {file_path}. Reason: {e}")
                    raise

    @staticmethod
    def split_path(path: Path | str) -> tuple[Path, str]:
        path = Path(path)
        return path.parent, path.name

    @staticmethod
    def create_path(directory: Path | str, filename: str, timestamp: bool = True,
                    dir_exist_ok: bool = True, time_prefix: bool = False,
                    custom_timestamp_format: str | None = None) -> Path:
        directory = Path(directory)
        if not re.match(r'^[\w,\s-]+\.[A-Za-z]{1,5}$', filename):
            raise ValueError(
                "Invalid filename. Ensure it doesn't contain illegal characters and has a valid extension.")

        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        ext = f".{ext}" if ext else ''

        timestamp_str = ""
        if timestamp:
            from datetime import datetime
            timestamp_format = custom_timestamp_format or "%Y%m%d%H%M%S"
            timestamp_str = datetime.now().strftime(timestamp_format)
            filename = f"{timestamp_str}_{name}" if time_prefix else f"{name}_{timestamp_str}"
        else:
            filename = name

        full_filename = f"{filename}{ext}"
        full_path = directory / full_filename
        full_path.parent.mkdir(parents=True, exist_ok=dir_exist_ok)

        return full_path


class ConvertUtil:

    @staticmethod
    def to_dict(input_: Any) -> Dict[Any, Any]:

        if isinstance(input_, str):
            try:
                return json.loads(input_)
            except json.JSONDecodeError as e:
                raise ValueError(f"Could not convert input_ to dict: {e}") from e

        elif isinstance(input_, dict):
            return input_
        else:
            raise TypeError(
                f"Could not convert input_ to dict: {type(input_).__name__} given.")

    @staticmethod
    def is_same_dtype(input_: list | dict, dtype: Type | None = None) -> bool:
        if not input_:
            return True

        iterable = input_.values() if isinstance(input_, dict) else input_
        first_element_type = type(next(iter(iterable), None))

        dtype = dtype or first_element_type

        return all(isinstance(element, dtype) for element in iterable)

    @staticmethod
    def xml_to_dict(root: ET.Element) -> Dict[str, Any]:
        def parse_xml(element: ET.Element, parent: Dict[str, Any]):
            children = list(element)
            if children:
                d = defaultdict(list)
                for child in children:
                    parse_xml(child, d)
                parent[element.tag].append(d if len(d) > 1 else d[next(iter(d))])
            else:
                parent[element.tag].append(element.text)

        result = defaultdict(list)
        parse_xml(root, result)
        return {k: v[0] if len(v) == 1 else v for k, v in result.items()}

    @staticmethod
    def str_to_num(input_: str, upper_bound: float | None = None, lower_bound: float | None = None,
                   num_type: Type[int | float] = int, precision: int | None = None) -> int | float:
        number_str = ConvertUtil._extract_first_number(input_)
        if number_str is None:
            raise ValueError(f"No numeric values found in the string: {input_}")

        number = ConvertUtil._convert_to_num(number_str, num_type, precision)

        if upper_bound is not None and number > upper_bound:
            raise ValueError(f"Number {number} is greater than the upper bound of {upper_bound}.")

        if lower_bound is not None and number < lower_bound:
            raise ValueError(f"Number {number} is less than the lower bound of {lower_bound}.")

        return number

    @staticmethod
    def strip_lower(input_: Any) -> str:
        try:
            return str(input_).strip().lower()
        except Exception as e:
            raise ValueError(f"Could not convert input_ to string: {input_}, Error: {e}")

    @staticmethod
    def _extract_first_number(input_: str) -> str | None:
        match = number_regex.search(input_)
        return match.group(0) if match else None

    @staticmethod
    def _convert_to_num(number_str: str, num_type: Type[int | float] = int, precision: int | None = None) -> int | float:
        if num_type is int:
            return int(float(number_str))
        elif num_type is float:
            number = float(number_str)
            return round(number, precision) if precision is not None else number
        else:
            raise ValueError(f"Invalid number type: {num_type}")

    @staticmethod
    def is_homogeneous(iterables: List[Any] | Dict[Any, Any], type_check: type) -> bool:
        if isinstance(iterables, list):
            return all(isinstance(it, type_check) for it in iterables)
        return isinstance(iterables, type_check)

    @staticmethod
    def to_readable_dict(input_: Dict[Any, Any] | List[Any]) -> str | List[Any]:
        return json.dumps(input_, indent=4) if isinstance(input_, dict) else input_

    @staticmethod
    def to_df(
        item: List[Dict[Any, Any] | DataFrame | Series] | DataFrame | Series,
        how: str = 'all',
        drop_kwargs: Dict[str, Any] | None = None,
        reset_index: bool = True,
        **kwargs: Any
    ) -> DataFrame:
        if drop_kwargs is None:
            drop_kwargs = {}
        dfs = ''
        try:
            if isinstance(item, list):
                if ConvertUtil.is_homogeneous(item, dict):
                    dfs = pd.DataFrame(item)
                elif ConvertUtil.is_homogeneous(item, (DataFrame, Series)):
                    dfs = pd.concat(item, **kwargs)
                else:
                    raise ValueError("Item list is not homogeneous or cannot be converted to DataFrame.")
            elif isinstance(item, (DataFrame, Series)):
                dfs = item if isinstance(item, DataFrame) else pd.DataFrame(item)
            else:
                raise TypeError("Unsupported type for conversion to DataFrame.")

            dfs.dropna(**(drop_kwargs | {'how': how}), inplace=True)

            if reset_index:
                dfs.reset_index(drop=True, inplace=True)

            return dfs

        except Exception as e:
            raise ValueError(f"Error converting item to DataFrame: {e}") from e


