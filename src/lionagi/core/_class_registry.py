# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

import os
from typing import TypeVar

from lionagi.libs.utils import get_class_file_registry, get_class_objects

T = TypeVar("T")
LION_CLASS_REGISTRY: dict[str, type[T]] = {}
LION_CLASS_FILE_REGISTRY: dict[str, str] = {}

pattern_list = [
    "lionagi/core/generic",
    "lionagi/core/communication",
    "lionagi/core/action",
    "lionagi/core/session",
    "lionagi/core/forms",
]


if not LION_CLASS_FILE_REGISTRY:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    LION_CLASS_FILE_REGISTRY = get_class_file_registry(
        script_dir, pattern_list
    )


def get_class(class_name: str) -> type:
    """
    Retrieve a class by name from the registry or dynamically import it.

    This function first checks the LION_CLASS_REGISTRY for the requested class.
    If not found, it uses mor to dynamically import the class. The
    function ensures that the retrieved class is a subclass of the specified
    base_class.

    Args:
        class_name: The name of the class to retrieve.

    Returns:
        The requested class, which is a subclass of base_class.

    Raises:
        ValueError: If the class is not found or not a subclass of base_class.

    Usage:
        MyClass = get_class("MyClassName", BaseClass)
        instance = MyClass()

    Note:
        This function automatically registers newly found classes in the
        LION_CLASS_REGISTRY for future quick access.
    """
    if class_name in LION_CLASS_REGISTRY:
        return LION_CLASS_REGISTRY[class_name]

    try:
        found_class_filepath = LION_CLASS_FILE_REGISTRY[class_name]
        found_class_dict = get_class_objects(found_class_filepath)
        return found_class_dict[class_name]
    except Exception as e:
        raise ValueError(f"Unable to find class {class_name}: {e}")


# File: lionagi/core/util/class_registry_util.py
