from lionagi.core.generic.node import Node
from lionagi.core.work.work_function import WorkFunction


class WorkFunctionNode(WorkFunction, Node):
    """
    A class representing a work function node, combining the functionality
    of a WorkFunction and a Node.

    Attributes:
        assignment (str): The assignment description of the work function.
        function (Callable): The function to be performed.
        retry_kwargs (dict): The retry arguments for the function.
        guidance (str): The guidance or documentation for the function.
        capacity (int): The capacity of the work queue batch processing.
        refresh_time (int): The time interval to refresh the work log queue.
    """

    def __init__(
        self,
        assignment,
        function,
        retry_kwargs=None,
        guidance=None,
        capacity=10,
        refresh_time=1,
        **kwargs,
    ):
        """
        Initializes a WorkFunctionNode instance.

        Args:
            assignment (str): The assignment description of the work function.
            function (Callable): The function to be performed.
            retry_kwargs (dict, optional): The retry arguments for the function. Defaults to None.
            guidance (str, optional): The guidance or documentation for the function. Defaults to None.
            capacity (int, optional): The capacity of the work queue batch processing. Defaults to 10.
            refresh_time (int, optional): The time interval to refresh the work log queue. Defaults to 1.
            **kwargs: Additional keyword arguments for the Node initialization.
        """
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
