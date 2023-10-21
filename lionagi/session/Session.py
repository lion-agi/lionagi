from .Conversation import Conversation
from lionagi.utils.sys_utils import create_copies
from lionagi.utils.log_utils import llm_logger
from lionagi.utils.api_utils import api_service, status_tracker
import aiohttp
import asyncio

llmlog = llm_logger()

class SessionConfig:
    def __init__(self):
        self.config = {
            "model": "gpt-3.5-turbo-16k",
            "frequency_penalty": 0,
            "n": 1,
            "stream": False,
            "temperature": 1,
            "top_p": 1,
            "sleep": 0.1,
            "out": True,
            "function_call": None,
            "functions": None,
            "stop": None
        }

class Session(SessionConfig):
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

    def __init__(self, system, api_service=api_service, status_tracker=status_tracker):
        """
        Initializes a new Session object.

        Args:
            system (str): The initial system message for the conversation.
            api_service (RateLimitedAPIService, optional): The API service instance for rate-limit handling.
            status_tracker (StatusTracker, optional): The status tracker instance for task monitoring.
        """
        super().__init__()
        self.conversation = Conversation(system=system)
        self.api_service = api_service  # RateLimitedAPIService instance
        self.status_tracker = status_tracker  # StatusTracker instance

    async def initiate(self, 
            instruction, system=None, context=None, **kwargs):
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

        config = {**self.config, **kwargs}
        system = system if system else self.conversation.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context)
        
        await self.call_OpenAI_ChatCompletion(**config)
        if config['out']:
            return self.conversation.responses[-1]['content']        

    async def followup(self, 
            instruction, system=None, context=None, **kwargs):
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
        
        config = {**self.config, **kwargs}
        await self.call_OpenAI_ChatCompletion(**config)
        if config['out']:
            return self.conversation.responses[-1]['content']
        
    async def call_OpenAI_ChatCompletion(self, **kwargs):
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
        config = {**self.config, **kwargs}
        
        payload = {
            "messages": messages,
            "model": config['model'],
            "frequency_penalty": config['frequency_penalty'],
            "temperature": config['temperature'],
            "top_p": config['top_p'],
            "n": config['n']}
        
        for key in ["stream", "stop", "function_call","functions"]:
            if config[key] is True:
                payload.update({key: config[key]})

        # Use the RateLimitedAPIService for API call
        try:
            async with aiohttp.ClientSession() as session:
                completion = await self.api_service.call_api(session, request_url, payload)
                if "choices" in completion:
                    completion = completion['choices'][0]
                    llmlog(self.conversation.messages, completion)
                    response = {"role": "assistant", "content": completion['message']["content"]}
                    self.conversation.responses.append(response)
                    self.conversation.response_counts += 1
                    await asyncio.sleep(config['sleep'])
                    self.status_tracker.num_tasks_succeeded += 1
                else:
                    self.status_tracker.num_tasks_failed += 1
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e
        
        
class MultiSession(SessionConfig):

    def __init__(self, system, api_service=api_service, status_tracker=status_tracker, num=3):
        """
        Initializes a new Session object.

        Args:
            system (str): The initial system message for the conversation.
            api_service (RateLimitedAPIService, optional): The API service instance for rate-limit handling.
            status_tracker (StatusTracker, optional): The status tracker instance for task monitoring.
        """
        super().__init__()
        self.num_conversation = num
        self.sessions = create_copies(
            Session(system=system, api_service=api_service, status_tracker=status_tracker), 
            n=num)

    async def initiate(self, instruction, system=None, context=None, **kwargs):
        config = {**self.config, **kwargs}
        system = system if system else self.sessions[0].conversation.system

        async def initiate_single_session(session):
            return await session.initiate(
                instruction=instruction, 
                system=system, 
                context=context, **config
            )
        
        results = await asyncio.gather(
            *[initiate_single_session(session) for session in self.sessions]
        )
        
        if config['out']:
            return results

    async def followup(self, instruction, system=None, context=None, **kwargs):
        config = {**self.config, **kwargs}

        async def followup_single_session(session):
            if system:
                session.conversation.change_system(system)
            return await session.followup(     
                system=system,       
                instruction=instruction, 
                context=context, **config)
        
        results = await asyncio.gather(
            *[followup_single_session(session) for session in self.sessions]
        )
        
        if config['out']:
            return results