"""   
Copyright 2023 HaiyangLi <ocean@lionagi.ai>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import aiohttp
import asyncio
from typing import Any, Dict, Optional
from .SessionConfigs import SessionConfig
from .Conversation import Conversation
from ..api.BaseService import StatusTracker
from ..api.Services import sync_api_service
from ..utils.LogUtils import LLMLogger

llmlog = LLMLogger()
status_tracker = StatusTracker()

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
    def __init__(self, system, api_service=sync_api_service, status_tracker=status_tracker):

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
        request_url = f"https://api.openai.com/v1/chat/completions"

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

        completion = self.api_service.call_api(None, request_url, payload)  # Assuming synchronous
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