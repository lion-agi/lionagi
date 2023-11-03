import asyncio
import json
import logging
import time
import dotenv
import os
from dataclasses import dataclass
import tiktoken
import re

dotenv.load_dotenv('.env')
logging.basicConfig(level=logging.INFO)

def api_endpoint_from_url(request_url):
    """Extract the API endpoint from the request URL."""
    match = re.search("^https://[^/]+/v\\d+/(.+)$", request_url)
    return match[1]

@dataclass
class StatusTracker:
    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_rate_limit_errors: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    time_of_last_rate_limit_error: int = 0

class RateLimitedAPIService:
    def __init__(self, api_key, max_requests_per_minute, max_tokens_per_minute, token_encoding_name, max_attempts):
        self.api_key = api_key
        self.max_requests_per_minute = max_requests_per_minute
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_encoding_name = token_encoding_name
        self.max_attempts = max_attempts
        self.available_request_capacity = max_requests_per_minute
        self.available_token_capacity = max_tokens_per_minute
        self.last_update_time = time.time()
        self.request_queue = asyncio.Queue()
        self.rate_limit_task = asyncio.create_task(self.rate_limit_replenisher())

    async def rate_limit_replenisher(self):
        while True:
            await asyncio.sleep(60)  # Replenish every minute
            self.available_request_capacity = self.max_requests_per_minute
            self.available_token_capacity = self.max_tokens_per_minute

    async def enqueue_request(self, session, request_url, payload):
        await self.request_queue.put((session, request_url, payload))

    async def process_requests(self):
        while True:
            session, request_url, payload = await self.request_queue.get()
            await self.call_api(session, request_url, payload)
            self.request_queue.task_done()

    async def call_api(self, session, request_url, payload):
        while True:
            if self.available_request_capacity < 1 or self.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            endpoint = api_endpoint_from_url(request_url)
            required_tokens = self.num_tokens_consumed_from_request(payload, endpoint)
            if self.available_token_capacity >= required_tokens:
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
                                    await asyncio.sleep(15)
                            else:
                                return response_json
                    except Exception as e:
                        logging.warning(f"API call failed with exception: {e}")
                        attempts_left -= 1

                logging.error("API call failed after all attempts.")
                break
            else:
                await asyncio.sleep(1)  # Wait for token capacity


    def handle_error(self, error, request_json, metadata, save_filepath, status_tracker):
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
            
            
import aiohttp

async def main():
    # Initialize the RateLimitedAPIService with strict rate limits for demonstration
    api_service = RateLimitedAPIService(
        api_key=os.getenv("OPENAI_API_KEY"),
        max_requests_per_minute=5,  # 2 requests per minute for demonstration
        max_tokens_per_minute=100,  # 100 tokens per minute for demonstration
        token_encoding_name="cl100k_base",
        max_attempts=3
    )

    # Mock payload for API call
    payload = {
        "model":"gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "tell me a joke"}
        ]
    }

    async with aiohttp.ClientSession() as session:
        # Create multiple tasks to make API calls
        tasks = [api_service.call_api(session, "https://api.openai.com/v1/chat/completions", payload) for _ in range(5)]
        
        # Execute all tasks and gather responses
        responses = await asyncio.gather(*tasks)

    # Print responses
    for i, response in enumerate(responses):
        print(f"Response {i + 1}: {response}\n")
