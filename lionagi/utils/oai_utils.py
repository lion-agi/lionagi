# Standard Library
import os
import re
import json
import time
import logging
import http.client
from dataclasses import dataclass, field

# Third-Party
import dotenv
import asyncio
import aiohttp
import tiktoken

# Local
from .sys_utils import dict_to_temp

dotenv.load_dotenv('.env')
logging.basicConfig(level=logging.INFO)


def num_tokens_consumed_from_request(
    request_json: dict,
    api_endpoint: str,
    token_encoding_name: str,
):
    """Count the number of tokens in the request. Only supports completion and embedding requests."""
    encoding = tiktoken.get_encoding(token_encoding_name)
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

def task_id_generator_function():
    """Generate integers 0, 1, 2, and so on."""
    task_id = 0
    while True:
        yield task_id
        task_id += 1

def api_endpoint_from_url(request_url):
    """Extract the API endpoint from the request URL."""
    match = re.search("^https://[^/]+/v\\d+/(.+)$", request_url)
    return match[1]

def append_to_jsonl(data, filename: str) -> None:
    """Append a json payload to the end of a jsonl file."""
    json_string = json.dumps(data)
    with open(filename, "a") as f:
        f.write(json_string + "\n")

@dataclass
class StatusTracker:
    """
    Tracks the status of various tasks for API service.

    Attributes:
        num_tasks_started (int): Number of tasks that have been started.
        num_tasks_in_progress (int): Number of tasks currently in progress.
        num_tasks_succeeded (int): Number of tasks that have succeeded.
        num_tasks_failed (int): Number of tasks that have failed.
        num_rate_limit_errors (int): Number of tasks that failed due to rate limiting.
        num_api_errors (int): Number of tasks that failed due to API errors.
        num_other_errors (int): Number of tasks that failed due to other errors.
        time_of_last_rate_limit_error (int): The UNIX timestamp of the last rate limit error.
    """
    
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    time_of_last_rate_limit_error: int = 0

def process_api_requests_from_file(
    requests_filepath: str,
    save_filepath: str,
    request_url: str,
    api_key: str,
    max_requests_per_minute: float,
    max_tokens_per_minute: float,
    token_encoding_name: str,
    max_attempts: int,
    logging_level: int,
):
    seconds_to_pause_after_rate_limit_error = 15
    seconds_to_sleep_each_loop = 0.001

    logging.basicConfig(level=logging_level)
    logging.debug(f"Logging initialized at level {logging_level}")

    api_endpoint = api_endpoint_from_url(request_url)
    request_header = {"Authorization": f"Bearer {api_key}"}

    queue_of_requests_to_retry = []  # Replacing asyncio.Queue with a simple list
    task_id_generator = task_id_generator_function()
    status_tracker = StatusTracker()
    next_request = None

    available_request_capacity = max_requests_per_minute
    available_token_capacity = max_tokens_per_minute
    last_update_time = time.time()

    file_not_finished = True

    logging.debug(f"Initialization complete.")

    with open(requests_filepath) as file:
        requests = file.__iter__()
        logging.debug(f"File opened. Entering main loop")

        # Replace aiohttp.ClientSession with a synchronous HTTP client
        with http.client.HTTPConnection(api_endpoint) as session:
            while True:
                if next_request is None:
                    if queue_of_requests_to_retry:
                        next_request = queue_of_requests_to_retry.pop(0)
                        logging.debug(
                            f"Retrying request {next_request.task_id}: {next_request}"
                        )
                    elif file_not_finished:
                        try:
                            request_json = json.loads(next(requests))
                            next_request = APIRequest(
                                task_id=next(task_id_generator),
                                request_json=request_json,
                                token_consumption=num_tokens_consumed_from_request(
                                    request_json, api_endpoint, token_encoding_name
                                ),
                                attempts_left=max_attempts,
                                metadata=request_json.pop("metadata", None),
                            )
                            status_tracker.num_tasks_started += 1
                            status_tracker.num_tasks_in_progress += 1
                            logging.debug(
                                f"Reading request {next_request.task_id}: {next_request}"
                            )
                        except StopIteration:
                            logging.debug("Read file exhausted")
                            file_not_finished = False

                current_time = time.time()
                seconds_since_update = current_time - last_update_time
                available_request_capacity = min(
                    available_request_capacity
                    + max_requests_per_minute * seconds_since_update / 60.0,
                    max_requests_per_minute,
                )
                available_token_capacity = min(
                    available_token_capacity
                    + max_tokens_per_minute * seconds_since_update / 60.0,
                    max_tokens_per_minute,
                )
                last_update_time = current_time

                if next_request:
                    next_request_tokens = next_request.token_consumption
                    if (
                        available_request_capacity >= 1
                        and available_token_capacity >= next_request_tokens
                    ):
                        available_request_capacity -= 1
                        available_token_capacity -= next_request_tokens
                        next_request.attempts_left -= 1

                        # Synchronous API call
                        next_request.call_api(
                            session=session,
                            request_url=request_url,
                            request_header=request_header,
                            retry_queue=queue_of_requests_to_retry,
                            save_filepath=save_filepath,
                            status_tracker=status_tracker,
                        )
                        next_request = None

                if status_tracker.num_tasks_in_progress == 0:
                    break

                time.sleep(seconds_to_sleep_each_loop)

                seconds_since_rate_limit_error = (
                    time.time() - status_tracker.time_of_last_rate_limit_error
                )
                if (
                    seconds_since_rate_limit_error
                    < seconds_to_pause_after_rate_limit_error
                ):
                    remaining_seconds_to_pause = (
                        seconds_to_pause_after_rate_limit_error
                        - seconds_since_rate_limit_error
                    )
                    time.sleep(remaining_seconds_to_pause)
                    logging.warn(
                        f"Pausing to cool down until {time.ctime(status_tracker.time_of_last_rate_limit_error + seconds_to_pause_after_rate_limit_error)}"
                    )

    logging.info(
        f"""Parallel processing complete. Results saved to {save_filepath}"""
    )
    if status_tracker.num_tasks_failed > 0:
        logging.warning(
            f"{status_tracker.num_tasks_failed} / {status_tracker.num_tasks_started} requests failed. Errors logged to {save_filepath}."
        )
    if status_tracker.num_rate_limit_errors > 0:
        logging.warning(
            f"{status_tracker.num_rate_limit_errors} rate limit errors received. Consider running at a lower rate."
        )

