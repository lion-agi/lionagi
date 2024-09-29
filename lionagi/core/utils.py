import warnings
from typing import Literal

from lionfuncs import format_deprecation_msg


def deprecation_warnings(
    deprecated_name: str,
    type_: Literal["class", "function", "method", "attribute", "property", "module"],
    deprecated_version: str,
    removal_version: str,
    replacement: str | None = None,
    additional_msg: str | None = None,
):
    msg = format_deprecation_msg(
        deprecated_name,
        type_,
        deprecated_version,
        removal_version,
        replacement,
        additional_msg,
    )
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
