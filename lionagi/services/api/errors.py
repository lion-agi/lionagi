    def api_error(response_json: Mapping[str, Any]) -> bool:
        """
        Checks if the given response_json dictionary contains an "error" key.

        Args:
                response_json: The JSON assistant_response as a dictionary.

        Returns:
                True if there is an error, False otherwise.

        Examples:
                >>> response_json_with_error = {"error": "Something went wrong"}
                >>> APIUtil.api_error(response_json_with_error)
                True
                >>> response_json_without_error = {"result": "Success"}
                >>> APIUtil.api_error(response_json_without_error)
                False
        """
        if "error" in response_json:
            logging.warning(f"API call failed with error: {response_json['error']}")
            return True
        return False
    
    
    def api_rate_limit_error(response_json: Mapping[str, Any]) -> bool:
        """
        Checks if the error message in the response_json dictionary contains the phrase "Rate limit".

        Args:
                response_json: The JSON assistant_response as a dictionary.

        Returns:
                True if the phrase "Rate limit" is found, False otherwise.

        Examples:
                >>> response_json_with_rate_limit = {"error": {"message": "Rate limit exceeded"}}
                >>> api_rate_limit_error(response_json_with_rate_limit)
                True
                >>> response_json_without_rate_limit = {"error": {"message": "Another error"}}
                >>> api_rate_limit_error(response_json_without_rate_limit)
                False
        """
        return "Rate limit" in response_json.get("error", {}).get("message", "")