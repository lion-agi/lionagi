from typing import Any, Callable, Dict, List, Optional
import asyncio
import json

from .sys_utils import create_multiple_copies, l_call
from .oai_utils import gpt4_api_service, status_tracker
from .log_utils import LLMLogger

llmlog = LLMLogger()


class Message:
    """
    Represents a single message in a conversation, which can be a system message,
    an instruction, or a response.
    
    Attributes:
        role (str): The role associated with the message. Can be 'system', 'user', or 'assistant'.
        content (Any): The content of the message. This can be any data structure.
    Methods:
        _create_message: Internal method to populate the `role` and `content` attributes.
        __call__: Creates a dictionary representation of the message when the object is called.
    Sample Usages:
        ```python
        # Create a system message
        msg = Message()
        print(msg(system="System maintenance scheduled."))
        
        # Create a user instruction message with context
        msg = Message()
        print(msg(instruction="Open file.", context={"filename": "example.txt"}))
        
        # Create an assistant response message
        msg = Message()
        print(msg(response={"content": "File opened successfully."}))
        ```
    """
    
    def __init__(self, role=None, content=None) -> None:
        self.role = role
        self.content = content

    def _create_message(
        self, system=None, response=None, instruction=None, context=None):
        """
        Internal method to set the `role` and `content` attributes based on the provided parameters.

        Args:
            system (str, optional): System-related message. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.

        Raises:
            ValueError: If more than one role is provided for a single message.
        """
        
        if (system and (response or instruction)) or (response and instruction):
            raise ValueError("Error: Message cannot have more than one role.")
        else:
            if response:
                self.role = "assistant"
                self.content = response['content']
            elif instruction:
                self.role = "user"
                self.content = {"instruction": instruction}
                if context:
                    for k, v in context.items():
                        self.content[k] = v
            elif system:
                self.role = "system"
                self.content = system

    def __call__(self, system=None, response=None, instruction=None, context=None):
        """
        Converts the Message object to a dictionary representation when the object is called.

        Args:
            system (str, optional): System-related message. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.

        Returns:
            dict: A dictionary representation of the Message object.
        """

        self._create_message(
            system=system, response=response, instruction=instruction, context=context
        )
        if self.role == "assistant":
            return {"role": self.role, "content": self.content}
        else:
            return {"role": self.role, "content": json.dumps(self.content)}

massenger = Message()


class Conversation:
    """
    Manages a conversation consisting of multiple messages.

    Attributes:
        response_counts (int): A class-level counter for responses.
        messages (list): A list of messages in the conversation.
        system (str): System-related message.
        responses (list): A list to store responses.
    Methods:
        initiate_conversation: Initializes a new conversation.
        add_messages: Adds a new message to the conversation.
        change_system: Changes the system message.
        append_last_response: Adds the last response to the list of messages.
    """

    response_counts = 0

    def __init__(self, system, messages=[]) -> None:
        self.messages = messages
        self.system = system
        self.responses = []

    def initiate_conversation(self, system, instruction, context=None):
        """
        Initializes a new conversation by setting the initial system and instruction messages.

        Args:
            system (str): The initial system message.
            instruction (str): The initial instruction from the user.
            context (dict, optional): Additional context for the instruction. Defaults to None.
        """
        self.messages = []
        self.add_messages(system=system)
        self.add_messages(instruction=instruction, context=context)

    def add_messages(
        self, system=None, instruction=None, context=None, response=None
    ):
        """
        Adds a new message to the conversation.

        Args:
            system (str, optional): System-related message. Defaults to None.
            instruction (str, optional): User's instruction. Defaults to None.
            context (dict, optional): Additional context for the instruction. Defaults to None.
            response (dict, optional): Assistant's response. Defaults to None.
        """
        message = massenger(
            system=system, response=response, instruction=instruction, context=context
        )
        self.messages.append(message)

    def change_system(self, system):
        """
        Changes the initial system message.

        Args:
            system (str): The new system message.
        """
        self.system = system
        self.messages[0] = massenger(system=system)

    def append_last_response(self):
        """
        Appends the last response to the list of messages.
        """
        self.add_messages(response=self.responses[-1])
        
    def keep_last_n_exchanges(self, n: int, system=None) -> None:
        """
        Truncates front messages to only include the last n exchanges between the user and the assistant.
        Always keeps the initial system message.

        Args:
            n (int): Number of exchanges to retain. One exchange consists of one instruction and one response.
            system (str): The new system message. Defaults to the initial system message.

        """
        # Keep the system message
        system = system or self.messages[0]
        
        # Count how many assistant's responses are in the conversation
        response_indices = [
            index for index, message in enumerate(self.messages[1:]) if message["role"] == "assistant"
        ]
        
        # Calculate the index from where to start keeping the messages
        if len(response_indices) >= n:
            first_index_to_keep = response_indices[-n]  # This index is based on slicing from 1
            first_index_to_keep += 1  # Adjust index to include system message
            
            # Truncate messages but keep the system message
            self.messages = [system] + self.messages[first_index_to_keep:]
        else:
            # If there are fewer than n exchanges, do nothing
            pass
        
        
