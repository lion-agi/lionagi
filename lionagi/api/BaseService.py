import asyncio
import json
import logging
import time
from dataclasses import dataclass
import tiktoken
import re
from abc import ABC


@dataclass
class StatusTracker:
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    
class BaseAPIService(ABC):
    """
    An abstract base class for API services that includes rate limiting
    and error handling mechanisms.

    Attributes:
        api_key (str): The API key used for authentication with the API service.
        max_requests_per_minute (int): The maximum number of requests allowed per minute.
        max_tokens_per_minute (int): The maximum number of tokens allowed to be used per minute.
        token_encoding_name (str): The encoding scheme used for the tokens.
        max_attempts (int): The maximum number of attempts to try a request.
        available_request_capacity (int): The current available request capacity.
        available_token_capacity (int): The current available token capacity.
        last_update_time (float): The last time the capacities were updated.
        rate_limit_task (asyncio.Task): The background task that replenishes rate limits.

    Methods:
        handle_error(self, error, request_json, metadata, save_filepath, status_tracker):
            Handles errors by decrementing the in-progress task count, incrementing the failed task count,
            and appending the error to a specified JSONL file.

        append_to_jsonl(self, data, filename):
            Appends a piece of data to a file in JSON Lines format.

    Raises:
        NotImplementedError: If an abstract method is not implemented by a subclass.
    """    
    def __init__(self, api_key, max_requests_per_minute, 
                 max_tokens_per_minute, 
                 token_encoding_name, max_attempts):
        self.api_key = api_key
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
        self.last_update_time = time.time()
        self.rate_limit_task = asyncio.create_task(self.rate_limit_replenisher())

    def handle_error(self, error, request_json, metadata, save_filepath, status_tracker):
        """
        Handles errors by logging and saving details to a file.

        Args:
            error (Exception): The exception that occurred.
            request_json (Dict[str, Any]): The request data that led to the error.
            metadata (Dict[str, Any]): Additional metadata related to the request.
            save_filepath (str): The file path to save error details.
            status_tracker ('StatusTracker'): An object tracking the status of tasks.

        Side effects:
            Logs an error message.
            Decrements the number of tasks in progress.
            Increments the number of tasks failed.
            Appends error details to the specified file.
        """        
        status_tracker.num_tasks_in_progress -= 1
        status_tracker.num_tasks_failed += 1
        data = (
            [request_json, [str(error)], metadata] 
            if metadata 
            else [request_json, [str(error)]]
        )
        self.append_to_jsonl(data, save_filepath)
        logging.error(f"Request failed after all attempts. Saving errors: {data}")

    def append_to_jsonl(self, data, filename):
        """
        Appends data to a file in JSON Lines format.

        Args:
            data (Any): The data to be appended.
            filename (str): The file to which the data should be appended.

        Side effects:
            Writes to the specified file.
        """        
        json_string = json.dumps(data)
        with open(filename, "a") as f:
            f.write(json_string + "\n")

    def num_tokens_consumed_from_request(self, request_json: dict, api_endpoint: str):
        """Count the number of tokens in the request. Only supports completion and embedding requests."""
        encoding = tiktoken.get_encoding(self.token_encoding_name)
        # if completions request, tokens = prompt + n * max_tokens
        if api_endpoint.endswith("completions"):
            max_tokens = request_json.get("max_tokens", 15)
            n = request_json.get("n", 1)
            completion_tokens = n * max_tokens

            # chat completions
            if api_endpoint.startswith("chat/"):
                num_tokens = 0
                for message in request_json["messages"]:
                    num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                    for key, value in message.items():
                        num_tokens += len(encoding.encode(value))
                        if key == "name":  # if there's a name, the role is omitted
                            num_tokens -= 1  # role is always required and always 1 token
                num_tokens += 2  # every reply is primed with <im_start>assistant
                return num_tokens + completion_tokens
            # normal completions
            else:
                prompt = request_json["prompt"]
                if isinstance(prompt, str):  # single prompt
                    prompt_tokens = len(encoding.encode(prompt))
                    num_tokens = prompt_tokens + completion_tokens
                    return num_tokens
                elif isinstance(prompt, list):  # multiple prompts
                    prompt_tokens = sum([len(encoding.encode(p)) for p in prompt])
                    num_tokens = prompt_tokens + completion_tokens * len(prompt)
                    return num_tokens
                else:
                    raise TypeError(
                        'Expecting either string or list of strings for "prompt" field in completion request'
                    )
        # if embeddings request, tokens = input tokens
        elif api_endpoint == "embeddings":
            input = request_json["input"]
            if isinstance(input, str):  # single input
                num_tokens = len(encoding.encode(input))
                return num_tokens
            elif isinstance(input, list):  # multiple inputs
                num_tokens = sum([len(encoding.encode(i)) for i in input])
                return num_tokens
            else:
                raise TypeError(
                    'Expecting either string or list of strings for "inputs" field in embedding request'
                )
        # more logic needed to support other API calls (e.g., edits, inserts, DALL-E)
        else:
            raise NotImplementedError(
                f'API endpoint "{api_endpoint}" not implemented in this script'
            )
    
    async def rate_limit_replenisher(self):
        """
        An asynchronous task that replenishes rate limits based on the set intervals.
        """
        while True:
            await asyncio.sleep(60)  # Replenish every minute
            self.available_request_capacity = self.max_requests_per_minute
            self.available_token_capacity = self.max_tokens_per_minute
    
    @staticmethod
    def api_endpoint_from_url(request_url):
        """Extract the API endpoint from the request URL."""
        match = re.search("^https://[^/]+/v\\d+/(.+)$", request_url)
        return match[1]
    
    @staticmethod
    def task_id_generator_function():
        """Generate integers 0, 1, 2, and so on."""
        task_id = 0
        while True:
            yield task_id
            task_id += 1