def process_api_requests_from_dict(    
    d: dict,
    save_filepath: str,
    request_url: str,
    api_key: str,
    max_requests_per_minute: float,
    max_tokens_per_minute: float,
    token_encoding_name: str,
    max_attempts: int,
    logging_level: int):
    
    temp_file = dict_to_temp(d)  # Assuming dict_to_tempfile is synchronous
    
    process_api_requests_from_file(  # Assuming this function is now synchronous
        requests_filepath=temp_file.name,
        save_filepath=save_filepath,
        request_url=request_url,
        api_key=api_key,
        max_requests_per_minute=max_requests_per_minute,
        max_tokens_per_minute=max_tokens_per_minute,
        token_encoding_name=token_encoding_name,
        max_attempts=max_attempts,
        logging_level=logging_level,
    )
    
    os.remove(temp_file.name)

async def aprocess_api_requests_from_file(
    requests_filepath: str,
    save_filepath: str,
    request_url: str,
    api_key: str,
    max_requests_per_minute: float,
    max_tokens_per_minute: float,
    token_encoding_name: str,
    max_attempts: int,
    logging_level: int,
):
    """Processes API requests in parallel, throttling to stay under rate limits."""
    # constants
    seconds_to_pause_after_rate_limit_error = 15
    seconds_to_sleep_each_loop = (
        0.001  # 1 ms limits max throughput to 1,000 requests per second
    )

    # initialize logging
    logging.basicConfig(level=logging_level)
    logging.debug(f"Logging initialized at level {logging_level}")

    # infer API endpoint and construct request header
    api_endpoint = api_endpoint_from_url(request_url)
    request_header = {"Authorization": f"Bearer {api_key}"}

    # initialize trackers
    queue_of_requests_to_retry = asyncio.Queue()
    task_id_generator = (
        task_id_generator_function()
    )  # generates integer IDs of 1, 2, 3, ...
    status_tracker = (
        StatusTracker()
    )  # single instance to track a collection of variables
    next_request = None  # variable to hold the next request to call

    # initialize available capacity counts
    available_request_capacity = max_requests_per_minute
    available_token_capacity = max_tokens_per_minute
    last_update_time = time.time()

    # initialize flags
    file_not_finished = True  # after file is empty, we'll skip reading it
    logging.debug(f"Initialization complete.")

    # initialize file reading
    with open(requests_filepath) as file:
        # `requests` will provide requests one at a time
        requests = file.__iter__()
        logging.debug(f"File opened. Entering main loop")
        async with aiohttp.ClientSession() as session:  # Initialize ClientSession here
            while True:
                # get next request (if one is not already waiting for capacity)
                if next_request is None:
                    if not queue_of_requests_to_retry.empty():
                        next_request = queue_of_requests_to_retry.get_nowait()
                        logging.debug(
                            f"Retrying request {next_request.task_id}: {next_request}"
                        )
                    elif file_not_finished:
                        try:
                            # get new request
                            request_json = json.loads(next(requests))
                            next_request = APIRequest(
                                task_id=next(task_id_generator),
                                request_json=request_json,
                                token_consumption=num_tokens_consumed_from_request(
                                    request_json, api_endpoint, token_encoding_name
                                ),
                                attempts_left=max_attempts,
                                metadata=request_json.pop("metadata", None),
                            )
                            status_tracker.num_tasks_started += 1
                            status_tracker.num_tasks_in_progress += 1
                            logging.debug(
                                f"Reading request {next_request.task_id}: {next_request}"
                            )
                        except StopIteration:
                            # if file runs out, set flag to stop reading it
                            logging.debug("Read file exhausted")
                            file_not_finished = False

                # update available capacity
                current_time = time.time()
                seconds_since_update = current_time - last_update_time
                available_request_capacity = min(
                    available_request_capacity
                    + max_requests_per_minute * seconds_since_update / 60.0,
                    max_requests_per_minute,
                )
                available_token_capacity = min(
                    available_token_capacity
                    + max_tokens_per_minute * seconds_since_update / 60.0,
                    max_tokens_per_minute,
                )
                last_update_time = current_time

                # if enough capacity available, call API
                if next_request:
                    next_request_tokens = next_request.token_consumption
                    if (
                        available_request_capacity >= 1
                        and available_token_capacity >= next_request_tokens
                    ):
                        # update counters
                        available_request_capacity -= 1
                        available_token_capacity -= next_request_tokens
                        next_request.attempts_left -= 1

                        # call API
                        asyncio.create_task(
                            next_request.acall_api(
                                session=session,
                                request_url=request_url,
                                request_header=request_header,
                                retry_queue=queue_of_requests_to_retry,
                                save_filepath=save_filepath,
                                status_tracker=status_tracker,
                            )
                        )
                        next_request = None  # reset next_request to empty

                # if all tasks are finished, break
                if status_tracker.num_tasks_in_progress == 0:
                    break

                # main loop sleeps briefly so concurrent tasks can run
                await asyncio.sleep(seconds_to_sleep_each_loop)

                # if a rate limit error was hit recently, pause to cool down
                seconds_since_rate_limit_error = (
                    time.time() - status_tracker.time_of_last_rate_limit_error
                )
                if (
                    seconds_since_rate_limit_error
                    < seconds_to_pause_after_rate_limit_error
                ):
                    remaining_seconds_to_pause = (
                        seconds_to_pause_after_rate_limit_error
                        - seconds_since_rate_limit_error
                    )
                    await asyncio.sleep(remaining_seconds_to_pause)
                    # ^e.g., if pause is 15 seconds and final limit was hit 5 seconds ago
                    logging.warn(
                        f"Pausing to cool down until {time.ctime(status_tracker.time_of_last_rate_limit_error + seconds_to_pause_after_rate_limit_error)}"
                    )
        # after finishing, log final status
        logging.info(
            f"""Parallel processing complete. Results saved to {save_filepath}"""
        )
        if status_tracker.num_tasks_failed > 0:
            logging.warning(
                f"{status_tracker.num_tasks_failed} / {status_tracker.num_tasks_started} requests failed. Errors logged to {save_filepath}."
            )
        if status_tracker.num_rate_limit_errors > 0:
            logging.warning(
                f"{status_tracker.num_rate_limit_errors} rate limit errors received. Consider running at a lower rate."
            )
             
