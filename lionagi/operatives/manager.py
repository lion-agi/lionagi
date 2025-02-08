# Copyright (c) 2023 - 2025, HaiyangLi <quantocean.li at gmail dot com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import TYPE_CHECKING, Any, Dict, List

from lionagi.operatives.operative import TaskOperative, TaskStatus

if TYPE_CHECKING:
    from lionagi.session.branch import Branch


class TaskManager:
    """
    Manages and executes TaskOperative instances within a Branch.
    """

    def __init__(self):
        self.tasks: Dict[str, TaskOperative] = {}  # {task_id: TaskOperative}

    def add_task(self, task: TaskOperative):
        """Adds a task to the task manager."""
        self.tasks[task.id] = task

    def get_ready_tasks(self) -> List[TaskOperative]:
        """Returns a list of tasks that are ready to be executed."""
        ready_tasks = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check if all parent tasks are completed
                ready = True
                if hasattr(task, "parent_ids") and task.parent_ids:
                    for parent_id in task.parent_ids:
                        if parent_id not in self.tasks:
                            # log a warning that parent task is not found
                            # TODO: use logging module
                            print(
                                f"Warning: Parent task {parent_id} not found for task {task.id}"
                            )
                            continue
                        parent_task = self.tasks[parent_id]
                        if parent_task.status != TaskStatus.COMPLETED:
                            ready = False
                            break
                if ready:
                    ready_tasks.append(task)
        return ready_tasks

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Any = None,
        error: str = None,
    ):
        """Updates the status of a task."""
        task = self.tasks.get(task_id)
        if task:
            task.status = status
            # Assuming TaskOperative has result and error attributes.  These might
            # be part of the associated Form instead. We'll refine this.
            if result is not None:
                # TODO: how to update the form?
                # task.form.fill_fields(result=result)
                pass
            if error is not None:
                task.error = error
        else:
            # TODO: use logging module
            print(f"Warning: Task {task_id} not found in TaskManager.")

    async def run_task(self, task: TaskOperative, branch: "Branch"):
        """Runs a single task."""
        # Assuming TaskOperative has an associated Operative instance
        operative = task.operative
        if operative:
            try:
                # TODO: how to get the input data from the form?
                # result = await branch.operate(operative=operative, input_data=task.form.get_results())
                result = await branch.operate(operative=operative)
                self.update_task_status(
                    task.id, TaskStatus.COMPLETED, result=result
                )
            except Exception as e:
                self.update_task_status(
                    task.id, TaskStatus.FAILED, error=str(e)
                )
        else:
            # TODO: use logging module
            print(f"Warning: Task {task.id} has no associated Operative.")
            self.update_task_status(
                task.id,
                TaskStatus.FAILED,
                error="No operative associated with task.",
            )

    async def run_all_tasks(self, branch: "Branch"):
        """Runs all tasks in the task list."""
        while True:
            ready_tasks = self.get_ready_tasks()
            if not ready_tasks:
                break  # No more tasks to run

            # TODO: how to handle concurrency?
            for task in ready_tasks:
                await self.run_task(task, branch)
