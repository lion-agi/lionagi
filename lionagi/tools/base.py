# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod

from lionagi.operatives.action.tool import Tool


class LionTool(ABC):
    is_lion_system_tool: bool = True
    system_tool_name: str

    @abstractmethod
    def to_tool(self) -> Tool:
        pass
