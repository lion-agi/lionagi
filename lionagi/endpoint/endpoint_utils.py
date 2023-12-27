import aiohttp


def create_payload(self, schema, **kwargs):
    """
    Create a payload for chat completion based on the conversation state and configuration.

    Parameters:
        kwargs: Additional keyword arguments for configuration.

    Returns:
        dict: The payload for chat completion.
    """
    # currently only openai chat completions are supported
    messages = self.conversation.messages
    config = {**self.llmconfig, **kwargs}
    
    payload = {"messages": messages}
    for key in schema['required']:
        payload.update({key: config[key]})

    for key in schema['optional']:
        if bool(config[key]) is True and str(config[key]).lower() != "none":
            payload.update({key: config[key]})
    return payload

async def call_api(payload, service, endpoint="chat/completions"):
    """
    Make a call to the chat completion API and process the response.

    Parameters:
        sleep (float): The sleep duration after making the API call. Default is 0.1.
        kwargs: Additional keyword arguments for configuration.
    """

    async with aiohttp.ClientSession() as session:
        completion = await service.call_api(session, endpoint, payload)
        return completion
    