async def aprocess_api_requests_from_dict(    
    d: dict,
    save_filepath: str,
    request_url: str,
    api_key: str,
    max_requests_per_minute: float,
    max_tokens_per_minute: float,
    token_encoding_name: str,
    max_attempts: int,
    logging_level: int):
    temp_file = dict_to_temp(d)
    
    await aprocess_api_requests_from_file(
        requests_filepath = temp_file.name,
        save_filepath = save_filepath,
        request_url = request_url,
        api_key = api_key,
        max_requests_per_minute = max_requests_per_minute,
        max_tokens_per_minute = max_tokens_per_minute,
        token_encoding_name = token_encoding_name,
        max_attempts = max_attempts,
        logging_level = logging_level
    )
    
    os.remove(temp_file.name)
           
            
@dataclass
class APIRequest:
    """Stores an API request's inputs, outputs, and other metadata. Contains a method to make an API call."""

    task_id: int
    request_json: dict
    token_consumption: int
    attempts_left: int
    metadata: dict
    result: list = field(default_factory=list)

    async def acall_api(
        self,
        session: aiohttp.ClientSession,
        request_url: str,
        request_header: dict,
        retry_queue: asyncio.Queue,
        save_filepath: str,
        status_tracker: StatusTracker,
    ):
        """Calls the OpenAI API and saves results."""
        logging.info(f"Starting request #{self.task_id}")
        error = None
        try:
            async with session.post(
                url=request_url, headers=request_header, json=self.request_json
            ) as response:
                response = await response.json()
            if "error" in response:
                logging.warning(
                    f"Request {self.task_id} failed with error {response['error']}"
                )
                status_tracker.num_api_errors += 1
                error = response
                if "Rate limit" in response["error"].get("message", ""):
                    status_tracker.time_of_last_rate_limit_error = time.time()
                    status_tracker.num_rate_limit_errors += 1
                    status_tracker.num_api_errors -= (
                        1  # rate limit errors are counted separately
                    )

        except (
            Exception
        ) as e:  # catching naked exceptions is bad practice, but in this case we'll log & save them
            logging.warning(f"Request {self.task_id} failed with Exception {e}")
            status_tracker.num_other_errors += 1
            error = e
        if error:
            self.result.append(error)
            if self.attempts_left:
                retry_queue.put_nowait(self)
            else:
                logging.error(
                    f"Request {self.request_json} failed after all attempts. Saving errors: {self.result}"
                )
                data = (
                    [self.request_json, [str(e) for e in self.result], self.metadata]
                    if self.metadata
                    else [self.request_json, [str(e) for e in self.result]]
                )
                append_to_jsonl(data, save_filepath)
                status_tracker.num_tasks_in_progress -= 1
                status_tracker.num_tasks_failed += 1
        else:
            data = (
                [self.request_json, response, self.metadata]
                if self.metadata
                else [self.request_json, response]
            )
            append_to_jsonl(data, save_filepath)
            status_tracker.num_tasks_in_progress -= 1
            status_tracker.num_tasks_succeeded += 1
            logging.debug(f"Request {self.task_id} saved to {save_filepath}")

    def call_api(
        self,
        connection: http.client.HTTPConnection,  # Replacing aiohttp.ClientSession with http.client.HTTPConnection
        request_url: str,
        request_header: dict,
        retry_queue: list,  # Replacing asyncio.Queue with a simple list
        save_filepath: str,
        status_tracker: 'StatusTracker',  # Assuming StatusTracker is a custom class
    ):
        logging.info(f"Starting request #{self.task_id}")
        error = None
        try:
            # Synchronous API call using http.client
            connection.request(
                "POST", request_url, body=json.dumps(self.request_json), headers=request_header
            )
            response = connection.getresponse()
            response_data = json.loads(response.read().decode())
            
            if "error" in response_data:
                logging.warning(
                    f"Request {self.task_id} failed with error {response_data['error']}"
                )
                status_tracker.num_api_errors += 1
                error = response_data
                if "Rate limit" in response_data["error"].get("message", ""):
                    status_tracker.time_of_last_rate_limit_error = time.time()
                    status_tracker.num_rate_limit_errors += 1
                    status_tracker.num_api_errors -= 1  # rate limit errors are counted separately
        except Exception as e:  # General catch for exceptions
            logging.warning(f"Request {self.task_id} failed with Exception {e}")
            status_tracker.num_other_errors += 1
            error = e

        if error:
            self.result.append(error)
            if self.attempts_left:
                retry_queue.append(self)  # Replacing asyncio put_nowait with list append
            else:
                logging.error(
                    f"Request {self.request_json} failed after all attempts. Saving errors: {self.result}"
                )
                data = (
                    [self.request_json, [str(e) for e in self.result], self.metadata]
                    if self.metadata
                    else [self.request_json, [str(e) for e in self.result]]
                )
                append_to_jsonl(data, save_filepath)  # Assuming append_to_jsonl is synchronous
                status_tracker.num_tasks_in_progress -= 1
                status_tracker.num_tasks_failed += 1
        else:
            data = (
                [self.request_json, response_data, self.metadata]
                if self.metadata
                else [self.request_json, response_data]
            )
            append_to_jsonl(data, save_filepath)  # Assuming append_to_jsonl is synchronous
            status_tracker.num_tasks_in_progress -= 1
            status_tracker.num_tasks_succeeded += 1
            logging.debug(f"Request {self.task_id} saved to {save_filepath}")
    
            
