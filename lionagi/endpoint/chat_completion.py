import aiohttp
import asyncio
from .base_endpoint import BaseEndpoint


class ChatCompletion(BaseEndpoint):
    
    endpoint = "chat/completions"
    
    def create_payload(self, messages=None, llmconfig=None,  **kwargs):
        config = {**llmconfig, **kwargs}
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

    async def process_response(self, payload, response, session, sleep=0):
        session._logger({"input": payload, "output": response})
        completion=response
        if "choices" in completion:
            session.conversation.add_messages(response=completion['choices'][0])
            session.conversation.responses.append(session.conversation.messages[-1])
            session.conversation.response_counts += 1
            await asyncio.sleep(sleep)
            session.status_tracker.num_tasks_succeeded += 1
        else:
            session.status_tracker.num_tasks_failed += 1
            
    def handle_error(self, error):
        print(f'An error occurred: {error}')
        # Include more sophisticated error handling as needed

# need work
    # async def call_api(self, session, **kwargs):
    #     payload = self.create_payload(**kwargs)
    #     try:
    #         async with session.post(self.endpoint, json=payload) as resp:
    #             if resp.status == 200:
    #                 response_data = await resp.json()
    #                 return self.process_response(response_data)
    #             else:
    #                 # Log the error or pass it to an error handler
    #                 self.handle_error(f'API returned {resp.status} status code')
    #     except Exception as e:
    #         self.handle_error(e)




    # async def call_api(self, sleep=0.1,**kwargs):
    #     """
    #     Make a call to the chat completion API and process the response.

    #     Parameters:
    #         sleep (float): The sleep duration after making the API call. Default is 0.1.

    #         **kwargs: Additional keyword arguments for configuration.
    #     """
        
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             payload = self.create_payload(**kwargs)
    #             completion = await api_service.call_api(, self.endpoint, payload)

    #     except Exception as e:
    #         session.status_tracker.num_tasks_failed += 1
    #         raise e