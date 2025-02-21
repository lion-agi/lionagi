# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.libs.fields.instruct import INSTRUCT_FIELD, Instruct
from lionagi.protocols.types import Node

__all__ = ("InstructNode",)


class InstructNode(Node):
    instruct: Instruct | None = INSTRUCT_FIELD.field_info
