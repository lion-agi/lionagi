import re
from typing import Generator
from .service_utils import BaseService



class BaseAPIService(BaseService):
    
    def __init__(self, api_key: str = None, 
                 status_tracker = None,
                 queue = None, endpoint=None, schema=None, 
                 ratelimiter=None, max_requests_per_minute=None, max_tokens_per_minute=None) -> None:
        self.api_key = api_key
        self.status_tracker = status_tracker
        self.queue = queue
        self.endpoint=endpoint
        self.schema = schema
        self.rate_limiter = ratelimiter(max_requests_per_minute, max_tokens_per_minute)
    
    @staticmethod                    
    def api_methods(http_session, method="post"):
        if method not in ["post", "delete", "head", "options", "patch"]:
            raise ValueError("Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']")
        elif method == "post":
            return http_session.post
        elif method == "delete":
            return http_session.delete
        elif method == "head":
            return http_session.head
        elif method == "options":
            return http_session.options
        elif method == "patch":
            return http_session.patch

    @staticmethod
    def api_endpoint_from_url(request_url: str) -> str:
        match = re.search(r"^https://[^/]+/v\d+/(.+)$", request_url)
        if match:
            return match.group(1)
        else:
            return ""

    @staticmethod
    def task_id_generator_function() -> Generator[int, None, None]:
        task_id = 0
        while True:
            yield task_id
            task_id += 1