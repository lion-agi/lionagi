import aiohttp
import asyncio
from typing import Any

from .conversation import Conversation
from ..config.llmconfig import llmconfig
from ..utils.log_util import DataLogger
from ..utils.api_util import StatusTracker
from ..config.oaiconfig import OAIService

status_tracker = StatusTracker()

class Session():
    """
    A class representing a conversation session with chat completion capabilities.

    This class manages conversations, interacts with chat completion services (currently OpenAI),
    and logs the interactions using a DataLogger.

    Attributes:
        conversation: An instance of the Conversation class for managing messages.
        system: The system identifier for the conversation session.
        llmconfig: Configuration parameters for language models.
        logger: An instance of DataLogger for logging conversation interactions.
        api_service: An instance of the API service for making asynchronous API calls.

    Methods:
        initiate: Initiate a conversation session with the given instruction.
        followup: Continue the conversation session with a follow-up instruction.
        create_payload_chatcompletion: Create a payload for chat completion API calls.
        call_chatcompletion: Make an asynchronous call to the chat completion API.
    """
    
    def __init__(self, system, dir=None, llmconfig=llmconfig, api_service=OAIService):
        """
        Initialize a Session object.

        Args:
            system: The system identifier for the conversation session.
            dir: The directory for logging interactions.
            llmconfig: Configuration parameters for language models.
            api_service: An instance of the API service for making asynchronous API calls.
        """
        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self.logger = DataLogger(dir=dir)
        self.api_service = api_service
    
    async def initiate(self, instruction, system=None, context=None, out=True, **kwargs) -> Any:
        """
        Initiate a conversation session with the given instruction.

        Args:
            instruction: The user's instruction to initiate the conversation.
            system: The content of the system message.
            context: Additional context for the user instruction.
            out: Whether to return the output content.

        Returns:
            Any: The output content if 'out' is True, otherwise None.
        """
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context)
        
        await self.call_chatcompletion(**config)
        if out:
            return self.conversation.responses[-1]['content']        

    async def followup(self, instruction, system=None, context=None, out=True, **kwargs) -> Any:
        """
        Continue the conversation session with a follow-up instruction.

        Args:
            instruction: The user's follow-up instruction.
            system: The content of the system message.
            context: Additional context for the user instruction.
            out: Whether to return the output content.

        Returns:
            Any: The output content if 'out' is True, otherwise None.
        """
        self.conversation.append_last_response()
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context)
        
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)
        if out:
            return self.conversation.responses[-1]['content']
    
    def create_payload_chatcompletion(self, **kwargs):
        """
        Create a payload for chat completion API calls.

        Args:
            kwargs: Additional keyword arguments for customization.
        """
        # currently only openai chat completions are supported
        messages = self.conversation.messages
        request_url = f"https://api.openai.com/v1/chat/completions"
        config = {**self.llmconfig, **kwargs}
        
        payload = {
            "messages": messages,
            "model": config.get('model'),
            "frequency_penalty": config.get('frequency_penalty'),
            "max_tokens": config.get('max_tokens'),
            "n": config.get('n'),
            "presence_penalty": config.get('presence_penalty'),
            "response_format": config.get('response_format'),
            "temperature": config.get('temperature'),
            "top_p": config.get('top_p'),
            }
        
        for key in ["seed", "stop", "stream", "tools", "tool_choice", "user"]:
            if config[key] is True:
                payload.update({key: config[key]})
    
        return (payload, request_url)
    
    async def call_chatcompletion(self, delay=1, **kwargs):
        """
        Make an asynchronous call to the chat completion API.

        Args:
            delay: The delay (in seconds) between API calls.
            kwargs: Additional keyword arguments for customization.
        """
        # currently only openai chat completions are supported
        payload, request_url = self.create_payload_chatcompletion(**kwargs)
        try:
            async with aiohttp.ClientSession() as session:
                completion = await self.api_service.call_api(session, request_url, payload)
                if "choices" in completion:
                    completion = completion['choices'][0]       # currently can only call one completion at a time, n has to be 1
                    self.logger({"input":self.conversation.messages, "output": completion})
                    response = {"role": "assistant", "content": completion['message']["content"]}
                    self.conversation.responses.append(response)
                    self.conversation.response_counts += 1
                    await asyncio.sleep(delay=delay)
                    status_tracker.num_tasks_succeeded += 1
                else:
                    status_tracker.num_tasks_failed += 1
        except Exception as e:
            status_tracker.num_tasks_failed += 1
            raise e