class RateLimitedAPIService:
    """
    A class to handle rate-limited API service calls.

    Args:
        api_key (str): The API key for authentication.
        max_requests_per_minute (int): The maximum number of requests allowed per minute.
        max_tokens_per_minute (int): The maximum number of tokens allowed per minute.
        token_encoding_name (str): The encoding name for tokens.
        max_attempts (int): The maximum number of attempts for each API call.

    Attributes:
        available_request_capacity (int): The available request capacity.
        available_token_capacity (int): The available token capacity.
        last_update_time (float): The last time the capacity was updated.
    """
    
    def __init__(self, api_key, max_requests_per_minute, max_tokens_per_minute, token_encoding_name="utf-8", max_attempts=3, request_url="https://api.openai.com/v1/chat/completions", save_file_path=None, logging_level=logging.INFO):
        self.request_url = request_url
        self.api_key = api_key
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.logging_level = logging_level
        self.save_file_path = save_file_path
        
    def call_api(self, payload, input_kind="dict", request_url=None):
        request_url = request_url if request_url else self.request_url
        if input_kind == "dict":
            process_api_requests_from_dict(  # Assuming this function is now synchronous
                d=payload, 
                save_filepath=self.save_file_path, 
                request_url=request_url,
                api_key=self.api_key,
                max_requests_per_minute=self.max_requests_per_minute,
                max_tokens_per_minute=self.max_tokens_per_minute,
                token_encoding_name=self.token_encoding_name,
                max_attempts=self.max_attempts,
                logging_level=self.logging_level
            )
        elif input_kind == "file":
            process_api_requests_from_file(  # Assuming this function is now synchronous
                requests_filepath=payload, 
                save_filepath=self.save_file_path, 
                request_url=request_url,
                api_key=self.api_key,
                max_requests_per_minute=self.max_requests_per_minute,
                max_tokens_per_minute=self.max_tokens_per_minute,
                token_encoding_name=self.token_encoding_name,
                max_attempts=self.max_attempts,
                logging_level=self.logging_level
            )
    
    async def acall_api(self, payload, input_kind="dict", request_url=None):
        request_url = request_url if request_url else self.request_url
        if input_kind == "dict":
            await aprocess_api_requests_from_dict(
                d = payload, 
                save_filepath=self.save_file_path, 
                request_url=request_url,
                api_key=self.api_key,
                max_requests_per_minute=self.max_requests_per_minute,
                max_tokens_per_minute=self.max_tokens_per_minute,
                token_encoding_name=self.token_encoding_name,
                max_attempts=self.max_attempts,
                logging_level=self.logging_level
            )
        elif input_kind == "file":
            await aprocess_api_requests_from_file(
                requests_filepath=payload, 
                save_filepath=self.save_file_path, 
                request_url=request_url,
                api_key=self.api_key,
                max_requests_per_minute=self.max_requests_per_minute,
                max_tokens_per_minute=self.max_tokens_per_minute,
                token_encoding_name=self.token_encoding_name,
                max_attempts=self.max_attempts,
                logging_level=self.logging_level
            )


gpt4_api_service = RateLimitedAPIService(
    api_key = os.getenv("OPENAI_API_KEY"),
    max_requests_per_minute=10000,
    max_tokens_per_minute=150000
)

gpt3_api_service = RateLimitedAPIService(
    api_key = os.getenv("OPENAI_API_KEY"),
    max_requests_per_minute=10000,
    max_tokens_per_minute=1000000
)

gpt3_instruct_api_service = RateLimitedAPIService(
    api_key=os.getenv("OPENAI_API_KEY"),
    max_requests_per_minute=3000,
    max_tokens_per_minute=250000
)

status_tracker = StatusTracker()