import aiohttp
import asyncio

def create_payload_chatcompletion(self, **kwargs):
    """
    Create a payload for chat completion based on the conversation state and configuration.

    Parameters:
        **kwargs: Additional keyword arguments for configuration.

    Returns:
        dict: The payload for chat completion.
    """
    # currently only openai chat completions are supported
    messages = self.conversation.messages
    config = {**self.llmconfig, **kwargs}
    payload = {
        "messages": messages,
        "model": config.get('model'),
        "frequency_penalty": config.get('frequency_penalty'),
        "n": config.get('n'),
        "presence_penalty": config.get('presence_penalty'),
        "response_format": config.get('response_format'),
        "temperature": config.get('temperature'),
        "top_p": config.get('top_p'),
        }
    
    for key in ["seed", "stop", "stream", "tools", "tool_choice", "user", "max_tokens"]:
        if bool(config[key]) is True and str(config[key]) != "none":
            payload.update({key: config[key]})
    return payload

async def call_chatcompletion(session, sleep=0.1,**kwargs):
    """
    Make a call to the chat completion API and process the response.

    Parameters:
        sleep (float): The sleep duration after making the API call. Default is 0.1.

        **kwargs: Additional keyword arguments for configuration.
    """
    endpoint = f"chat/completions"
    try:
        async with aiohttp.ClientSession() as session:
            payload = create_payload_chatcompletion(**kwargs)
            completion = await session.api_service.call_api(
                            session, endpoint, payload)
            if "choices" in completion:
                session._logger({"input": payload, "output": completion})
                session.conversation.add_messages(response=completion['choices'][0])
                session.conversation.responses.append(session.conversation.messages[-1])
                session.conversation.response_counts += 1
                await asyncio.sleep(sleep)
                session.status_tracker.num_tasks_succeeded += 1
            else:
                session.status_tracker.num_tasks_failed += 1
    except Exception as e:
        session.status_tracker.num_tasks_failed += 1
        raise e