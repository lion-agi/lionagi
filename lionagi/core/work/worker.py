import inspect
from abc import ABC
from functools import wraps

from lionagi import logging as _logging
from lionagi.core.collections.abc import get_lion_id
from lionagi.core.report.form import Form
from lionagi.core.work.work import Work
from lionagi.core.work.work_function import WorkFunction


class Worker(ABC):
    """
    This class represents a worker that handles multiple work functions.

    Attributes:
        name (str): The name of the worker.
        work_functions (dict[str, WorkFunction]): Dictionary mapping assignments to WorkFunction objects.
        forms (dict[str, Form]): Dictionary mapping form identifier to Form objects.
        default_form (str|None): The default form to be used by the worker.
    """

    name: str = "Worker"

    def __init__(self, forms=None, default_form=None) -> None:
        """
        Initializes a new instance of Worker.

        Args:
            forms (dict[str, Form], optional): Dictionary mapping form identifier to Form objects.
            default_form (str|None, optional): The default form to be used by the worker.
        """
        self.work_functions: dict[str, WorkFunction] = {}
        self.forms: dict[str, Form] = forms or {}
        self.default_form = default_form
        self._validate_worklink_functions()

    async def stop(self):
        """
        Stops the worker and all associated work functions.
        """
        # self.stopped = True
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
            any(
                [
                    await i.is_progressable()
                    for i in self.work_functions.values()
                ]
            )
            and not self.stopped
        )

    async def change_default_form(self, form_key):
        """
        Changes the default form to the specified form key.

        Args:
            form_key (str): The key of the form to set as the default.

        Raises:
            ValueError: If the form key does not exist in the forms dictionary.

        """
        if form_key not in self.forms.keys():
            raise ValueError(
                f"Unable to change default form. Key {form_key} does not exist."
            )
        self.default_form = self.forms[form_key]

    def _get_decorated_functions(self, decorator_attr, name_only=True):
        """
        Retrieves decorated functions based on the specified decorator attribute.

        Args:
            decorator_attr (str): The attribute name of the decorator.
            name_only (bool, optional): Whether to return only the function names. Defaults to True.

        Returns:
            list: List of decorated function names or tuples containing function details.
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

    def _validate_worklink_functions(self):
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

    def construct_all_work_functions(self):
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
        *args,
        function=None,
        assignment=None,
        form_param_key=None,
        capacity=None,
        retry_kwargs=None,
        guidance=None,
        refresh_time=1,
        **kwargs,
    ):
        """
        Internal wrapper to handle work function execution.

        Args:
            func (Callable): The function to be executed.
            assignment (str): The assignment description.
            form_param_key (str): The key to identify the form parameter in
                the function's signature. This parameter is used to locate and fill
                the appropriate form according to the assignment. Raises an error
                if the form parameter key is not found in the function's signature.
            capacity (int): Capacity for the work queue batch processing.
            retry_kwargs (dict): Retry arguments for the function.
            guidance (str): Guidance or documentation for the function.
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
                form_key = get_lion_id(form_key)
            except:
                pass
            form = self.forms.get(form_key) or self.default_form

            if form:
                subform = form.__class__(
                    assignment=work_func.assignment, task=work_func.guidance
                )
                for k in subform.input_fields:
                    v = getattr(form, k, None)
                    setattr(subform, k, v)
                subform.origin = form
                kwargs = {"form": subform} | kwargs
            else:
                raise ValueError(
                    f"Cannot locate form in Worker's forms and default_form is not available."
                )

        task = work_func.perform(self, *args, **kwargs)
        work = Work(async_task=task, async_task_name=work_func.name)
        await work_func.worklog.append(work)
        return work


def work(
    assignment=None,
    form_param_key=None,
    capacity=10,
    guidance=None,
    retry_kwargs=None,
    timeout=10,
    refresh_time=1,
):
    """
    Decorator to mark a method as a work function.

    Args:
        assignment (str): The assignment description of the work function.
        form_param_key (str): The key to identify the form parameter in
                the function's signature. This parameter is used to locate and fill
                the appropriate form according to the assignment. Raises an error
                if the form parameter key is not found in the function's signature.
        capacity (int): Capacity for the work queue batch processing.
        guidance (str): Guidance or documentation for the work function.
        retry_kwargs (dict): Retry arguments for the work function.
        timeout (int): Timeout for the work function.
        refresh_time (int, optional): Refresh time for the work log queue.

    Returns:
        Callable: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(
            self: Worker,
            *args,
            func=func,
            assignment=assignment,
            form_param_key=form_param_key,
            capacity=capacity,
            retry_kwargs=retry_kwargs,
            guidance=guidance,
            refresh_time=refresh_time,
            **kwargs,
        ):
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


def worklink(from_: str, to_: str, auto_schedule: bool = True):
    """
    Decorator to create a link between two work functions.

    Args:
        from_ (str): The name of the source work function.
        to_ (str): The name of the target work function.
        auto_schedule (bool, optional): Whether to automatically schedule the next work function. Defaults to True.

    Returns:
        Callable: The decorated function.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(
            self: Worker, *args, func=func, from_=from_, to_=to_, **kwargs
        ):
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
                return
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


# # Example
# from lionagi import Session
# from lionagi.experimental.work.work_function import work


# class MyWorker(Worker):

#     @work(assignment="instruction, context -> response")
#     async def chat(instruction=None, context=None):
#         session = Session()
#         return await session.chat(instruction=instruction, context=context)


# await a.chat(instruction="Hello", context={})
