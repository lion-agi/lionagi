# import requests
import aiohttp
import hashlib
import json
import logging
import re
import tiktoken

from typing import Any, Callable, Dict, Optional

from lionagi.util import strip_lower, CallDecorator


class APIUtil:
    """
    Provides a suite of static utility functions for making asynchronous API calls,
    handling responses, and managing common API interaction patterns using aiohttp.

    This class encapsulates methods for dynamically selecting HTTP methods, identifying
    and logging API errors, handling API rate limits by retrying calls, extracting endpoints
    from URLs, and caching responses to minimize redundant network traffic. It also offers
    functionality for uploading files with automatic retries on failure and calculating
    the number of tokens required for a request, which can be useful for rate-limited APIs.

    The utility functions make extensive use of modern Python asynchronous features,
    enabling efficient and scalable API interactions in concurrent applications. It's
    designed to be used with aiohttp's ClientSession objects, providing a high-level
    interface for various API request and response operations.

    Features:
    - Dynamic HTTP method selection based on string input.
    - Error checking for common API response issues, including rate limit errors.
    - Caching of responses and endpoints to improve efficiency and performance.
    - Utility for file uploads with retry logic on failure.
    - Token calculation for API requests, aiding in managing rate limits.

    Example Usage:
    ```python
    async with aiohttp.ClientSession() as session:
        response = await APIUtil.api_call(session, 'post', 'https://api.example.com/data', json={'key': 'value'})
        if not APIUtil.api_error(response):
            print('API call succeeded:', response)
    ```

    Note:
    This class is intended as a utility and should be extended or modified to fit
    specific API interaction requirements, including handling authentication, parsing
    complex responses, and integrating with specific API rate limiting schemes.
    """

    @staticmethod
    def api_method(http_session: aiohttp.ClientSession, method: str = "post") -> Callable:
        """
        Retrieves a method from an aiohttp.ClientSession instance corresponding to the specified HTTP verb.

        This method dynamically selects and returns the callable associated with the HTTP method
        (e.g., 'get', 'post', 'delete') to be used for making an API call.

        Args:
            http_session (aiohttp.ClientSession): The session object used for making HTTP requests.
            method (str): The HTTP method as a string. Supported methods are 'post', 'delete',
                          'head', 'options', and 'patch'. Default is 'post'.

        Returns:
            Callable: The aiohttp.ClientSession method corresponding to the specified HTTP verb.

        Raises:
            ValueError: If the specified method is not supported or recognized.

        Examples:
            >>> async with aiohttp.ClientSession() as session:
            >>>     post_method = APIUtil.api_method(session, "post")
            >>>     # Now you can use post_method(url, **kwargs) to make a post request.
        """
        if method not in ["post", "delete", "head", "options", "patch"]:
            raise ValueError(
                "Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']")
        return getattr(http_session, method)

    @staticmethod
    def api_error(response_json: Dict[str, Any]) -> bool:
        """
        Evaluates if the provided JSON response from an API call contains an error indication.

        This method checks for the presence of an 'error' key in the dictionary, implying
        that the API call resulted in an error. If an error is found, it logs a warning with the error message.

        Args:
            response_json (Dict[str, Any]): The JSON response from an API call as a dictionary.

        Returns:
            bool: True if the response contains an 'error' key, indicating a failed API call;
                  False otherwise.

        Examples:
            >>> response_json_with_error = {"error": "Something went wrong"}
            >>> assert APIUtil.api_error(response_json_with_error) == True
            >>> response_json_without_error = {"result": "Success"}
            >>> assert APIUtil.api_error(response_json_without_error) == False
        """
        if "error" in response_json:
            logging.warning(f"API call failed with error: {response_json['error']}")
            return True
        return False

    @staticmethod
    def api_rate_limit_error(response_json: Dict[str, Any]) -> bool:
        """
        Determines whether the API response indicates a rate limit error.

        This function specifically looks for the phrase "Rate limit" in the error message within
        the response JSON. It's useful for identifying when an API call has failed due to exceeding
        the rate limit imposed by the API provider.

        Args:
            response_json (Dict[str, Any]): The JSON response from an API call as a dictionary.

        Returns:
            bool: True if the error message contains "Rate limit", indicating that the API call
                  was rate-limited; False otherwise.

        Examples:
            >>> response_json_with_rate_limit = {"error": {"message": "Rate limit exceeded"}}
            >>> assert APIUtil.api_rate_limit_error(response_json_with_rate_limit) == True
            >>> response_json_without_rate_limit = {"error": {"message": "Another error"}}
            >>> assert APIUtil.api_rate_limit_error(response_json_without_rate_limit) == False
        """
        return "Rate limit" in response_json.get("error", {}).get("message", "")

    @staticmethod
    @CallDecorator.cache(ttl=10 * 60)
    def api_endpoint_from_url(request_url: str) -> str:
        """
        Extracts and returns the API endpoint path from a full URL.

        Utilizes a regular expression to parse the URL and extract the portion that represents
        the API endpoint. This method is useful for identifying the specific API service being
        called based on its URL, especially when caching responses or logging API usage.

        Args:
            request_url (str): The complete URL of the API request.

        Returns:
            str: The API endpoint extracted from the URL. Returns an empty string if the URL
                 does not match the expected pattern.

        Examples:
            >>> valid_url = "https://api.example.com/v1/users"
            >>> APIUtil.api_endpoint_from_url(valid_url)
            'users'
            >>> invalid_url = "https://api.example.com/users"
            >>> APIUtil.api_endpoint_from_url(invalid_url)
            ''

        Note:
            The function is designed to recognize URLs following a common REST API structure,
            where the version number ('v1', 'v2', etc.) precedes the endpoint name.
        """
        match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
        return match.group(2) if match else ""

    @staticmethod
    @CallDecorator.retry(retries=3, delay=0.1, backoff_factor=2)
    async def api_call(http_session: aiohttp.ClientSession, method: str, url: str,
                       **kwargs) -> Any:
        """
        Asynchronously executes an API call with automatic retry on failure.

        This method abstracts the complexity of making HTTP requests and handling common issues
        like rate limiting. It automatically retries the request based on the specified retry
        policy if a rate limit error is detected.

        Args:
            http_session (aiohttp.ClientSession): The session object to use for making HTTP requests.
            method (str): The HTTP method (e.g., 'get', 'post') to use for the request.
            url (str): The URL to which the API request is directed.
            **kwargs: Additional keyword arguments passed directly to the aiohttp request method.

        Returns:
            Any: The JSON response from the API call, parsed into a dictionary or list, depending on
                 the API response format.

        Raises:
            ValueError: If a rate limit error is detected and retries are exhausted.

        Examples:
            >>> async with aiohttp.ClientSession() as session:
            >>>     success_url = "https://api.example.com/v1/success"
            >>>     response = await APIUtil.api_call(session, 'get', success_url)
            >>>     print(response)  # Expected: {'result': 'Success'}
            >>>     rate_limit_url = "https://api.example.com/v1/rate_limit"
            >>>     response = await APIUtil.api_call(session, 'get', rate_limit_url)
            >>>     # Raises ValueError due to rate limit error if retries are exhausted

        Note:
            The retry mechanism is applied using the CallDecorator.retry, with configurable
            retries, delay, and backoff_factor. It's recommended to handle the ValueError in
            calling code to manage the flow in case of persistent rate limit errors.
        """
        api_call = APIUtil.api_method(http_session, method)

        async with api_call(url, **kwargs) as response:
            response_json = await response.json()

            if not APIUtil.api_error(response_json):
                return response_json

            if APIUtil.api_rate_limit_error(response_json):
                logging.warning(f"Rate limit error detected. Retrying...")
                raise ValueError("Rate limit error detected")

            return response_json

    @staticmethod
    @CallDecorator.cache(ttl=10 * 60)
    def get_cache_key(url: str, params: Optional[Dict[str, Any]]) -> str:
        """
        Generates a unique cache key for an API request based on the URL and query parameters.

        This method serializes the request URL and parameters into a string and then applies
        an MD5 hash to generate a unique key. It's particularly useful for caching responses
        to avoid redundant network calls for identical requests.

        Args:
            url (str): The request URL.
            params (Optional[Dict[str, Any]]): A dictionary of query parameters included with the request.

        Returns:
            str: A unique string key derived from the URL and parameters, suitable for use in caching mechanisms.

        Examples:
            >>> url = "https://api.example.com/data"
            >>> params = {"query": "info", "limit": 5}
            >>> cache_key = APIUtil.get_cache_key(url, params)
            >>> print(cache_key)  # Output will be an MD5 hash of the concatenated URL and parameters.
        """
        param_str = json.dumps(params, sort_keys=True) if params else ""
        return hashlib.md5((url + param_str).encode('utf-8')).hexdigest()

    @staticmethod
    async def upload_file(http_session: aiohttp.ClientSession, url: str, file_path: str,
                          param_name: str = 'file',
                          additional_data: Dict[str, Any] = None) -> Any:
        """
        Asynchronously uploads a file to a specified URL, supporting additional data alongside the file.

        This method handles file uploads using multipart/form-data encoding, which is commonly used for
        uploading files via HTTP. It's designed to work asynchronously with aiohttp's ClientSession.

        Args:
            http_session (aiohttp.ClientSession): The session object to use for making the HTTP request.
            url (str): The URL to which the file will be uploaded.
            file_path (str): The filesystem path to the file that will be uploaded.
            param_name (str): The name of the form field expected by the server for the file upload. Defaults to 'file'.
            additional_data (Optional[Dict[str, Any]]): Any additional data to be sent with the file upload as form fields.

        Returns:
            Any: The JSON-decoded response from the server.

        Raises:
            aiohttp.ClientError: If an HTTP error occurs during the file upload process.

        Examples:
            >>> async with aiohttp.ClientSession() as session:
            >>>     response = await APIUtil.upload_file(session, "https://example.com/upload", "/path/to/file.jpg")
            >>>     print(response)  # Server response to the file upload.
        """
        try:
            with open(file_path, 'rb') as file:
                files = {param_name: file}
                if additional_data is None:
                    additional_data = {}
                data = {**files, **additional_data}
                async with http_session.post(url, data=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"Failed to upload file to {url}: {e}")
            raise

    @staticmethod
    def create_payload(input_, config, required_, optional_, input_key, **kwargs):
        config = {**config, **kwargs}
        payload = {input_key: input_}

        for key in required_:
            payload.update({key: config[key]})

        for key in optional_:
            if bool(config[key]) is True and strip_lower(config[key]) != "none":
                payload.update({key: config[key]})

        return payload





    # @staticmethod
    # def get_url_response(url: str, timeout: tuple = (1, 1), **kwargs) -> requests.Response:
    #     """
    #     Sends a GET request to a URL and returns the response.

    #     Args:
    #         url (str): The URL to send the GET request to.
    #         timeout (tuple): A tuple specifying the connection and read timeouts in seconds.
    #                         Defaults to (1, 1).
    #         **kwargs: Additional keyword arguments to be passed to the requests.get() function.

    #     Returns:
    #         requests.Response: A Response object containing the server's response to the GET request.

    #     Raises:
    #         TimeoutError: If a timeout occurs while requesting or reading the response.
    #         Exception: If an error other than a timeout occurs during the request.
    #     """
    #     try:
    #         response = requests.get(url, timeout=timeout, **kwargs)
    #         response.raise_for_status()
    #         return response
    #     except requests.exceptions.ConnectTimeout:
    #         raise TimeoutError(f"Timeout: requesting >{timeout[0]} seconds.")
    #     except requests.exceptions.ReadTimeout:
    #         raise TimeoutError(f"Timeout: reading >{timeout[1]} seconds.")
    #     except Exception as e:
    #         raise e

    # @staticmethod    
    # def get_url_content(url: str) -> str:
    #     """
    #     Retrieve and parse the content from a given URL.

    #     Args:
    #         url (str): The URL to fetch and parse.

    #     Returns:
    #         str: The text content extracted from the URL.

    #     Raises:
    #         ValueError: If there is an issue during content retrieval or parsing.
    #     """
    #     try:
    #         response = requests.get(url)
    #         response.raise_for_status()

    #         soup = BeautifulSoup(response.text, 'html.parser')

    #         text_content = ' '.join([p.get_text() for p in soup.find_all('p')])
    #         return text_content
    #     except Exception as e:
    #         raise f"Error fetching content for {url}: {e}"
