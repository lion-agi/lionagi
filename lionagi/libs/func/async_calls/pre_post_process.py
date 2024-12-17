from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar

from .ucall import ucall

F = TypeVar("F")

__all__ = ("pre_post_process",)


def pre_post_process(
    preprocess: Callable[..., Any] | None = None,
    postprocess: Callable[..., Any] | None = None,
    preprocess_args: Sequence[Any] = (),
    preprocess_kwargs: dict[str, Any] = {},
    postprocess_args: Sequence[Any] = (),
    postprocess_kwargs: dict[str, Any] = {},
) -> Callable[[F], F]:
    """Decorator to apply pre-processing and post-processing functions.

    Args:
        preprocess: Function to apply before the main function.
        postprocess: Function to apply after the main function.
        preprocess_args: Arguments for the preprocess function.
        preprocess_kwargs: Keyword arguments for preprocess function.
        postprocess_args: Arguments for the postprocess function.
        postprocess_kwargs: Keyword arguments for postprocess function.

    Returns:
        The decorated function.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            preprocessed_args = (
                [
                    await ucall(
                        preprocess,
                        arg,
                        *preprocess_args,
                        **preprocess_kwargs,
                    )
                    for arg in args
                ]
                if preprocess
                else args
            )
            preprocessed_kwargs = (
                {
                    k: await ucall(
                        preprocess,
                        v,
                        *preprocess_args,
                        **preprocess_kwargs,
                    )
                    for k, v in kwargs.items()
                }
                if preprocess
                else kwargs
            )
            result = await ucall(
                func, *preprocessed_args, **preprocessed_kwargs
            )

            return (
                await ucall(
                    postprocess,
                    result,
                    *postprocess_args,
                    **postprocess_kwargs,
                )
                if postprocess
                else result
            )

        return async_wrapper

    return decorator
