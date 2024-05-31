    def api_method(
        http_session: aiohttp.ClientSession, method: str = "post"
    ) -> Callable:
        """
        Returns the corresponding HTTP method function from the http_session object.

        Args:
                http_session: The session object from the aiohttp library.
                method: The HTTP method as a string.

        Returns:
                The Callable for the specified HTTP method.

        Raises:
                ValueError: If the method is not one of the allowed ones.

        Examples:
                >>> session = aiohttp.ClientSession()
                >>> post_method = APIUtil.api_method(session, "post")
                >>> print(post_method)
                <bound method ClientSession._request of <aiohttp.client.ClientSession object at 0x...>>
        """
        if method in {"post", "delete", "head", "options", "patch"}:
            return getattr(http_session, method)
        else:
            raise ValueError(
                "Invalid request, method must be in ['post', 'delete', 'head', 'options', 'patch']"
            )






    @func_call.lru_cache(maxsize=128)
    def api_endpoint_from_url(request_url: str) -> str:
        """
        Extracts the API endpoint from a given URL using a regular expression.

        Args:
                request_url: The full URL to the API endpoint.

        Returns:
                The extracted endpoint or an empty string if the pattern does not match.

        Examples:
                >>> valid_url = "https://api.example.com/v1/users"
                >>> api_endpoint_from_url(valid_url)
                'users'
                >>> invalid_url = "https://api.example.com/users"
                >>> api_endpoint_from_url(invalid_url)
                ''
        """
        match = re.search(r"^https://[^/]+(/.+)?/v\d+/(.+)$", request_url)
        return match[2] if match else ""