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
    
    def __init__(self, system, dir=None, llmconfig=llmconfig, api_service=OAIService):
        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self.logger = DataLogger(dir_=dir)
        self.api_service = api_service
    
    async def initiate(self, instruction, system=None, context=None, out=True, **kwargs) -> Any:
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context)
        
        await self.call_chatcompletion(**config)
        if out:
            return self.conversation.responses[-1]['content']        

    async def followup(self, instruction, system=None, context=None, out=True, **kwargs) -> Any:
        self.conversation.append_last_response()
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context)
        
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)
        if out:
            return self.conversation.responses[-1]['content']
    
    def create_payload_chatcompletion(self, **kwargs):
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