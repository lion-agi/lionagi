"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from collections.abc import Callable
from typing import Any

from pydantic import Field

from lionagi.protocols.graph import Node

from .work_function import WorkFunction


class WorkFunctionNode(WorkFunction, Node):
    """
    A class representing a work function node, combining the functionality
    of a WorkFunction and a Node.

    This class extends both WorkFunction and Node to provide:
    - Work function capabilities (execution, retry logic, work logging)
    - Graph node capabilities (relations, edge management)
    - Unique identification and timestamp tracking (from Element)

    Attributes:
        assignment (str): The assignment description of the work function.
        function (Callable): The function to be performed.
        retry_kwargs (dict): The retry arguments for the function.
        guidance (str): The guidance or documentation for the function.
        capacity (int): The capacity of the work queue batch processing.
        refresh_time (float): The time interval to refresh the work log queue.
    """

    def __init__(
        self,
        assignment: str,
        function: Callable,
        retry_kwargs: dict | None = None,
        guidance: str | None = None,
        capacity: int = 10,
        refresh_time: float = 1,
        **kwargs: Any,
    ):
        """
        Initializes a WorkFunctionNode instance.

        Args:
            assignment (str): The assignment description of the work function.
            function (Callable): The function to be performed.
            retry_kwargs (dict, optional): The retry arguments for the function.
            guidance (str, optional): The guidance or documentation for the function.
            capacity (int): The capacity of the work queue batch processing.
            refresh_time (float): The time interval to refresh the work log queue.
            **kwargs: Additional keyword arguments for Node initialization.
        """
        # Initialize both parent classes
        # Note: Element.__init__ is called by both WorkFunction and Node,
        # but Pydantic handles this correctly through model_config
        Node.__init__(self, **kwargs)
        WorkFunction.__init__(
            self,
            assignment=assignment,
            function=function,
            retry_kwargs=retry_kwargs,
            guidance=guidance,
            capacity=capacity,
            refresh_time=refresh_time,
        )
