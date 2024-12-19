from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import model_validator

from ._utils import Params
from .alcall import alcall
from .bcall import bcall
from .create_path import create_path
from .lcall import lcall
from .tcall import tcall
from .to_dict import to_dict
from .to_list import to_list
from .undefined import Undefined

__all__ = (
    "Params",
    "ToListParams",
    "CallParams",
    "LCallParams",
    "ALCallParams",
    "TCallParams",
    "BCallParams",
    "ToDictParams",
    "CreatePathParams",
)


class ToListParams(Params):
    flatten: bool = False
    dropna: bool = False
    unique: bool = False
    use_values: bool = False
    flatten_tuple_set: bool = False

    def __call__(self, input_: Any):
        return to_list(
            input_,
            flatten=self.flatten,
            dropna=self.dropna,
            unique=self.unique,
            use_values=self.use_values,
            flatten_tuple_set=self.flatten_tuple_set,
        )


class CallParams(Params):
    """params class for high order function with additional handling of lower order function parameters, can take arbitrary number of args and kwargs, args need to be in agrs=, kwargs can be passed as is"""

    args: list = []
    kwargs: dict = {}

    @model_validator(mode="before")
    def _validate_data(cls, data: dict):
        _d = {}
        for k in list(data.keys()):
            if k in cls.keys():
                _d[k] = data.pop(k)
        _d.setdefault("args", [])
        _d.setdefault("kwargs", {})
        _d["kwargs"].update(data)
        return _d

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(
            "This method should be implemented in a subclass"
        )


class LCallParams(CallParams):
    func: Any = None
    sanitize_input: bool = False
    unique_input: bool = False
    flatten: bool = False
    dropna: bool = False
    unique_output: bool = False
    flatten_tuple_set: bool = False

    def __call__(self, input_: Any, func=None):
        if self.func is None and func is None:
            raise ValueError("a sync func must be provided")
        return lcall(
            input_,
            func or self.func,
            *self.args,
            sanitize_input=self.sanitize_input,
            unique_input=self.unique_input,
            flatten=self.flatten,
            dropna=self.dropna,
            unique_output=self.unique_output,
            flatten_tuple_set=self.flatten_tuple_set,
            **self.kwargs,
        )


class ALCallParams(CallParams):
    func: Any = None
    sanitize_input: bool = False
    unique_input: bool = False
    num_retries: int = 0
    initial_delay: float = 0
    retry_delay: float = 0
    backoff_factor: float = 1
    retry_default: Any = Undefined
    retry_timeout: float | None = None
    retry_timing: bool = False
    max_concurrent: int | None = None
    throttle_period: float | None = None
    flatten: bool = False
    dropna: bool = False
    unique_output: bool = False
    flatten_tuple_set: bool = False

    async def __call__(self, input_: Any, func=None):
        if self.func is None and func is None:
            raise ValueError("a sync/async func must be provided")
        return await alcall(
            input_,
            func or self.func,
            *self.args,
            sanitize_input=self.sanitize_input,
            unique_input=self.unique_input,
            num_retries=self.num_retries,
            initial_delay=self.initial_delay,
            retry_delay=self.retry_delay,
            backoff_factor=self.backoff_factor,
            retry_default=self.retry_default,
            retry_timeout=self.retry_timeout,
            retry_timing=self.retry_timing,
            max_concurrent=self.max_concurrent,
            throttle_period=self.throttle_period,
            flatten=self.flatten,
            dropna=self.dropna,
            unique_output=self.unique_output,
            flatten_tuple_set=self.flatten_tuple_set,
            **self.kwargs,
        )


class TCallParams(CallParams):
    func: Any = None
    timeout: float | None = None
    default: Any = Undefined
    timing: bool = False
    error_msg: str = ""
    initial_delay: float = 0
    error_map: dict = None

    async def __call__(self, func=None):
        if self.func is None and func is None:
            raise ValueError("a sync/async func must be provided")
        return await tcall(
            func or self.func,
            *self.args,
            timeout=self.timeout,
            default=self.default,
            timing=self.timing,
            error_msg=self.error_msg,
            initial_delay=self.initial_delay,
            error_map=self.error_map,
            **self.kwargs,
        )


class BCallParams(CallParams):
    func: Any = None
    batch_size: int
    sanitize_input: bool = False
    unique_input: bool = False
    num_retries: int = 0
    initial_delay: float = 0
    retry_delay: float = 0
    backoff_factor: float = 1
    retry_default: Any = Undefined
    retry_timeout: float | None = None
    retry_timing: bool = False
    max_concurrent: int | None = None
    throttle_period: float | None = None
    flatten: bool = False
    dropna: bool = False
    unique_output: bool = False
    flatten_tuple_set: bool = False

    async def __call__(self, input_, func=None):
        if self.func is None and func is None:
            raise ValueError("a sync/async func must be provided")
        return await bcall(
            input_,
            func or self.func,
            *self.args,
            batch_size=self.batch_size,
            sanitize_input=self.sanitize_input,
            unique_input=self.unique_input,
            num_retries=self.num_retries,
            initial_delay=self.initial_delay,
            retry_delay=self.retry_delay,
            backoff_factor=self.backoff_factor,
            retry_default=self.retry_default,
            retry_timeout=self.retry_timeout,
            retry_timing=self.retry_timing,
            max_concurrent=self.max_concurrent,
            throttle_period=self.throttle_period,
            flatten=self.flatten,
            dropna=self.dropna,
            unique_output=self.unique_output,
            flatten_tuple_set=self.flatten_tuple_set,
            **self.kwargs,
        )


class ToDictParams(Params):
    use_model_dump: bool = True
    fuzzy_parse: bool = False
    suppress: bool = False
    str_type: Literal["json", "xml"] | None = "json"
    parser: Callable[[str], Any] | None = None
    recursive: bool = False
    max_recursive_depth: int | None = None
    recursive_python_only: bool = True
    use_enum_values: bool = False
    remove_root: bool = False
    root_tag: str = "root"

    def __call__(self, input_, /):
        return to_dict(
            input_,
            use_model_dump=self.use_model_dump,
            fuzzy_parse=self.fuzzy_parse,
            suppress=self.suppress,
            str_type=self.str_type,
            parser=self.parser,
            recursive=self.recursive,
            max_recursive_depth=self.max_recursive_depth,
            recursive_python_only=self.recursive_python_only,
            use_enum_values=self.use_enum_values,
            remove_root=self.remove_root,
            root_tag=self.root_tag,
        )


class CreatePathParams(Params):
    directory: Path | str
    filename: str
    extension: str = None
    timestamp: bool = False
    dir_exist_ok: bool = True
    file_exist_ok: bool = False
    time_prefix: bool = False
    timestamp_format: str | None = None
    random_hash_digits: int = 0

    def __call__(
        self, directory: Path | str = None, filename: str = None
    ) -> Path:
        return create_path(
            directory or self.directory,
            filename or self.filename,
            extension=self.extension,
            timestamp=self.timestamp,
            dir_exist_ok=self.dir_exist_ok,
            file_exist_ok=self.file_exist_ok,
            time_prefix=self.time_prefix,
            timestamp_format=self.timestamp_format,
            random_hash_digits=self.random_hash_digits,
        )
