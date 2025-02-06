import asyncio
from collections.abc import Callable
from typing import Any

from pydantic import Field

from lionagi.protocols.generic.element import Element
from lionagi.protocols.generic.event import EventStatus
from lionagi.protocols.generic.log import Log
from lionagi.protocols.generic.pile import Pile, pile
from lionagi.protocols.graph.graph import Graph
from lionagi.utils import to_dict

from .work_edge import WorkEdge
from .work_function_node import WorkFunctionNode
from .work_task import WorkTask
from .worker import Worker


class WorkerEngine(Element):
    """
    A class representing an engine that manages and executes work tasks for a worker.

    This class extends Element to provide unique identification and timestamp tracking,
    while managing task execution and worker orchestration.

    Attributes:
        worker (Worker): The worker instance that the engine manages.
        tasks (Pile[WorkTask]): A pile of tasks to be executed.
        active_tasks (Pile[WorkTask]): A pile of currently active tasks.
        failed_tasks (Pile[WorkTask]): A pile of tasks that have failed.
        worker_graph (Graph): A graph representing the relationships between work functions.
        refresh_time (float): The time interval for refreshing the work log queue.
        _stop_event (asyncio.Event): An event to signal stopping the execution.
    """

    worker: Worker = Field(
        ..., description="The worker instance that the engine manages"
    )

    tasks: Pile[WorkTask] = Field(
        default_factory=lambda: pile(item_type=WorkTask),
        description="A pile of tasks to be executed",
    )

    active_tasks: Pile[WorkTask] = Field(
        default_factory=lambda: pile(item_type=WorkTask),
        description="A pile of currently active tasks",
    )

    failed_tasks: Pile[WorkTask] = Field(
        default_factory=lambda: pile(item_type=WorkTask),
        description="A pile of tasks that have failed",
    )

    worker_graph: Graph = Field(
        default_factory=Graph,
        description="A graph representing the relationships between work functions",
    )

    refresh_time: float = Field(
        default=1.0,
        description="The time interval for refreshing the work log queue",
    )

    def __init__(
        self, worker: Worker, refresh_time: float = 1.0, **kwargs: Any
    ) -> None:
        """
        Initializes a new instance of WorkerEngine.

        Args:
            worker (Worker): The worker instance to be managed.
            refresh_time (float): The time interval for refreshing the work log queue.
            **kwargs: Additional keyword arguments for Element initialization.
        """
        super().__init__(**kwargs)
        self.worker = worker
        self.refresh_time = refresh_time
        self._stop_event = asyncio.Event()
        self._construct_work_functions()
        self._construct_workedges()

    async def add_task(
        self,
        *args: Any,
        task_function: str,
        task_name: str | None = None,
        task_max_steps: int = 10,
        task_post_processing: Callable | None = None,
        **kwargs: Any,
    ) -> WorkTask:
        """
        Adds a new task to the task queue.
        """
        task = WorkTask(
            name=task_name,
            max_steps=task_max_steps,
            post_processing=task_post_processing,
        )
        self.tasks.include(task)
        function = getattr(self.worker, task_function)
        work = await function(*args, **kwargs)
        task.current_work = work
        task.work_history.append(work)
        return task

    async def activate_work_queues(self) -> None:
        """
        Activates the work queues for all work functions.
        """
        for work_function in self.worker.work_functions.values():
            if not work_function.worklog.queue.execution_mode:
                asyncio.create_task(work_function.worklog.queue.execute())

    async def stop(self) -> None:
        """
        Stops the execution of tasks.
        """
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """
        Checks if the execution has been stopped.
        """
        return self._stop_event.is_set()

    async def process(self, task: WorkTask) -> None:
        """
        Processes a single task.
        """
        current_work_func_name = task.current_work.async_task_name
        current_work_func = self.worker.work_functions[current_work_func_name]
        await task.process(current_work_func)

        if task.status == EventStatus.COMPLETED:
            self.active_tasks.exclude(task)
        elif task.status == EventStatus.FAILED:
            self.active_tasks.exclude(task)
            self.failed_tasks.include(task)
        else:
            await asyncio.sleep(self.refresh_time)

    async def execute(self, stop_queue: bool = True) -> None:
        """
        Executes all tasks in the task queue.
        """
        for task in self.tasks:
            if task.status == EventStatus.PENDING:
                task.status = EventStatus.PROCESSING
                self.active_tasks.include(task)

        await self.activate_work_queues()
        self._stop_event.clear()

        while len(self.active_tasks) > 0 and not self.stopped:
            for work_function in self.worker.work_functions.values():
                if len(work_function.worklog.pending) > 0:
                    await work_function.worklog.forward()
            tasks = list(self.active_tasks)
            await asyncio.gather(*[self.process(task) for task in tasks])
            await asyncio.sleep(self.refresh_time)

        if stop_queue:
            await self.stop()
            await self.worker.stop()

    async def execute_lasting(self) -> None:
        """
        Executes tasks continuously until stopped.
        """
        self._stop_event.clear()

        async def execute_lasting_inner() -> None:
            while not self.stopped:
                await self.execute(stop_queue=False)
                await asyncio.sleep(self.refresh_time)

        asyncio.create_task(execute_lasting_inner())

    def _construct_work_functions(self) -> None:
        """
        Constructs work functions for the worker.
        """
        if getattr(self.worker, "work_functions", None) is None:
            self.worker.work_functions = {}

        work_decorated_function = self.worker._get_decorated_functions(
            decorator_attr="_work_decorator_params", name_only=False
        )

        for func_name, func, dec_params in work_decorated_function:
            if func_name not in self.worker.work_functions:
                self.worker.work_functions[func_name] = WorkFunctionNode(
                    **dec_params
                )
                self.worker_graph.add_node(
                    self.worker.work_functions[func_name]
                )
            else:
                if not isinstance(
                    self.worker.work_functions[func_name], WorkFunctionNode
                ):
                    raise TypeError(
                        f"WorkFunction {func_name} already exists but is not a WorkFunctionNode. "
                        f"If you would like to use it in WorkerEngine, please convert it to a "
                        f"WorkFunctionNode, or initiate a new worker, or pop it from work_function dict"
                    )

    def _construct_workedges(self) -> None:
        """
        Constructs work edges for the worker graph.
        """
        worklink_decorated_function = self.worker._get_decorated_functions(
            decorator_attr="_worklink_decorator_params", name_only=False
        )

        for func_name, func, dec_params in worklink_decorated_function:
            head = self.worker.work_functions[dec_params["from_"]]
            tail = self.worker.work_functions[dec_params["to_"]]
            self.worker_graph.add_edge(
                head=head,
                tail=tail,
                convert_function=func,
                associated_worker=self.worker,
                edge_class=WorkEdge,
            )

    def to_log(self) -> Log:
        """Create a Log object summarizing this engine."""
        return Log(
            content={
                "type": "WorkerEngine",
                "id": str(self.id),
                "worker": str(self.worker.id),
                "tasks": {
                    "total": len(self.tasks),
                    "active": len(self.active_tasks),
                    "failed": len(self.failed_tasks),
                },
                "graph": {
                    "nodes": [
                        {
                            "id": str(n.id),
                            "name": n.name,
                            "type": n.__class__.__name__,
                        }
                        for n in self.worker_graph.nodes
                    ],
                    "edges": [
                        {
                            "id": str(e.id),
                            "name": e.name,
                            "head": str(e.head.id) if e.head else None,
                            "tail": str(e.tail.id) if e.tail else None,
                        }
                        for e in self.worker_graph.edges
                    ],
                },
                "status": {
                    "stopped": self.stopped,
                    "refresh_time": self.refresh_time,
                },
            }
        )
