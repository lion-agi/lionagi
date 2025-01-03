# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import Any

from lionagi.protocols.generic.element import ID, IDType
from lionagi.utils import time

from .._concepts import Communicatable, Observable


class PackageCategory(str, Enum):
    """Enumeration of package categories in the Lion framework."""

    MESSAGE = "message"
    TOOL = "tool"
    IMODEL = "imodel"
    NODE = "node"
    NODE_LIST = "node_list"
    NODE_ID = "node_id"
    START = "start"
    END = "end"
    CONDITION = "condition"
    SIGNAL = "signal"


def validate_category(value: Any) -> PackageCategory:
    """Validate the category field."""
    if isinstance(value, PackageCategory):
        return value
    try:
        return PackageCategory(str(value))
    except ValueError as e:
        raise ValueError("Invalid value for category.") from e


class Package(Observable):

    def __init__(
        self,
        category: PackageCategory,
        item: Any,
        request_source: ID[Communicatable] = None,
    ):

        super().__init__()
        self.id = IDType.create()
        self.created_at = time(type_="timestamp")
        self.category = validate_category(category)
        self.item = item
        self.request_source = request_source

    __slots__ = ("id", "created_at", "category", "item", "request_source")
