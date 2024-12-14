# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""Nested data structure manipulation utilities."""

from .nfilter import nfilter
from .nget import nget
from .ninsert import ninsert
from .nmerge import nmerge
from .npop import npop
from .nset import nset
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
    "deep_update",
    "ensure_list_index",
    "get_target_container",
    "is_homogeneous",
    "is_same_dtype",
    "is_structure_homogeneous",
]
