    @staticmethod
    @AsyncUtil.cached(ttl=10 * 60)
    async def cached_api_call(
        http_session: aiohttp.ClientSession, url: str, **kwargs
    ) -> Any:
        """
        Makes an API call.

        Args:
                http_session: The aiohttp client session.
                url: The URL for the API call.
                **kwargs: Additional arguments for the API call.

        Returns:
                The assistant_response from the API call, if successful; otherwise, None.
        """
        try:
            async with http_session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"API call to {url} failed: {e}")
            return None
        
        
    async def retry_api_call(
        http_session: aiohttp.ClientSession,
        url: str,
        retries: int = 3,
        backoff_factor: float = 0.5,
        **kwargs,
    ) -> Any:
        """
        Retries an API call on failure, with exponential backoff.

        Args:
                http_session: The aiohttp client session.
                url: The URL to make the API call.
                retries: The number of times to retry.
                backoff_factor: The backoff factor for retries.
                **kwargs: Additional arguments for the API call.

        Returns:
                The assistant_response from the API call, if successful; otherwise, None.
        """
        for attempt in range(retries):
            try:
                async with http_session.get(url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError:
                if attempt < retries - 1:
                    delay = backoff_factor * (2**attempt)
                    logging.info(f"Retrying {url} in {delay} seconds...")
                    await AsyncUtil.sleep(delay)
                else:
                    logging.error(
                        f"Failed to retrieve data from {url} after {retries} attempts."
                    )
                    return None


    async def unified_api_call(
        http_session: aiohttp.ClientSession, method: str, url: str, **kwargs
    ) -> Any:
        """
        Makes an API call and automatically retries on rate limit error.

        Args:
                http_session: The session object from the aiohttp library.
                method: The HTTP method as a string.
                url: The URL to which the request is made.
                **kwargs: Additional keyword arguments to pass to the API call.

        Returns:
                The JSON assistant_response as a dictionary.

        Examples:
                >>> session = aiohttp.ClientSession()
                >>> success_url = "https://api.example.com/v1/success"
                >>> print(await unified_api_call(session, 'get', success_url))
                {'result': 'Success'}
                >>> rate_limit_url = "https://api.example.com/v1/rate_limit"
                >>> print(await unified_api_call(session, 'get', rate_limit_url))
                {'error': {'message': 'Rate limit exceeded'}}
        """
        api_call = APIUtil.api_method(http_session, method)
        retry_count = 3
        retry_delay = 5  # seconds

        for attempt in range(retry_count):
            async with api_call(url, **kwargs) as response:
                response_json = await response.json()

                if not APIUtil.api_error(response_json):
                    return response_json

                if (
                    APIUtil.api_rate_limit_error(response_json)
                    and attempt < retry_count - 1
                ):
                    logging.warning(
                        f"Rate limit error detected. Retrying in {retry_delay} seconds..."
                    )
                    await AsyncUtil.sleep(retry_delay)
                else:
                    break

        return response_json