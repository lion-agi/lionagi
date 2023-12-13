import aiohttp
import asyncio
from typing import Any

from .conversation import Conversation
from ..utils.sys_util import to_list
from ..utils.log_util import DataLogger
from ..utils.api_util import StatusTracker
from ..utils.tool_util import ToolManager
from ..api.oai_service import OpenAIService

from ..api.oai_config import oai_llmconfig


status_tracker = StatusTracker()
OAIService = OpenAIService()

class Session():
    
    def __init__(self, system, dir=None, llmconfig=oai_llmconfig, api_service=OAIService):
        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self._logger = DataLogger(dir=dir)
        self.api_service = api_service
        self.toolmanager = ToolManager()
    
    def set_dir(self, dir):
        self._logger.dir = dir
    
    def set_system(self, system):
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        self.llmconfig = llmconfig
    
    def set_api_service(self, api_service):
        self.api_service = api_service
    
    async def _output(self, output, invoke=True, out=True):
        if invoke:
            try: 
                func, args = self.toolmanager._get_function_call(output)
                outs = await self.toolmanager.ainvoke(func, args)
                self.conversation.add_messages(tool=outs)
            except:
                pass
        if out:
            return output
        
    def register_tools(self, tools, funcs, update=False, new=False, prefix=None, postfix=None):
        funcs = to_list(funcs)
        self.toolmanager.register_tools(tools, funcs, update, new, prefix, postfix)
    
    async def initiate(self, instruction, system=None, context=None, out=True, name=None, invoke=True, **kwargs) -> Any:
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self.call_chatcompletion(**config)
        output = self.conversation.responses[-1]['content']
        
        return await self._output(output, invoke, out)

    async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, **kwargs) -> Any:
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        await self.call_chatcompletion(**config)
        output = self.conversation.responses[-1]['content']
        
        return await self._output(output, invoke, out)
    
    def create_payload_chatcompletion(self, **kwargs):
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

    async def call_chatcompletion(self, sleep=0.1,  **kwargs):
        endpoint = f"chat/completions"
        try:
            async with aiohttp.ClientSession() as session:
                payload = self.create_payload_chatcompletion(**kwargs)
                completion = await self.api_service.call_api(
                                session, endpoint, payload)
                if "choices" in completion:
                    self._logger({"input":payload, "output": completion})
                    self.conversation.add_messages(response=completion['choices'][0])
                    self.conversation.responses.append(self.conversation.messages[-1])
                    self.conversation.response_counts += 1
                    await asyncio.sleep(sleep)
                    status_tracker.num_tasks_succeeded += 1
                else:
                    status_tracker.num_tasks_failed += 1
        except Exception as e:
            status_tracker.num_tasks_failed += 1
            raise e
    
    def messages_to_csv(self, dir=None, filename="_messages.csv", **kwags):
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.conversation.msg.to_csv(dir=dir, filename=filename, **kwags)
        
    def log_to_csv(self, dir=None, filename="_llmlog.csv", **kwags):
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self._logger.to_csv(dir=dir, filename=filename, **kwags)