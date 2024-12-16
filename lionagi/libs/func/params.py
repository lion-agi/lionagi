"""Parameter models for function execution configurations.

This module defines Pydantic models that specify parameters for various function
execution patterns including timed calls and retry logic.
"""

from collections.abc import Callable

from pydantic import BaseModel, Field

from lionagi.libs.constants import UNDEFINED, UndefinedType


class TimedCallParams(BaseModel):

    initial_delay: int = Field(
        default=0,
        ge=0,
        description="Delay in seconds before function execution",
    )
    retry_default: str | UndefinedType = Field(
        default=UNDEFINED,
        description="Value to return if an error occurs and suppress_err is True",
    )
    retry_timeout: int | None = Field(
        default=None,
        ge=0,
        description="Timeout in seconds for function execution. None means no timeout",
    )
    retry_timing: bool = Field(
        default=False,
        description="If True, return execution duration along with result",
    )
    error_msg: str | None = Field(
        default=None, description="Custom error message prefix for exceptions"
    )
    error_map: dict[type[Exception], Callable[[Exception], None]] | None = (
        Field(
            default=None,
            description="Dictionary mapping exception types to error handler functions",
        )
    )


class RetryCallParams(TimedCallParams):

    num_retries: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts after initial failure",
    )
    retry_delay: int = Field(
        default=0,
        ge=0,
        description="Base delay in seconds between retry attempts",
    )
    backoff_factor: int = Field(
        default=1,
        ge=1,
        description="Factor to multiply retry_delay by after each attempt",
    )
    verbose_retry: bool = Field(
        default=False, description="If True, print retry attempt messages"
    )
