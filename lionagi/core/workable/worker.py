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

from abc import ABC
from functools import wraps
import asyncio
from lionagi import logging as _logging
from lionagi.os.lib import pcall
from lionagi.os.core.work.work_function import WorkFunction
from lionagi.os.core.work.work import Work


class Worker(ABC):
    """
    This class represents a worker that handles multiple work functions.

    Attributes:
        name (str): The name of the worker.
        work_functions (dict[str, WorkFunction]): Dictionary mapping assignments to WorkFunction objects.
    """

    name: str = "Worker"
    work_functions: dict[str, WorkFunction] = {}

    def __init__(self) -> None:
        self.stopped = False

    async def stop(self):
        """
        Stops the worker and all associated work functions.
        """
        self.stopped = True
        _logging.info(f"Stopping worker {self.name}")
        non_stopped_ = []

        for func in self.work_functions.values():
            worklog = func.worklog
            await worklog.stop()
            if not worklog.stopped:
                non_stopped_.append(func.name)

        if len(non_stopped_) > 0:
            _logging.error(f"Could not stop worklogs: {non_stopped_}")
        _logging.info(f"Stopped worker {self.name}")

    async def is_progressable(self):
        """
        Checks if any work function is progressable and the worker is not stopped.

        Returns:
            bool: True if any work function is progressable and the worker is not stopped, else False.
        """

        return (
            any([await i.is_progressable() for i in self.work_functions.values()])
            and not self.stopped
        )

    async def process(self, refresh_time=1):
        """
        Processes all work functions periodically.

        Args:
            refresh_time (int): Time interval between each process cycle.
        """
        while await self.is_progressable():
            await pcall([i.process(refresh_time) for i in self.work_functions.values()])
            await asyncio.sleep(refresh_time)

    # TODO: Implement process method

    # async def process(self, refresh_time=1):
    #     while not self.stopped:
    #         tasks = [
    #             asyncio.create_task(func.process(refresh_time=refresh_time))
    #             for func in self.work_functions.values()
    #         ]
    #         await asyncio.wait(tasks)
    #         await asyncio.sleep(refresh_time)

    async def _wrapper(
        self,
        *args,
        func=None,
        assignment=None,
        capacity=None,
        retry_kwargs=None,
        guidance=None,
        **kwargs,
    ):
        """
        Internal wrapper to handle work function execution.

        Args:
            func (Callable): The function to be executed.
            assignment (str): The assignment description.
            capacity (int): Capacity for the work log.
            retry_kwargs (dict): Retry arguments for the function.
            guidance (str): Guidance or documentation for the function.
        """
        if getattr(self, "work_functions", None) is None:
            self.work_functions = {}

        if func.__name__ not in self.work_functions:
            self.work_functions[func.__name__] = WorkFunction(
                assignment=assignment,
                function=func,
                retry_kwargs=retry_kwargs or {},
                guidance=guidance or func.__doc__,
                capacity=capacity,
            )

        work_func: WorkFunction = self.work_functions[func.__name__]
        task = asyncio.create_task(work_func.perform(self, *args, **kwargs))
        work = Work(async_task=task)
        await work_func.worklog.append(work)
        return True


def work(
    assignment=None,
    capacity=10,
    guidance=None,
    retry_kwargs=None,
    refresh_time=1,
    timeout=10,
):
    """
    Decorator to mark a method as a work function.

    Args:
        assignment (str): The assignment description of the work function.
        capacity (int): Capacity for the work log.
        guidance (str): Guidance or documentation for the work function.
        retry_kwargs (dict): Retry arguments for the work function.
        refresh_time (int): Time interval between each process cycle.
        timeout (int): Timeout for the work function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(
            self: Worker,
            *args,
            func=func,
            assignment=assignment,
            capacity=capacity,
            retry_kwargs=retry_kwargs,
            guidance=guidance,
            **kwargs,
        ):
            retry_kwargs = retry_kwargs or {}
            retry_kwargs["timeout"] = retry_kwargs.get("timeout", timeout)
            return await self._wrapper(
                *args,
                func=func,
                assignment=assignment,
                capacity=capacity,
                retry_kwargs=retry_kwargs,
                guidance=guidance,
                **kwargs,
            )

        return wrapper

    return decorator


# # Example
# from lionagi import Session
# from lionagi.experimental.work.work_function import work


# class MyWorker(Worker):

#     @work(assignment="instruction, context -> response")
#     async def chat(instruction=None, context=None):
#         session = Session()
#         return await session.chat(instruction=instruction, context=context)


# await a.chat(instruction="Hello", context={})
