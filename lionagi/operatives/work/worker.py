import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any

from pydantic import Field, field_validator

from lionagi import logging as _logging
from lionagi.operatives.forms.form import Form
from lionagi.protocols._concepts import Manager
from lionagi.protocols.generic.element import ID, Element
from lionagi.protocols.generic.log import Log
from lionagi.utils import to_dict

from .work import Work
from .work_function import WorkFunction


class Worker(Element, Manager):
    """
    This class represents a worker that handles multiple work functions.

    This class extends Element to provide unique identification and timestamp tracking,
    while implementing Manager to handle work function orchestration.

    Attributes:
        name (str): The name of the worker.
        work_functions (dict[str, WorkFunction]): Dictionary mapping assignments to WorkFunction objects.
        forms (dict[str, Form]): Dictionary mapping form identifier to Form objects.
        default_form (str|None): The default form to be used by the worker.
    """

    name: str = Field("Worker", description="The name of the worker")

    work_functions: dict[str, WorkFunction] = Field(
        default_factory=dict,
        description="Dictionary mapping assignments to WorkFunction objects",
    )

    forms: dict[str, Form] = Field(
        default_factory=dict,
        description="Dictionary mapping form identifier to Form objects",
    )

    default_form: str | None = Field(
        None, description="The default form to be used by the worker"
    )

    def __init__(
        self,
        forms: dict[str, Form] | None = None,
        default_form: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes a new instance of Worker.

        Args:
            forms (dict[str, Form], optional): Dictionary mapping form identifier to Form objects.
            default_form (str|None, optional): The default form to be used by the worker.
            **kwargs: Additional keyword arguments for Element initialization.
        """
        super().__init__(**kwargs)
        self.forms = forms or {}
        self.default_form = default_form
        self._validate_worklink_functions()

    async def stop(self) -> None:
        """
        Stops the worker and all associated work functions.
        """
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

    async def is_progressable(self) -> bool:
        """
        Checks if any work function is progressable and the worker is not stopped.
        """
        return any(
            [await i.is_progressable() for i in self.work_functions.values()]
        )

    async def change_default_form(self, form_key: str) -> None:
        """
        Changes the default form to the specified form key.
        """
        if form_key not in self.forms.keys():
            raise ValueError(
                f"Unable to change default form. Key {form_key} does not exist."
            )
        self.default_form = self.forms[form_key]

    def _get_decorated_functions(
        self, decorator_attr: str, name_only: bool = True
    ) -> list[str] | list[tuple[str, Callable, dict]]:
        """
        Retrieves decorated functions based on the specified decorator attribute.
        """
        decorated_functions = []
        for name, func in inspect.getmembers(
            self.__class__, predicate=inspect.isfunction
        ):
            if hasattr(func, decorator_attr):
                if name_only:
                    decorated_functions.append(name)
                else:
                    decorator_params = getattr(func, decorator_attr)
                    decorated_functions.append((name, func, decorator_params))
        return decorated_functions

    def _validate_worklink_functions(self) -> None:
        """
        Validates worklink functions to ensure they have the required parameters.
        """
        worklink_decorated_function = self._get_decorated_functions(
            decorator_attr="_worklink_decorator_params", name_only=False
        )
        for func_name, func, _ in worklink_decorated_function:
            func_signature = inspect.signature(func)
            if (
                "from_work" not in func_signature.parameters
                and "from_result" not in func_signature.parameters
            ):
                raise ValueError(
                    f'Either "from_work" or "from_result" must be a parameter in function {func_name}'
                )

    def construct_all_work_functions(self) -> None:
        """
        Constructs all work functions for the worker.
        """
        if getattr(self, "work_functions", None) is None:
            self.work_functions = {}
        work_decorated_function = self._get_decorated_functions(
            decorator_attr="_work_decorator_params", name_only=False
        )
        for func_name, func, dec_params in work_decorated_function:
            if func_name not in self.work_functions:
                self.work_functions[func_name] = WorkFunction(**dec_params)

    async def _work_wrapper(
        self,
        *args: Any,
        function: Callable | None = None,
        assignment: str | None = None,
        form_param_key: str | None = None,
        capacity: int | None = None,
        retry_kwargs: dict | None = None,
        guidance: str | None = None,
        refresh_time: float = 1,
        **kwargs: Any,
    ) -> Work:
        """
        Internal wrapper to handle work function execution.
        """
        if getattr(self, "work_functions", None) is None:
            self.work_functions = {}

        if function.__name__ not in self.work_functions:
            self.work_functions[function.__name__] = WorkFunction(
                assignment=assignment,
                function=function,
                retry_kwargs=retry_kwargs or {},
                guidance=guidance or function.__doc__,
                capacity=capacity,
                refresh_time=refresh_time,
            )

        work_func: WorkFunction = self.work_functions[function.__name__]

        # locate form that should be filled according to the assignment
        if form_param_key:
            func_signature = inspect.signature(function)
            if form_param_key not in func_signature.parameters:
                raise KeyError(
                    f'Failed to locate form. "{form_param_key}" is not defined in the function.'
                )
            if "self" in func_signature.parameters:
                bound_args = func_signature.bind(None, *args, **kwargs)
            else:
                bound_args = func_signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            arguments = bound_args.arguments

            form_key = arguments.get(form_param_key)
            try:
                form_key = ID.get_id(form_key)
            except:
                pass
            form = self.forms.get(form_key) or self.default_form

            if form:
                subform = form.__class__(
                    assignment=work_func.assignment,
                    guidance=work_func.guidance,
                    task=work_func.guidance,
                )
                # Copy fields from original form
                fields_to_copy = form.get_results()
                subform.fill_fields(**fields_to_copy)
                subform.origin = form
                kwargs = {"form": subform} | kwargs
            else:
                raise ValueError(
                    "Cannot locate form in Worker's forms and default_form is not available."
                )

        task = work_func.perform(self, *args, **kwargs)
        work = Work(async_task=task, async_task_name=work_func.name)
        await work_func.worklog.append(work)
        return work

    def to_log(self) -> Log:
        """Create a Log object summarizing this worker."""
        return Log(
            content={
                "type": "Worker",
                "id": str(self.id),
                "name": self.name,
                "work_functions": {
                    name: {
                        "id": str(func.id),
                        "assignment": func.assignment,
                        "guidance": func.guidance,
                        "pending_work": len(func.worklog.pending_work),
                        "completed_work": len(func.worklog.completed_work),
                    }
                    for name, func in self.work_functions.items()
                },
                "forms": {
                    name: str(form.id) for name, form in self.forms.items()
                },
                "default_form": self.default_form,
            }
        )


def work(
    assignment: str | None = None,
    form_param_key: str | None = None,
    capacity: int = 10,
    guidance: str | None = None,
    retry_kwargs: dict | None = None,
    timeout: int = 10,
    refresh_time: float = 1,
) -> Callable:
    """
    Decorator to mark a method as a work function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            self: Worker,
            *args: Any,
            func: Callable = func,
            assignment: str | None = assignment,
            form_param_key: str | None = form_param_key,
            capacity: int = capacity,
            retry_kwargs: dict | None = retry_kwargs,
            guidance: str | None = guidance,
            refresh_time: float = refresh_time,
            **kwargs: Any,
        ) -> Work:
            if not inspect.iscoroutinefunction(func):
                raise TypeError(
                    f"{func.__name__} must be an asynchronous function"
                )
            retry_kwargs = retry_kwargs or {}
            retry_kwargs["timeout"] = retry_kwargs.get("timeout", timeout)
            return await self._work_wrapper(
                *args,
                function=func,
                assignment=assignment,
                form_param_key=form_param_key,
                capacity=capacity,
                retry_kwargs=retry_kwargs,
                guidance=guidance,
                refresh_time=refresh_time,
                **kwargs,
            )

        wrapper._work_decorator_params = {
            "assignment": assignment,
            "function": func,
            "retry_kwargs": retry_kwargs,
            "guidance": guidance,
            "capacity": capacity,
            "refresh_time": refresh_time,
        }

        return wrapper

    return decorator


