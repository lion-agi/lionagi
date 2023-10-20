from .Conversation import Conversation
from lionagi.utils.api_utils import api_service, status_tracker
import aiohttp
import asyncio

class Session:
    """
    Manages a chat conversation with OpenAI's API.

    This class acts as a high-level interface for managing a conversation, 
    which includes initiating the conversation, making follow-up requests, 
    and handling API rate limits.

    Attributes:
        conversation (Conversation): An instance of the Conversation class to manage the chat.
        api_service (RateLimitedAPIService): An instance to handle rate-limited API calls.
        status_tracker (StatusTracker): An instance to track the status of API tasks.
    """
    
    def __init__(self, system, api_service=api_service, status_tracker=status_tracker) -> None:
        """
        Initializes a new Session object.

        Args:
            system (str): The initial system message for the conversation.
            api_service (RateLimitedAPIService, optional): The API service instance for rate-limit handling.
            status_tracker (StatusTracker, optional): The status tracker instance for task monitoring.
        """
        self.conversation = Conversation(system=system)
        self.api_service = api_service  # RateLimitedAPIService instance
        self.status_tracker = status_tracker  # StatusTracker instance

    async def initiate(self, 
            instruction, 
            system=None, 
            context=None, 
            model="gpt-3.5-turbo-16k", 
            frequency_penalty=0, 
            n=1,
            stream=False,
            temperature=1,
            top_p=1, 
            sleep=0.1, out=True):
        """
        Initiates a new conversation by sending the first user instruction.

        Args:
            instruction (str): The instruction from the user.
            system (str, optional): System message for the conversation.
            context (dict, optional): Additional context for the conversation.
            model (str, optional): The model to be used for chat completion. Defaults to "gpt-3.5-turbo-16k".
            frequency_penalty (float, optional): Controls the frequency penalty. Defaults to 0.
            n (int, optional): Number of chat completions to generate. Defaults to 1.
            stream (bool, optional): Whether to stream the completions. Defaults to False.
            temperature (float, optional): Controls randomness. Defaults to 1.
            top_p (float, optional): Controls diversity via nucleus sampling. Defaults to 1.
            sleep (float, optional): Time to sleep after an API call. Defaults to 0.1 seconds.
            out (bool, optional): Whether to return the last response content. Defaults to True.

        Returns:
            str: The content of the last response if `out` is True.
        """
        system = system if system else self.conversation.system
        self.conversation.initiate_conversation(system, instruction, context)
        await self.call_OpenAI_ChatCompletion(
            model=model, 
            frequency_penalty=frequency_penalty, 
            n=n,
            stream=stream,
            temperature=temperature,
            top_p=top_p, 
            sleep=sleep)
        if out:
            return self.conversation.responses[-1]['content']

    async def followup(self,
            instruction,
            system=None, 
            context=None, 
            model="gpt-3.5-turbo-16k", 
            frequency_penalty=0, 
            n=1,
            stream=False,
            temperature=1,
            top_p=1, 
            sleep=0.1, 
            out=True):
        """
        Sends a follow-up user instruction in the ongoing conversation.

        Args:
            instruction (str): The follow-up instruction from the user.
            system (str, optional): System message for the conversation.
            context (dict, optional): Additional context for the conversation.
            model (str, optional): The model to be used for chat completion. Defaults to "gpt-3.5-turbo-16k".
            frequency_penalty (float, optional): Controls the frequency penalty. Defaults to 0.
            n (int, optional): Number of chat completions to generate. Defaults to 1.
            stream (bool, optional): Whether to stream the completions. Defaults to False.
            temperature (float, optional): Controls randomness. Defaults to 1.
            top_p (float, optional): Controls diversity via nucleus sampling. Defaults to 1.
            sleep (float, optional): Time to sleep after an API call. Defaults to 0.1 seconds.
            out (bool, optional): Whether to return the last response content. Defaults to True.

        Returns:
            str: The content of the last response if `out` is True.
        """
        self.conversation.append_last_response()
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context)
        await self.call_OpenAI_ChatCompletion(
            model=model, 
            frequency_penalty=frequency_penalty, 
            n=n,
            stream=stream,
            temperature=temperature,
            top_p=top_p, 
            sleep=sleep)
        if out:
            return self.conversation.responses[-1]['content']

    async def call_OpenAI_ChatCompletion(self, model, frequency_penalty=0, n=1, stream=False, temperature=1, top_p=1, sleep=0.1):
        """
        Makes the API call to OpenAI for chat completion.

        This method prepares the payload and then uses the RateLimitedAPIService for the API call. 
        It also updates the status tracker depending on the success or failure of the task.

        Args:
            model (str): The model to be used for chat completion.
            frequency_penalty (float): Controls the frequency penalty.
            n (int): Number of chat completions to generate.
            stream (bool): Whether to stream the completions.
            temperature (float): Controls randomness.
            top_p (float): Controls diversity via nucleus sampling.
            sleep (float): Time to sleep after an API call.

        Raises:
            Exception: Any exceptions that occur during the API call.
        """
        messages = self.conversation.messages
        request_url = f"https://api.openai.com/v1/chat/completions"
        
        # Prepare the payload with all the parameters
        payload = {
            "messages": messages,
            "model": model,
            "frequency_penalty": frequency_penalty,
            "n": n,
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p
        }

        # Use the RateLimitedAPIService for API call
        try:
            async with aiohttp.ClientSession() as session:
                completion = await self.api_service.call_api(session, request_url, payload)
                if "choices" in completion:
                    completion = completion['choices'][0]
                    response = {"role": "assistant", "content": completion['message']["content"]}
                    self.conversation.responses.append(response)
                    # llmlog(self.conversation.messages, completion)
                    self.conversation.response_counts += 1
                    await asyncio.sleep(sleep)
                    self.status_tracker.num_tasks_succeeded += 1
                else:
                    self.status_tracker.num_tasks_failed += 1
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e