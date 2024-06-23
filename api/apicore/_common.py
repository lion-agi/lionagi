from sys import exit
from functools import wraps
from logging import Logger as Log


def info_logger(
    message: str | None = "",
    func_str: str | None = "",
    logger: Log | None = None,
    addition_msg: str | None = "",
):
    """Logs a formatted message or prints it if no logger is provided.

    This function formats a message by optionally prefixing it with a function string,
    then logs the message using the provided logger object. If no logger is provided,
    the message is printed to the console. An additional message can be appended.
    If an error occurs during logging, the exception is caught and raised.

    Args:
        message (str | None): The main message to be logged. Defaults to an empty string.
        func_str (str | None): A prefix string, usually representing a function name,
                               to be added to the start of the message. Defaults to an empty string.
        logger (Log | None): The logging object to use for logging the message. If None,
                             the message will be printed using the print function. Defaults to None.
        addition_msg (str | None): An additional message to append to the end of the
                                   main message. Defaults to an empty string.

    Raises:
        Exception: Propagates any exception that occurs during the logging process.
    """

    try:
        if func_str:
            message = f"{func_str}: {message}"
        (
            logger.info(f"{message} {addition_msg}")
            if logger
            else print(f"{message} {addition_msg}")
        )
    except Exception as err:
        raise err


def error_logger(
    func_str: str | None,
    error: str | None,
    logger: Log | None = None,
    addition_msg: str | None = "",
    mode: str | None = "critical",
    ignore_flag: bool = True,
    set_trace: bool = False,
) -> None:
    """
    Logs or prints an error message constructed from the provided arguments. This function
    supports logging with different levels (critical, debug, error, info) and can optionally
    trigger a trace logging for the exception. If no logger is provided, it falls back to
    printing the error message. Additionally, it can exit the program with a specific status
    code if the ignore_flag is False.

    Args:
        func_str (str | None): The name of the function where the error occurred.
            Used for constructing the error message.
        error (str | None): The error message to be logged or printed.
        logger (Log | None, optional): The logging object to use for logging the error.
            If None, the error message is printed instead. Defaults to None.
        addition_msg (str | None, optional): Additional message to include in the error
            message. Defaults to an empty string.
        mode (str | None, optional): The logging level to use. Valid options are
            "critical", "debug", "error", "info". Defaults to "critical".
        ignore_flag (bool, optional): If False, the function will exit the program with
            status code 99. Defaults to True, meaning the error is logged or printed, but
            the program continues execution.
        set_trace (bool, optional): If True and a logger is provided, logs an exception
            trace. Defaults to False.

    Returns:
        None: The function does not return any value. It may exit the program depending
            on the ignore_flag.
    """

    if logger:
        logger_mode = {
            "critical": logger.critical,
            "debug": logger.debug,
            "error": logger.error,
            "info": logger.info,
        }
    try:
        (
            logger_mode.get(mode, logger_mode)(
                f"Error in {func_str} {addition_msg} {error}"
            )
            if logger
            else print(f"Error in {func_str} {addition_msg} {error}")
        )
        if logger and set_trace:
            logger.exception("trace")
        return exit(99) if not ignore_flag else None
    except Exception as err:
        raise err


def exception_handlers(logger: Log | None = None):
    """
    A decorator that wraps a function with exception handling logic.

    If an exception occurs during the execution of the wrapped function, it logs the
    exception using a provided logger or a default logging mechanism defined in
    the `error_logger` function. This allows for centralized error logging and
    handling for functions that use this decorator.

    Args:
        logger (Log | None): An optional logger object to log exceptions. If not provided,
                             the default logging mechanism inside `error_logger` will be used.

    Returns:
        Callable: A decorator that wraps functions with exception handling logic.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                error_logger(
                    func.__name__, err, logger=logger, mode="error", ignore_flag=False
                )

        return wrapper

    return decorator


class mockawsclient:
    def __call__(self, *args, **kwargs):
        return {"ResponseMetadata":
            {
                "HTTPStatusCode": 200
            }
        }

    def __getattr__(self, name):
        return self