import asyncio
import json
import logging
import time
import dotenv
import os
from dataclasses import dataclass

dotenv.load_dotenv('.env')
logging.basicConfig(level=logging.INFO)

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


# Class definition
import asyncio
import logging
import time

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
    def __init__(self, api_key, max_requests_per_minute, max_tokens_per_minute, token_encoding_name, max_attempts):
        self.api_key = api_key
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
        self.last_update_time = time.time()

    def update_capacity(self):
        """
        Updates the available request and token capacities based on the time elapsed 
        since the last update. The capacities are replenished at rates defined by 
        `max_requests_per_minute` and `max_tokens_per_minute`.
        
        The method calculates the amount of time that has elapsed since the last update, 
        and then uses this to proportionally increase the available capacities. The capacities 
        are capped at their respective maximum limits.
        
        Finally, the last update time is set to the current time.
        """
        current_time = time.time()
        seconds_since_update = current_time - self.last_update_time
        self.available_request_capacity = min(
            self.available_request_capacity + (self.max_requests_per_minute * seconds_since_update / 60.0),
            self.max_requests_per_minute,
        )
        self.available_token_capacity = min(
            self.available_token_capacity + (self.max_tokens_per_minute * seconds_since_update / 60.0),
            self.max_tokens_per_minute,
        )
        self.last_update_time = current_time

    async def call_api(self, session, request_url, payload):
        """
        Asynchronously calls the API using aiohttp, handling rate limits and retries.
        
        Firstly, this method updates the available capacity for API calls by invoking `update_capacity()`.
        If sufficient capacity is available, it proceeds to make the API call.
        
        The method tries to post to the `request_url` with the provided `payload`. 
        If the API call fails due to rate-limiting or other errors, retries are attempted based 
        on `max_attempts`.

        Args:
            session (aiohttp.ClientSession): The aiohttp client session.
            request_url (str): The API endpoint URL.
            payload (dict): The payload for the API request.
            
        Returns:
            dict: The API response if successful.
            
        Raises:
            logging.warning: Logs warnings for each failed attempt.
            logging.error: Logs an error if all attempts fail.
        """
        self.update_capacity()
        required_tokens = 0  # Implement your own token calculation here

        if (
            self.available_request_capacity >= 1
            and self.available_token_capacity >= required_tokens
        ):
            self.available_request_capacity -= 1
            self.available_token_capacity -= required_tokens
            request_headers = {"Authorization": f"Bearer {self.api_key}"}
            attempts_left = self.max_attempts
            
            while attempts_left > 0:
                try:
                    async with session.post(
                        url=request_url, headers=request_headers, json=payload
                    ) as response:
                        response_json = await response.json()
                        
                        if "error" in response_json:
                            logging.warning(
                                f"API call failed with error: {response_json['error']}"
                            )
                            attempts_left -= 1
                            
                            if "Rate limit" in response_json["error"].get("message", ""):
                                self.last_update_time = time.time()
                                await asyncio.sleep(15)
                        else:
                            return response_json
                except Exception as e:
                    logging.warning(f"API call failed with exception: {e}")
                    attempts_left -= 1
            
            logging.error("API call failed after all attempts.")
        else:
            logging.warning(
                "Insufficient capacity for API call. Waiting for capacity to be available."
            )
            await asyncio.sleep(1)
            return await self.call_api(session, request_url, payload)

    def handle_error(self, error, request_json, metadata, save_filepath, status_tracker):
        """
        Handles API request errors by updating the `status_tracker` and saving the error data.
        
        This method updates the `status_tracker` to reflect that a task has failed. 
        It then saves the error information, request JSON, and optional metadata to a JSONL file.

        Args:
            error (Exception): The error that occurred.
            request_json (dict): The JSON of the failed request.
            metadata (dict, optional): Any additional metadata.
            save_filepath (str): The filepath where to save the error data.
            status_tracker (StatusTracker): The status tracker to update.
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
        Appends a Python data object to a JSONL (JSON Lines) file.
        
        This method takes a Python data object (which can be a dict, list, etc.), 
        converts it to a JSON-formatted string, and then appends this string as 
        a new line in the specified JSONL file.

        Args:
            data (Union[dict, list]): The data to append.
            filename (str): The name of the JSONL file to which the data will be appended.
        """
        json_string = json.dumps(data)
        with open(filename, "a") as f:
            f.write(json_string + "\n")


api_service = RateLimitedAPIService(
    api_key=os.getenv('OPENAI_API_KEY'),
    max_requests_per_minute=5000,
    max_tokens_per_minute=100000,
    token_encoding_name="utf-8",
    max_attempts=3,
)

status_tracker = StatusTracker()