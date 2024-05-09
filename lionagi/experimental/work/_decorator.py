from functools import wraps
import asyncio
from ._work._work import Work
from ._work._function import WorkFunction

def work(assignment, capacity=5, refresh_time=1):
    """
    Decorator to convert a function into a WorkFunction managed by a Worker. This decorator
    handles the instantiation and management of WorkFunction objects and appends new work
    to the worklog asynchronously.

    Args:
        assignment (str): A unique identifier or description for the type of work.
        capacity (int, optional): Maximum number of concurrent tasks that can be handled by the WorkFunction.
        refresh_time (float, optional): The time to wait after processing each batch of tasks.

    Returns:
        Callable: A wrapped asynchronous function that manages tasks via WorkFunction.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, retry_kwargs=None, manual=None, **kwargs):
            if getattr(self, "work_functions", None) is None:
                self.work_functions = {}
            
            # Cache the WorkFunction instance using the function's name to avoid duplicates
            if func.__name__ not in self.work_functions:                
                self.work_functions[func.__name__] = WorkFunction(
                    assignment=assignment,
                    function=func,
                    retry_kwargs=retry_kwargs or {},
                    manual=manual or func.__doc__,
                    capacity=capacity, 
                    refresh_time=refresh_time
                )
                
            work_func = self.work_functions[func.__name__]
            
            # Perform the work function, passing all necessary arguments
            task = asyncio.create_task(work_func.perform(self, *args, **kwargs))
            work = Work(async_task=task)
            
            # Append the work to the log and ensure it is processed
            await work_func.worklog.append(work)
            return True
        
        return wrapper
    return decorator
