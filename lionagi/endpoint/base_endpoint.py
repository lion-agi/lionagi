import abc

class BaseEndpoint(abc.ABC):
    endpoint: str = abc.abstractproperty()

    @abc.abstractmethod
    def create_payload(self, **kwargs):
        """
        Create a payload for the request based on configuration.
        
        Parameters:
            **kwargs: Additional keyword arguments for configuration.

        Returns:
            dict: The payload for the request.
        """
        pass

    # @abc.abstractmethod
    # async def call_api(self, session, **kwargs):
    #     """
    #     Make a call to the API endpoint and process the response.
        
    #     Parameters:
    #         session: The aiohttp client session.
    #         **kwargs: Additional keyword arguments for configuration.
    #     """
    #     pass

    @abc.abstractmethod
    def process_response(self, response):
        """
        Process the response from the API call.
        
        Parameters:
            response: The response to process.
        """
        pass




    # @abc.abstractmethod
    # def handle_error(self, error):
    #     """
    #     Handle any errors that occur during the API call.
        
    #     Parameters:
    #         error: The error to handle.
    #     """
    #     pass
