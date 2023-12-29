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

    @abc.abstractmethod
    def process_response(self, response):
        """
        Process the response from the API call.
        
        Parameters:
            response: The response to process.
        """
        pass




    
