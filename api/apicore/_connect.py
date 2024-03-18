from contextlib import contextmanager
from typing import Callable
from logging import Logger as Log
from inspect import currentframe
from types import SimpleNamespace
from functools import wraps
from api.apicore import _meta as _meta_
from api.apicore import _common as _common_
from api.apicore import _config as _config_
from api.aws import _aws_s3 #this line needs to be present to dynamically load the API object at startup

@_common_.exception_handlers()
@contextmanager
def create_session(
        object_type: str | None,
        logger: Log | None = None
    ) -> Callable:
    """
    This function initializes a session for a given object type by leveraging a configuration
    singleton and an API object registration singleton. It looks up the requested object type
    in the registered objects dictionary. If the object type is found, it yields a new session
    object pointer for that type, initialized with the singleton configuration. If the object
    type is not found, it logs an error message listing the supported object types.

    Args:
        object_type (str): The type of the object for which to create a session.
        logger (Log, optional): A logger object for logging error messages. Defaults to None,
                                in which case a default logger is used.

    Return:
        Callable: A pointer to the session object of the requested type, initialized with
                  the configuration. If the requested object type is not found, it yields None.

    Raises:
        Exception: If the object type is not found, it logs the error and yields None without
                   raising an exception. However, it's implied that the `error_logger` function
                   might raise exceptions depending on its implementation.

    """
    config = _config_.ConfigSingleton()
    object_dict = {object_name.lower(): object_val for object_name, object_val in
                    _meta_.APIObjectSingleton().object_registration.items()}

    if object_type.lower() not in object_dict.keys():
        _common_.error_logger(currentframe().f_code.co_name,
                              f"{object_type} is not found, currently {' '.join(object_dict.keys())} are supported",
                              logger=logger,
                              mode="error",
                              ignore_flag=False)
    yield object_dict.get(object_type.lower(), None).get("object_ptr")(config)


def object_binding(
        object_type: str | None,
        object_name: str | None = "",
        variable_name: str | None = "action"
    ) -> Callable:
    """
    Binds a session object of a specified type to the decorated function.
    This function generates a decorator that, when applied to another function, dynamically injects
    a session object into that function's arguments based on the specified `object_type` and optionally
    `object_name`. The session object is accessed or created via `create_session` and is inserted into
    the function's arguments under `variable_name`.

    Args:
        object_type (str): The type of the object session to be created or accessed.
        object_name (str, optional): The name of the object within the session to specifically bind.
                                     If not provided, the entire session object is bound. Defaults to an empty string.
        variable_name (str, optional): The name of the variable under which the session object (or the specified
                                       object within the session) is to be injected into the decorated function's
                                       arguments. Defaults to 'action'.

    Returns:
        Callable: A decorator that, when applied to a function, injects a session object or a specific object
                  within that session into the function's arguments.

    Note:
        The session object is retrieved or created using the `create_session` function, which should yield a
        session object for the specified `object_type`. The `object_binding` decorator enhances the flexibility
        of function signatures by allowing them to implicitly receive complex objects without altering their
        explicit arguments list.

    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            arg_session = variable_name
            func_params = func.__code__.co_varnames

            session_in_args = arg_session in func_params and func_params.index(arg_session) < len(args)
            session_in_kwargs = arg_session in kwargs

            if (session_in_args or session_in_kwargs) and variable_name in kwargs and object_type in kwargs.get(variable_name).__dict__:
                if object_name is None or object_name in kwargs.get(variable_name).__dict__.get(object_type).__dict__:

                    return func(*args, **kwargs)
            else:

                with create_session(object_type) as session:
                    if session:
                        if object_name:
                            object_name_namespace = SimpleNamespace(**{object_name: session})
                            kwargs[variable_name] = SimpleNamespace(**{object_type: object_name_namespace})
                        else:
                            kwargs[variable_name] = session
                return func(*args, **kwargs)
        return wrapper
    return decorator


def get_object(
        object_name: str | None,
        logger: Log | None = None
    ) -> object:
    """
    Retrieves an object by its name and logs errors if any exceptions are encountered.
    This function attempts to retrieve an object specified by `object_name` using
    the `object_binding` decorator. The decorator is applied to a temporary lambda
    function, which effectively serves to fetch the desired object. If the object retrieval
    process raises an exception, the error is logged using a provided logger object.

    Args:
        object_name (str | None): The name of the object to retrieve. If None, the behavior
                                  of the `object_binding` decorator will determine the outcome.
        logger (Log | None): An optional logger object for logging exceptions that occur during
                             the object retrieval process. Defaults to None, in which case a
                             default logging mechanism may be used.
    Returns:
        The requested object if found and accessible; otherwise, this function may return `None`
        or behave according to the `object_binding` decorator's implementation when the object
        name is not provided or an error occurs.

    Note:
        The use of the `object_binding` decorator in this context demonstrates an advanced pattern
        of leveraging decorators for dynamic resource access and management, showcasing flexibility
        in handling dependencies within functions.
    """
    try:
        return object_binding(object_name)(lambda action: action)()
    except Exception as err:
        _common_.error_logger(currentframe().f_code.co_name,
                              err,
                              logger=logger,
                              mode="error",
                              ignore_flag=False)