class SessionConfig:
    """
    Manages the configuration settings for a Session object.
    
    Attributes:
        config (dict): A dictionary containing key-value pairs for default configuration settings.
    """    
    def __init__(self):
        self.config = {
            "model": "gpt-4",
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
    Manages a conversation session, including its initiation, follow-up, and interaction with an API service.
    
    Attributes:
        conversation (Conversation): An object of the Conversation class that stores the conversation history.
        api_service (func): A function that handles API calls to the GPT-4 service.
        status_tracker (func): A function that tracks the status of the conversation.
        config (dict): Inherits the default configuration settings from `SessionConfig`.

    Methods:
        initiate: Starts a new conversation session, optionally with a new system message.
        followup: Adds a follow-up instruction to the ongoing conversation.
        call_OpenAI_ChatCompletion: Makes an API call to GPT-4 and updates the conversation history.
    """
    def __init__(self, system, api_service=gpt4_api_service, status_tracker=status_tracker):

        super().__init__()
        self.conversation = Conversation(system=system)
        self.api_service = api_service 
        self.status_tracker = status_tracker
        
    def initiate(
        self, 
        instruction: Dict[str, Any], 
        system: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None, 
        **kwargs
    ) -> Any:
        """
        Initiates a new conversation session or restarts an existing one.

        Args:
            instruction (Dict[str, Any]): The initial instruction from the user.
            system (Optional[str], optional): System message to initialize or restart the conversation.
            context (Optional[Dict[str, Any]], optional): Additional context data.
            kwargs (dict): Additional settings to override the default configuration.

        Returns:
            Any: The assistant's response, if the 'out' flag in the configuration is True.

        Sample Usages:
            >>> session.initiate(instruction={"command": "start"})
            >>> session.initiate(instruction={"command": "restart"}, system="System Reinitialized")
        """
        config = {**self.config, **kwargs}
        system = system if system else self.conversation.system
        self.conversation.initiate_conversation(
            system=system, instruction=instruction, context=context
        )

        self.call_OpenAI_ChatCompletion(**config)
        if config["out"]:
            return self.conversation.responses[-1]["content"]    
        
    def followup(
        self, 
        instruction: Dict[str, Any], 
        system: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None, 
        **kwargs
    ) -> Any:
        """
        Adds a follow-up instruction to an ongoing conversation.

        Args:
            instruction (Dict[str, Any]): The follow-up instruction from the user.
            system (Optional[str], optional): Optionally update the system message.
            context (Optional[Dict[str, Any]], optional): Additional context data.
            kwargs (dict): Additional settings to override the default configuration.

        Returns:
            Any: The assistant's response, if the 'out' flag in the configuration is True.

        Sample Usages:
            >>> session.followup(instruction={"command": "open"}, context={"filename": "example.txt"})
            >>> session.followup(instruction={"command": "save"}, system="File Operations")
        """

        self.conversation.append_last_response()
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context)

        config = {**self.config, **kwargs}
        self.call_OpenAI_ChatCompletion(**config)
        if config["out"]:
            return self.conversation.responses[-1]["content"]

    def call_OpenAI_ChatCompletion(self, **kwargs) -> None:
        """
        Makes an API call to GPT-4 to obtain the assistant's response.

        Args:
            kwargs (dict): Additional settings to override the default configuration. Possible keys include:
                - model (str): The GPT model to use (default is "gpt-4").
                - frequency_penalty (float): Controls the frequency penalty for the generated text.
                - temperature (float): Controls the randomness of the output (default is 1).
                - top_p (float): Controls the nucleus sampling and affects diversity of the generated text.
                - n (int): Number of generated tokens (default is 1).
                - stream (bool): Whether to stream the output (default is False).
                - stop (str or list): Token(s) at which to stop the generation (default is None).
                - function_call (bool): Flag to indicate a function call (default is None).
                - functions (dict): Dictionary containing function definitions (default is None).
                - sleep (float): Time in seconds to wait before the API call (default is 0.1).
                - out (bool): Whether to return the output (default is True).

        Sample Usage:
            >>> session.call_OpenAI_ChatCompletion(model="gpt-3.5-turbo", temperature=0.7)
        """
        messages = self.conversation.messages
        config = {**self.config, **kwargs}

        payload: Dict[str, Any] = {
            "messages": messages,
            "model": config["model"],
            "frequency_penalty": config["frequency_penalty"],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "n": config["n"],
        }

        for key in ["stream", "stop", "function_call", "functions"]:
            if config[key] is True:
                payload.update({key: config[key]})

        completion = self.api_service.call_api(payload)  # Assuming synchronous
        completion = completion["choices"][0]
        llmlog(self.conversation.messages, completion)
        response = {"role": "assistant", "content": completion["message"]["content"]}
        self.conversation.responses.append(response)
        self.conversation.response_counts += 1    
    
    async def ainitiate(self, 
            instruction: Dict[str, Any], 
            system: Optional[str] = None, 
            context: Optional[Dict[str, Any]] = None, 
            **kwargs) -> Any:
        """
        Asynchronously initiates a new conversation session or restarts an existing one.
        For argument details, refer to the `initiate` method.

        Returns:
            Any: The assistant's response, if the 'out' flag in the configuration is True.
        """
        config = {**self.config, **kwargs}
        system = system if system else self.conversation.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context)
        
        await self.acall_OpenAI_ChatCompletion(**config)
        if config['out']:
            return self.conversation.responses[-1]['content']        

    async def afollowup(self, 
            instruction: Dict[str, Any], 
            system: Optional[str] = None, 
            context: Optional[Dict[str, Any]] = None, 
            **kwargs) -> Any:
        """
        Asynchronously adds a follow-up instruction to an ongoing conversation.
        For argument details, refer to the `followup` method.

        Returns:
            Any: The assistant's response, if the 'out' flag in the configuration is True.
        """
        self.conversation.append_last_response()
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context)
        
        config = {**self.config, **kwargs}
        await self.acall_OpenAI_ChatCompletion(**config)
        if config['out']:
            return self.conversation.responses[-1]['content']
        
    async def acall_OpenAI_ChatCompletion(self, **kwargs) -> None:
        """
        Asynchronously makes an API call to GPT-4 to obtain the assistant's response.
        For argument details, refer to the `call_OpenAI_ChatCompletion` method.
        """
        messages = self.conversation.messages
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

        completion = await self.api_service.call_api(payload)
        completion = completion['choices'][0]
        llmlog(self.conversation.messages, completion)
        response = {"role": "assistant", "content": completion['message']["content"]}
        self.conversation.responses.append(response)
        self.conversation.response_counts += 1

class MultiSession(SessionConfig):
    """
    Manages multiple parallel sessions of user-assistant interactions.
    For argument and method details, refer to the `Session` class.
    
    Attributes:
        num_conversation (int): Number of parallel sessions.
        sessions (List[Session]): List of individual Session objects.
    """

    def __init__(self, 
                 system: str, 
                 api_service: Callable, 
                 status_tracker: Callable, 
                 num: int = 3) -> None:
        """
        Initializes multiple parallel sessions.
        """
        
        super().__init__()
        self.num_conversation = num
        self.sessions = create_multiple_copies(
            Session(system=system, api_service=api_service, status_tracker=status_tracker), 
            n=num)
        
    def initiate(self, 
                 instruction: Dict[str, Any], 
                 system: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None, 
                 **kwargs) -> List[Any]:
        """
        Initiates a new conversation session or restarts an existing one for all sessions.
        """

        config = {**self.config, **kwargs}
        system = system if system else self.sessions[0].conversation.system

        def initiate_single_session(session):
            return session.initiate(
                instruction=instruction, 
                system=system, 
                context=context, **config
            )
        
        results = l_call(self.sessions, initiate_single_session)
    
        if config['out']:
            return results

    def followup(self, 
                 instruction: Dict[str, Any], 
                 system: Optional[str] = None, 
                 context: Optional[Dict[str, Any]] = None, 
                 **kwargs) -> List[Any]:
        """
        Adds a follow-up instruction to an ongoing conversation for all sessions.
        """

        config = {**self.config, **kwargs}

        def followup_single_session(session):
            if system:
                session.conversation.change_system(system)
            return session.followup(
                system=system, 
                instruction=instruction, 
                context=context, **config
            )
        
        results = l_call(self.sessions, followup_single_session)
        
        if config['out']:
            return results


    async def ainitiate(self, 
                        instruction: Dict[str, Any], 
                        system: Optional[str] = None, 
                        context: Optional[Dict[str, Any]] = None, 
                        **kwargs) -> List[Any]:
        """
        Asynchronously initiates a new conversation session or restarts an existing one for all sessions.
        """
        
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

    async def afollowup(self, 
                        instruction: Dict[str, Any], 
                        system: Optional[str] = None, 
                        context: Optional[Dict[str, Any]] = None, 
                        **kwargs) -> List[Any]:
        """
        Asynchronously adds a follow-up instruction to an ongoing conversation for all sessions.
        """

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