import asyncio

from lionagi.core.collections.pile import pile
from lionagi.core.generic.graph import Graph
from lionagi.core.work.work import WorkStatus
from lionagi.core.work.work_edge import WorkEdge
from lionagi.core.work.work_function_node import WorkFunctionNode
from lionagi.core.work.work_task import WorkTask
from lionagi.core.work.worker import Worker


class WorkerEngine:
    """
    A class representing an engine that manages and executes work tasks for a worker.

    Attributes:
        worker (Worker): The worker instance that the engine manages.
        tasks (Pile): A pile of tasks to be executed.
        active_tasks (Pile): A pile of currently active tasks.
        failed_tasks (Pile): A pile of tasks that have failed.
        worker_graph (Graph): A graph representing the relationships between work functions.
        refresh_time (int): The time interval for refreshing the work log queue.
        _stop_event (asyncio.Event): An event to signal stopping the execution.
    """

    def __init__(self, worker: Worker, refresh_time=1):
        """
        Initializes a new instance of WorkerEngine.

        Args:
            worker (Worker): The worker instance to be managed.
            refresh_time (int): The time interval for refreshing the work log queue.
        """
        self.worker = worker
        self.tasks = pile()
        self.active_tasks = pile()
        self.failed_tasks = pile()
        self.worker_graph = Graph()
        self._construct_work_functions()
        self._construct_workedges()
        self.refresh_time = refresh_time
        self._stop_event = asyncio.Event()

    async def add_task(
        self,
        *args,
        task_function: str,
        task_name=None,
        task_max_steps=10,
        task_post_processing=None,
        **kwargs,
    ):
        """
        Adds a new task to the task queue.

        Args:
            task_function (str): The name of the task function to execute.
            task_name (str, optional): The name of the task.
            task_max_steps (int, optional): The maximum number of steps for the task.
            task_post_processing (Callable, optional): The post-processing function for the task.
            *args: Positional arguments for the task function.
            **kwargs: Keyword arguments for the task function.

        Returns:
            WorkTask: The newly created task.
        """
        task = WorkTask(
            name=task_name,
            max_steps=task_max_steps,
            post_processing=task_post_processing,
        )
        self.tasks.append(task)
        function = getattr(self.worker, task_function)
        work = await function(*args, **kwargs)
        task.current_work = work
        task.work_history.append(work)
        return task

    async def activate_work_queues(self):
        """
        Activates the work queues for all work functions.
        """
        for work_function in self.worker.work_functions.values():
            if not work_function.worklog.queue.execution_mode:
                asyncio.create_task(work_function.worklog.queue.execute())

    async def stop(self):
        """
        Stops the execution of tasks.
        """
        self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """
        Checks if the execution has been stopped.

        Returns:
            bool: True if stopped, otherwise False.
        """
        return self._stop_event.is_set()

    async def process(self, task: WorkTask):
        """
        Processes a single task.

        Args:
            task (WorkTask): The task to be processed.
        """
        current_work_func_name = task.current_work.async_task_name
        current_work_func = self.worker.work_functions[current_work_func_name]
        updated_task = await task.process(current_work_func)
        if updated_task == "COMPLETED":
            self.active_tasks.pop(task)
        elif updated_task == "FAILED":
            self.active_tasks.pop(task)
            self.failed_tasks.append(task)
        elif isinstance(updated_task, list):
            self.tasks.include(updated_task)
            self.active_tasks.include(updated_task)
        else:
            await asyncio.sleep(self.refresh_time)

    async def execute(self, stop_queue=True):
        """
        Executes all tasks in the task queue.

        Args:
            stop_queue (bool, optional): Whether to stop the queue after execution. Defaults to True.
        """
        for task in self.tasks:
            if task.status == WorkStatus.PENDING:
                task.status = WorkStatus.IN_PROGRESS
                self.active_tasks.append(task)

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

    async def execute_lasting(self):
        """
        Executes tasks continuously until stopped.
        """
        self._stop_event.clear()

        async def execute_lasting_inner():
            while not self.stopped:
                await self.execute(stop_queue=False)
                await asyncio.sleep(self.refresh_time)

        asyncio.create_task(execute_lasting_inner())

    def _construct_work_functions(self):
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

    def _construct_workedges(self):
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
