# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

"""
Defines `Package` and `PackageCategory`, encapsulating the contents
and classification of mail items. Also includes a simple validator
to ensure categories are valid.
"""

from enum import Enum
from typing import Any

from lionagi.protocols.generic.element import ID, IDType
from lionagi.utils import time

from .._concepts import Communicatable, Observable


class PackageCategory(str, Enum):
    """
    Enumeration of common package categories in LionAGI:

    - MESSAGE: General message content
    - TOOL: A tool or action to be invoked
    - IMODEL: Some internal model reference
    - NODE: A node in a graph
    - NODE_LIST: A list of nodes
    - NODE_ID: A node ID
    - START: A 'start' signal
    - END: An 'end' signal
    - CONDITION: A condition or gating logic
    - SIGNAL: A more generic signal or marker
    """

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
    """
    Validate and convert the input to a valid PackageCategory.

    Parameters
    ----------
    value : Any
        The input to interpret as a `PackageCategory`.

    Returns
    -------
    PackageCategory
        The validated category.

    Raises
    ------
    ValueError
        If the value cannot be converted into a valid package category.
    """
    if isinstance(value, PackageCategory):
        return value
    try:
        return PackageCategory(str(value))
    except ValueError as e:
        raise ValueError("Invalid value for category.") from e


class Package(Observable):
    """
    A self-contained package that can be attached to `Mail` items.
    Includes a unique ID, creation timestamp, category, payload item,
    and an optional request source for context.

    Attributes
    ----------
    category : PackageCategory
        The classification or type of package.
    item : Any
        The main payload or data of this package.
    request_source : ID[Communicatable] | None
        An optional reference indicating the origin or context
        for this package.
    """

    __slots__ = ("id", "created_at", "category", "item", "request_source")

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


# File: lionagi/protocols/mail/package.py
