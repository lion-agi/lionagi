
import logging
import time
from queue import Queue
import requests
from .BaseService import BaseAPIService

class SyncAPIService(BaseAPIService):
    
    def __init__(self, api_key, max_requests_per_minute, max_tokens_per_minute, token_encoding_name, max_attempts):
        super().__init__(api_key, max_requests_per_minute, max_tokens_per_minute, token_encoding_name, max_attempts)
        self.request_queue = Queue()
        
    def enqueue_request(self, session, request_url, payload):
        self.request_queue.put((session, request_url, payload))

    def call_api(self, session, request_url, payload):
        while True:
            if self.available_request_capacity < 1 or self.available_token_capacity < 10:  # Minimum token count
                time.sleep(1)
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
                        with requests.post(
                            url=request_url, headers=request_headers, json=payload
                        ) as response:
                            response_json = response.json()

                        if "error" in response_json:
                            logging.warning(
                                f"API call failed with error: {response_json['error']}"
                            )
                            attempts_left -= 1

                            if "Rate limit" in response_json["error"].get("message", ""):
                                time.sleep(15)
                        else:
                            return response_json
                    except Exception as e:
                        logging.warning(f"API call failed with exception: {e}")
                        attempts_left -= 1

                logging.error("API call failed after all attempts.")
                break
            else:
                time.sleep(1)
