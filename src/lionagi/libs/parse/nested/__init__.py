"""Nested data structure manipulation utilities."""

from .nfilter import nfilter
from .nget import nget
from .ninsert import ninsert
from .nmerge import nmerge
from .npop import npop
from .nset import nset
from .to_flat_list import to_flat_list
from .utils import (
    deep_update,
    ensure_list_index,
    get_target_container,
    is_homogeneous,
    is_same_dtype,
    is_structure_homogeneous,
)

__all__ = [
    "nfilter",
    "nget",
    "ninsert",
    "nmerge",
    "npop",
    "nset",
    "to_flat_list",
    "deep_update",
    "ensure_list_index",
    "get_target_container",
    "is_homogeneous",
    "is_same_dtype",
    "is_structure_homogeneous",
]
