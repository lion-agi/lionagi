from functools import wraps
from typing import Any, Callable, Tuple

from abc import ABC, abstractmethod
from lionagi import logging as _logging
from .work_function import WorkFunction
import asyncio
from .schema import Work
from .worklog import WorkLog


class Worker(ABC):
    # This is a class that will be used to create a worker object
    # work_functions are keyed by assignment {assignment: WorkFunction}

    name: str = "Worker"
    work_functions: dict[str, WorkFunction] = {}

    def __init__(self) -> None:
        self.stopped = False

    async def stop(self):
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
        task = asyncio.create_task(work_func.perform(*args, **kwargs))
        work = Work(async_task=task)
        work_func: WorkFunction = self.work_functions[func.__name__]
        await work_func.worklog.append(work)
        return True


def work(assignment, capacity=10, guidance=None, retry_kwargs=None):
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
