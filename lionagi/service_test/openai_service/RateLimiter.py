from collections import deque
from datetime import datetime

from pydantic import BaseModel, Field

from .CompleteRequestTokenInfo import CompleteRequestTokenInfo


class RateLimiter(BaseModel):
    limit_tokens: int = Field()

    limit_requests: int = Field()

    remaining_tokens: int = Field(default=None)

    remaining_requests: int = Field(default=None)

    last_check_timestamp: float = Field(default=None, description="Last time to check tokens and requests.")

    unreleased_tokens: deque = Field(default_factory=deque, description="completed request info for replenish", exclude=True)

    def append_complete_request_token_info(self, info: CompleteRequestTokenInfo):
        self.unreleased_tokens.append(info)
        if self.remaining_tokens:
            self.remaining_tokens -= info.token_usage
        else:
            self.remaining_tokens = self.limit_tokens - info.token_usage

        if self.remaining_requests:
            self.remaining_requests -= 1
        else:
            self.remaining_requests = self.limit_requests - 1

    def release_tokens(self):
        while self.unreleased_tokens:
            if datetime.now().timestamp() - self.unreleased_tokens[0].timestamp > 60:
                release_info = self.unreleased_tokens.popleft()
                self.remaining_tokens += release_info.token_usage
                self.remaining_requests += 1
            else:
                break

    def update_text_rate_limit(self, response_body, response_headers):
        # mainly for chat/completions and embedding endpoints
        total_token_usage = response_body["usage"]["total_tokens"]

        # rate limiter only tracks if there are token usage info
        request_datetime_header = response_headers.get("Date")
        date_format = "%a, %d %b %Y %H:%M:%S GMT"  # the format of the date string according to RFC 1123
        # (in http response header)
        dt = datetime.strptime(request_datetime_header, date_format)
        request_timestamp = dt.timestamp()

        complete_request_token_info = CompleteRequestTokenInfo(
            timestamp=request_timestamp, token_usage=total_token_usage
        )
        self.append_complete_request_token_info(
            complete_request_token_info
        )
