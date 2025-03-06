# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from pathlib import Path
from typing import ClassVar

from pydantic import Field, PrivateAttr

from lionagi.protocols._concepts import Manager
from lionagi.protocols.generic.pile import Pile
from lionagi.protocols.graph.graph import Graph
from lionagi.protocols.graph.node import Node
from lionagi.tools.base import LionTool
from lionagi.tools.file.base import Document
from lionagi.operatives.action.tool import Tool


class DocumentManager(Manager):
        
    _g: Graph = PrivateAttr(default_factory=Graph)

