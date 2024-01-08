from lionagi.objs.abc_objs import BaseEndpoint


class ChatCompletion(BaseEndpoint):
    """
    Represents an endpoint for chat completions in an API.

    This class is designed to handle the creation of payloads for chat completion requests. The 'endpoint' attribute specifies the API endpoint for chat completions.

    Attributes:
        endpoint (str): The API endpoint for chat completions.
    """
    endpoint: str = "chat/completions"

    @classmethod
    def create_payload(scls, messages, llmconfig, schema, **kwargs):
        """
        Creates a payload for a chat completion request using provided messages, configuration, and schema.

        This method constructs a payload dictionary that includes required and optional parameters 
        as specified in the schema. Required parameters are extracted from 'llmconfig' and 'kwargs', 
        while optional parameters are included only if they are truthy and not equal to the string "none".

        Parameters:
            messages (list): A list of message objects to include in the payload.
            llmconfig (dict): A dictionary containing configuration settings for the large language model.
            schema (dict): A dictionary defining required and optional keys for the payload.
                The 'required' key should map to a list of required parameter names.
                The 'optional' key should map to a list of optional parameter names.
            **kwargs: Additional keyword arguments that can override or supplement 'llmconfig'.

        Returns:
            dict: A dictionary representing the payload for the chat completion request.

        Example:
            payload = ChatCompletion.create_payload(
                messages=[{"text": "Hello, world!"}],
                llmconfig={"max_tokens": 100},
                schema={"required": ["max_tokens"], "optional": ["temperature"]}
            )
        """
        config = {**llmconfig, **kwargs}
        payload = {"messages": messages}
        for key in schema['required']:
            payload.update({key: config[key]})

        for key in schema['optional']:
            if bool(config[key]) is True and str(config[key]).lower() != "none":
                payload.update({key: config[key]})
        return payload
    
    # def process_response(self, session, payload, completion):
    #     ...
        