class Throttle:
    """
    A class that provides a throttling mechanism for function calls.

    When used as a decorator, it ensures that the decorated function can only be called
    once per specified period. Subsequent calls within this period are delayed to enforce
    this constraint.

    Attributes:
            period (int): The minimum time period (in seconds) between successive calls.

    Methods:
            __call__: Decorates a synchronous function with throttling.
            __call_async__: Decorates an asynchronous function with throttling.
    """

    def __init__(self, period: int) -> None:
        """
        Initializes a new instance of _Throttle.

        Args:
                period (int): The minimum time period (in seconds) between successive calls.
        """
        self.period = period
        self.last_called = 0

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorates a synchronous function with the throttling mechanism.

        Args:
                func (Callable[..., Any]): The synchronous function to be throttled.

        Returns:
                Callable[..., Any]: The throttled synchronous function.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = SysUtil.get_now(datetime_=False) - self.last_called
            if elapsed < self.period:
                SysUtil.sleep(self.period - elapsed)
            self.last_called = SysUtil.get_now(datetime_=False)
            return func(*args, **kwargs)

        return wrapper

    async def __call_async__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorates an asynchronous function with the throttling mechanism.

        Args:
                func (Callable[..., Any]): The asynchronous function to be throttled.

        Returns:
                Callable[..., Any]: The throttled asynchronous function.
        """

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            elapsed = SysUtil.get_now(datetime_=False) - self.last_called
            if elapsed < self.period:
                await AsyncUtil.sleep(self.period - elapsed)
            self.last_called = SysUtil.get_now(datetime_=False)
            return await func(*args, **kwargs)

        return wrapper
