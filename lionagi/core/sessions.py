import os
import json
from typing import Any

from .conversations import Conversation
from ..utils.sys_utils import to_list, l_call, al_call
from ..schema import DataLogger
from ..utils.service_utils import StatusTracker
from ..service.oai import OpenAIService
from ..llm_configs import oai_llmconfig
from ..endpoint.chat_completion import ChatCompletion
from ..utils.tool_utils import ToolManager

status_tracker = StatusTracker()
OAIService = OpenAIService(api_key=os.getenv('OPENAI_API_KEY'))
chat_completion = ChatCompletion()


class Session():

    def __init__(self, system, dir=None, llmconfig=oai_llmconfig, service=OAIService):
        self.conversation = Conversation()
        self.system = system
        self.llmconfig = llmconfig
        self._logger = DataLogger(dir=dir)
        self.service = service
        self._toolmanager = ToolManager()
    
    def set_dir(self, dir):
        self._logger.dir = dir
    
    def set_system(self, system):
        self.conversation.change_system(system)
    
    def set_llmconfig(self, llmconfig):
        self.llmconfig = llmconfig
    
    def set_service(self, service):
        self.service = service
    
    async def _output(self, invoke=True, out=True):
        if invoke:
            try:
                tool_uses = json.loads(self.conversation.responses[-1]['content'])
                if 'function_list' in tool_uses.keys():
                    func_calls = l_call(tool_uses['function_list'], self._toolmanager._get_function_call)

                else:
                    func_calls = l_call(tool_uses['tool_uses'], self._toolmanager._get_function_call)

                outs = await al_call(func_calls, self._toolmanager.ainvoke)
                if tool_parser:
                    outs = l_call(outs, tool_parser)
                for out, f in zip(outs, func_calls):
                    response = {"function": f[0], "arguments": f[1], "output": out}
                    self.conversation.add_messages(response=response)

            except:
                pass

        if out:
            return self.conversation.responses[-1]['content']
    
    def _is_invoked(self):
        msg = self.conversation.messages[-1]
        try: 
            if json.loads(msg['content']).keys() >= {'function', 'arguments', 'output'}:
                return True
        except: 
            return False    

    def register_tools(self, tools, funcs, update=False, new=False, prefix=None, postfix=None):
        funcs = to_list(funcs)
        self._toolmanager.register_tools(tools, funcs, update, new, prefix, postfix)
    
    async def initiate(self, instruction, system=None, context=None, name=None, invoke=True, out=True, tool_parser=None, sleep=0, **kwargs) -> Any:
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        # await call_chatcompletion(self, sleep, **config)
        return await self._output(invoke, out)

    async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, tool_parser=None, sleep=0, **kwargs) -> Any:
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        # await call_chatcompletion(self, sleep, **config)

        return await self._output(invoke, out)

    async def auto_followup(self, instruction, num=3, **kwargs):
        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruction, tool_choice="auto", **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruction, **kwargs)

    def messages_to_csv(self, dir=None, filename="_messages.csv", **kwargs):
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self.conversation.msg.to_csv(dir=dir, filename=filename, **kwargs)
        
    def log_to_csv(self, dir=None, filename="_llmlog.csv", **kwargs):
        dir = dir or self._logger.dir
        if dir is None:
            raise ValueError("No directory specified.")
        self._logger.to_csv(dir=dir, filename=filename, **kwargs)
