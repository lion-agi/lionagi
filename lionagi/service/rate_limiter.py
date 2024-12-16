from collections import deque
from datetime import UTC, datetime, timezone

from pydantic import BaseModel, Field

from .complete_request_info import (
    CompleteRequestInfo,
    CompleteRequestTokenInfo,
)


class RateLimiter(BaseModel):
    limit_tokens: int = Field(default=None)

    limit_requests: int = Field(default=None)

    remaining_tokens: int = Field(default=None)

    remaining_requests: int = Field(default=None)

    last_check_timestamp: float = Field(
        default=None, description="Last time to check tokens and requests."
    )

    unreleased_requests: deque = Field(
        default_factory=deque,
        description="completed request info for replenish",
        exclude=True,
    )

    def append_complete_request_token_info(self, info: CompleteRequestInfo):
        if not self.limit_tokens and not self.limit_requests:
            # no limits
            return

        self.unreleased_requests.append(info)
        if self.limit_tokens and isinstance(info, CompleteRequestTokenInfo):
            # For request with token limits only
            if self.remaining_tokens:
                self.remaining_tokens -= info.token_usage
            else:
                self.remaining_tokens = self.limit_tokens - info.token_usage

        if self.limit_requests:
            if self.remaining_requests:
                self.remaining_requests -= 1
            else:
                self.remaining_requests = self.limit_requests - 1

    def release_tokens(self):
        self.last_check_timestamp = datetime.now(UTC).timestamp()
        while self.unreleased_requests:
            if (
                datetime.now(UTC).timestamp()
                - self.unreleased_requests[0].timestamp
                > 60
            ):
                release_info = self.unreleased_requests.popleft()
                if (
                    isinstance(release_info, CompleteRequestTokenInfo)
                    and self.remaining_tokens
                ):
                    self.remaining_tokens += release_info.token_usage
                if self.remaining_requests:
                    self.remaining_requests += 1
            else:
                break

    def update_rate_limit(
        self, request_datetime_header, total_token_usage: int = None
    ):
        # rate limiter tokens only tracks if there are token usage info
        # otherwise, tracks requests num
        date_format = "%a, %d %b %Y %H:%M:%S GMT"  # the format of the date string according to RFC 1123
        # (in http response header)
        dt = datetime.strptime(request_datetime_header, date_format)
        dt = dt.replace(tzinfo=timezone.utc)
        request_timestamp = dt.timestamp()

        if total_token_usage:
            complete_request_info = CompleteRequestTokenInfo(
                timestamp=request_timestamp, token_usage=total_token_usage
            )
        else:
            complete_request_info = CompleteRequestInfo(
                timestamp=request_timestamp
            )
        self.append_complete_request_token_info(complete_request_info)

    def check_availability(
        self, request_token_len: int = 0, estimated_output_len: int = 0
    ):
        if self.remaining_tokens is not None:
            if (
                request_token_len + estimated_output_len
                > self.remaining_tokens
            ):
                return False
        if self.remaining_requests is not None:
            if self.remaining_requests <= 0:
                return False
        return True


class RateLimitError(Exception):
    def __init__(self, message, input_token_len, estimated_output_len):
        super().__init__(message)
        self.requested_tokens = input_token_len + estimated_output_len