def worklink(from_: str, to_: str, auto_schedule: bool = True) -> Callable:
    """
    Decorator to create a link between two work functions.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            self: Worker,
            *args: Any,
            func: Callable = func,
            from_: str = from_,
            to_: str = to_,
            **kwargs: Any,
        ) -> Any:
            if not inspect.iscoroutinefunction(func):
                raise TypeError(
                    f"{func.__name__} must be an asynchronous function"
                )

            work_funcs = self._get_decorated_functions(
                decorator_attr="_work_decorator_params"
            )
            if from_ not in work_funcs or to_ not in work_funcs:
                raise ValueError(
                    "Invalid link. 'from_' and 'to_' must be the name of work decorated functions."
                )

            func_signature = inspect.signature(func)
            if (
                "from_work" not in func_signature.parameters
                and "from_result" not in func_signature.parameters
            ):
                raise ValueError(
                    f'Either "from_work" or "from_result" must be a parameter in function {func.__name__}'
                )

            if "self" in func_signature.parameters:
                bound_args = func_signature.bind(None, *args, **kwargs)
            else:
                bound_args = func_signature.bind(*args, **kwargs)
            bound_args.apply_defaults()
            arguments = bound_args.arguments
            if "kwargs" in arguments:
                arguments.update(arguments.pop("kwargs"))

            if from_work := arguments.get("from_work"):
                if not isinstance(from_work, Work):
                    raise ValueError(
                        "Invalid type for from_work. Only work objects are accepted."
                    )
                if from_work.async_task_name != from_:
                    raise ValueError(
                        f"Invalid work object in from_work. "
                        f'async_task_name "{from_work.async_task_name}" does not match from_ "{from_}"'
                    )

            next_params = await func(self, *args, **kwargs)
            to_work_func = getattr(self, to_)
            if next_params is None:
                return None

            if isinstance(next_params, list):
                if wrapper.auto_schedule:
                    return await to_work_func(*next_params)
            elif isinstance(next_params, dict):
                if wrapper.auto_schedule:
                    return await to_work_func(**next_params)
            elif isinstance(next_params, tuple) and len(next_params) == 2:
                if isinstance(next_params[0], list) and isinstance(
                    next_params[1], dict
                ):
                    if wrapper.auto_schedule:
                        return await to_work_func(
                            *next_params[0], **next_params[1]
                        )
                else:
                    raise TypeError(f"Invalid return type {func.__name__}")
            else:
                raise TypeError(f"Invalid return type {func.__name__}")

            return next_params

        wrapper.auto_schedule = auto_schedule
        wrapper._worklink_decorator_params = {
            "func": func,
            "from_": from_,
            "to_": to_,
        }

        return wrapper

    return decorator
