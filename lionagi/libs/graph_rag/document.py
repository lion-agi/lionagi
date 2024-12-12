# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0
#
# Portions derived from https://github.com/microsoft/autogen are under the MIT License.
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class DocumentType(Enum):
    """
    Enum for supporting document type.
    """

    TEXT = auto()
    HTML = auto()
    PDF = auto()


@dataclass
class Document:
    """
    A wrapper of graph store query results.
    """

    doctype: DocumentType
    data: object | None = None
    path_or_url: str | None = ""
