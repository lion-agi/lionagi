import asyncio
import logging
from .BaseService import BaseAPIService

class AsyncAPIService(BaseAPIService):
    """
    Asynchronous API Service for handling API requests concurrently.
    Inherits from BaseAPIService.
    """

    def __init__(self, api_key, max_requests_per_minute, 
                 max_tokens_per_minute, token_encoding_name, max_attempts):
        """
        Initialize the async API service with the given parameters.
        
        Parameters:
        api_key (str): The API key for authentication.
        max_requests_per_minute (int): Maximum number of API requests per minute.
        max_tokens_per_minute (int): Maximum number of tokens that can be used per minute.
        token_encoding_name (str): The encoding name for tokens.
        max_attempts (int): Maximum number of attempts for an API call.
        """        
        super().__init__(api_key, max_requests_per_minute, 
                         max_tokens_per_minute, token_encoding_name, max_attempts)
        self.request_queue = asyncio.Queue()

    async def enqueue_request(self, session, request_url, payload):
        """
        Enqueue a request for processing.
        
        Parameters:
        session (ClientSession): The session for making HTTP requests.
        request_url (str): The URL to which the request is made.
        payload (dict): The payload of the request.
        """
        await self.request_queue.put((session, request_url, payload))

    async def process_requests(self):
        """
        Process the requests in the queue.
        """
        while True:
            session, request_url, payload = await self.request_queue.get()
            await self.call_api(session, request_url, payload)
            self.request_queue.task_done()

    async def call_api(self, session, request_url, payload):
        """
        Make an API call with the given session, request URL, and payload.
        
        Parameters:
        session (ClientSession): The session for making HTTP requests.
        request_url (str): The URL to which the request is made.
        payload (dict): The payload of the request.
        """
        while True:
            if self.available_request_capacity < 1 or self.available_token_capacity < 10:  # Minimum token count
                await asyncio.sleep(1)  # Wait for capacity
                continue
            
            endpoint = self.api_endpoint_from_url(request_url)
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