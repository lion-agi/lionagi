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
    def create_payload(scls, messages, imodel, config, schema, **kwargs):
        config = config or imodel.config
        config = {**config, **kwargs}

        payload = {"messages": messages}
        for key in schema['required']:
            payload.update({key: config[key]})

        for key in schema['optional']:
            if bool(config[key]) is True and str(config[key]).lower() != "none":
                payload.update({key: config[key]})
        return payload
    
    # def process_response(self, session, payload, completion):
    #     ...
        