import asyncio
from functools import wraps

from .rate_limiter import RateLimitError


def invoke_retry(
    max_retries: int = 3, base_delay: int = 1, max_delay: int = 60
):
    def decorator(func):
        @wraps(func)
        async def wrapper(request_model, *args, **kwargs):
            if max_retries <= 0:
                raise ValueError(
                    "Invalid max number of retries. It must a positive integer."
                )

            for retry in range(max_retries + 1):
                try:
                    response_body = await func(request_model, *args, **kwargs)
                    return response_body
                except Exception as e:
                    # Last try used
                    if retry == max_retries:
                        raise e

                    # RateLimitError for Model only
                    if isinstance(e, RateLimitError):
                        if (
                            e.requested_tokens
                            > request_model.rate_limiter.limit_tokens
                        ):
                            raise ValueError(
                                "Requested tokens exceed the model's token limit. "
                                "Please modify the input, adjust the expected output tokens, or increase the token limit. "
                                f"The current token limit is {request_model.rate_limiter.limit_tokens} tokens."
                            )

                        while request_model.rate_limiter.unreleased_requests:
                            await asyncio.sleep(2)
                            request_model.rate_limiter.release_tokens()
                            if request_model.rate_limiter.check_availability(
                                request_token_len=e.requested_tokens
                            ):
                                break

                    elif error_code := getattr(
                        e, "status", None
                    ):  # http request errors
                        if (
                            error_code == 429
                            and "exceeded your current quota" in str(e)
                        ):  # RateLimitError (account quota reached)
                            raise e
                        if (
                            error_code == 429 or error_code >= 500
                        ):  # ServerError
                            if retry_after := getattr(e, "headers", {}).get(
                                "Retry-After"
                            ):
                                if retry_after.isdigit():
                                    await asyncio.sleep(int(retry_after))
                                    continue

                            wait_time = min(base_delay * (2**retry), max_delay)
                            await asyncio.sleep(wait_time)
                    else:
                        raise e

        return wrapper

    return decorator
