# Copyright (c) 2023 - 2024, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from lionagi.protocols.types import Node

from .instruct import INSTRUCT_FIELD, Instruct

__all__ = ("InstructNode",)


class InstructNode(Node):
    instruct: Instruct | None = INSTRUCT_FIELD.field_info
