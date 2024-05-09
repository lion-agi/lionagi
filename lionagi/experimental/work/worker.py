from abc import ABC
import asyncio
import logging
from typing import Dict, Optional

from lionagi.core.session.session import Session
from .record.report import Report, Form
from ._work._function import WorkFunction

class Worker(ABC):
    """
    Abstract base class for workers that process assigned tasks using asynchronous work functions.
    
    Attributes:
        name (str): Name of the worker.
        work_functions (Dict[str, WorkFunction]): Dictionary mapping assignments to WorkFunction instances.
        stopped (bool): Flag to indicate if the worker is stopped.
        reports (Dict[str, Report]): Dictionary of reports managed by this worker.
        default_form (Form): Default form class used for handling forms.
        session (Session): Session instance for the worker.

    Methods:
        append_report(report): Adds a report to the worker's management if it's not already present.
        stop(): Stops all work functions and logs the status.
        process(refresh_time): Processes all workable reports as long as the worker is not stopped.
    """

    name: str = "Worker"
    work_functions: Dict[str, WorkFunction] = {}
    stopped: bool = False
    reports: Dict[str, Report] = {}
    default_form: Form = Form
    session: Session = Session()

    async def append_report(self, report: Report) -> bool:
        """
        Adds a report to the worker's reports dictionary if not already present.

        Args:
            report (Report): The report to add.

        Returns:
            bool: True if the report was added, False if it was already present.
        """
        if report.id_ not in self.reports:
            self.reports[report.id_] = report
            return True
        return False

    @property
    def workable_reports(self) -> Optional[Dict[str, Report]]:
        """
        Filters and returns workable reports from the reports dictionary.

        Returns:
            Optional[Dict[str, Report]]: A dictionary of workable reports if any exist, otherwise None.
        """
        workable = {k: v for k, v in self.reports.items() if v.workable}
        return workable if workable else None

    async def stop(self):
        """
        Stops all work functions and updates the worker's status to stopped.
        """
        self.stopped = True
        logging.info(f"Stopping worker {self.name}")
        non_stopped_worklogs = []

        for func in self.work_functions.values():
            worklog = func.worklog
            await worklog.stop()
            if not worklog.stopped:
                non_stopped_worklogs.append(func.name)

        if non_stopped_worklogs:
            logging.error(f"Could not stop worklogs: {non_stopped_worklogs}")

        logging.info(f"Stopped worker {self.name}")

    async def process(self, refresh_time: float = 1.0):
        """
        Processes workable reports asynchronously until the worker is stopped.

        Args:
            refresh_time (float): The time to pause after processing a batch of reports.
        """
        while self.workable_reports and not self.stopped:
            tasks = [
                asyncio.create_task(func.process())
                for func in self.work_functions.values()
            ]
            await asyncio.wait(tasks)

        await asyncio.sleep(refresh_time)



# def work(assignment=None, capacity=5, refresh_time=1):
#     def decorator(func: Callable):

#         @wraps(func)
#         async def wrapper(self: Worker, **kwargs):
#             if getattr(self, "work_functions", None) is None:
#                 self.work_functions = {}

#             if assignment not in self.work_functions:
#                 self.work_functions[assignment] = WorkFunction(
#                     assignment=assignment,
#                     function=func,
#                     retry_kwargs=kwargs.get("retry_kwargs") or {},
#                     manual=kwargs.get("instruction", None) or func.__doc__,
#                     capacity=capacity,
#                     refresh_time=refresh_time,
#                 )

#             work_func: WorkFunction = self.work_functions[assignment]

#             # form: Form = kwargs.get("form", None) or self.default_form(
#             #     assignment=work_func.assignment
#             # )

#             # for k, v in kwargs.items():
#             #     if k in form.work_fields:
#             #         form.fill(**{k: v})

#             # try:
#             #     form.check_workable()
#             # except Exception as e:
#             #     raise ValueError(f"Not workable") from e

#             task = asyncio.create_task(work_func.perform(self, **kwargs))
#             work = Work(async_task=task)
#             await work_func.worklog.append(work)
#             work_func.worklog.add_count += 1
#             return True

#         return wrapper

#     return decorator


# # Example
# from lionagi import Session
# from lionagi.experimental.work.work_function import work


# class MyWorker(Worker):

#     @work(assignment="instruction, context -> response")
#     async def chat(instruction=None, context=None):
#         session = Session()
#         return await session.chat(instruction=instruction, context=context)


# await a.chat(instruction="Hello", context={})
