    def get_cache_key(url: str, params: Mapping[str, Any] | None) -> str:
        """
        Creates a unique cache key based on the URL and parameters.
        """
        import hashlib

        param_str = to_str(params, sort_keys=True) if params else ""
        return hashlib.md5((url + param_str).encode("utf-8")).hexdigest()
        
    @AsyncUtil.cached(ttl=10 * 60)  # Cache the result for 10 minutes
    async def get_oauth_token_with_cache(
        http_session: aiohttp.ClientSession,
        auth_url: str,
        client_id: str,
        client_secret: str,
        scope: str,
    ) -> str:
        """
        Retrieves an OAuth token from the authentication server and caches it to avoid unnecessary requests.

        Args:
                http_session: The HTTP session object to use for making the request.
                auth_url: The URL of the authentication server.
                client_id: The client ID for OAuth authentication.
                client_secret: The client secret for OAuth authentication.
                scope: The scope for which the OAuth token is requested.

        Returns:
                The OAuth token as a string.

        Examples:
                >>> session = aiohttp.ClientSession()
                >>> token = await APIUtil.get_oauth_token_with_cache(session, 'http://auth.example.com', 'client_id', 'client_secret', 'read')
                >>> token
                'mock_access_token'
        """
        async with http_session.post(
            auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": scope,
            },
        ) as auth_response:
            auth_response.raise_for_status()
            return (await auth_response.json()).get("access_token")