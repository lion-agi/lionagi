import json
from typing import Any
from dotenv import load_dotenv
load_dotenv()

from .conversations import Conversation
from ..utils.sys_utils import to_list
from ..schema import DataLogger
from ..service.service_utils import StatusTracker
from ..tools.tool_utils import ToolManager
from ..service.oai import OpenAIService
from ..endpoint.chat_completion import ChatCompletion
from ..llm_configs import oai_llmconfig, oai_schema

status_tracker = StatusTracker()
OAIService = OpenAIService(endpoint=ChatCompletion)


class Session:

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
    
    async def _output(self, invoke=True, out=True, tool_parser=None):
        if invoke:
            try: 
                func, args = self._toolmanager._get_function_call(self.conversation.responses[-1]['content'])
                outs = await self._toolmanager.ainvoke(func, args)
                outs = tool_parser(outs) if tool_parser else outs
                self.conversation.add_messages(response=outs)
            except:
                pass
        if out:
            return self.conversation.responses[-1]['content']
    
    def _is_invoked(self):
        msg = self.conversation.messages[-1]
        try: 
            if "function call result" in json.loads(msg['content']).keys():
                return True
        except: 
            return False    

    def register_tools(self, tools, funcs, update=False, new=False, prefix=None, postfix=None):
        funcs = to_list(funcs)
        self._toolmanager.register_tools(tools, funcs, update, new, prefix, postfix)
    
    async def initiate(self, instruction, system=None, context=None, name=None, invoke=True, out=True, tool_parser=None, **kwargs) -> Any:
        config = {**self.llmconfig, **kwargs}
        system = system or self.system
        self.conversation.initiate_conversation(system=system, instruction=instruction, context=context, name=name)
        await self._call_chatcompletion(**config)
        
        return await self._output(invoke, out, tool_parser)

    async def followup(self, instruction, system=None, context=None, out=True, name=None, invoke=True, tool_parser=None, **kwargs) -> Any:
        if system:
            self.conversation.change_system(system)
        self.conversation.add_messages(instruction=instruction, context=context, name=name)
        config = {**self.llmconfig, **kwargs}
        await self._call_chatcompletion(**config)

        return await self._output(invoke, out, tool_parser)

    async def auto_followup(self, instruct, num=3, tool_parser=None, **kwargs):
        cont_ = True
        while num > 0 and cont_ is True:
            await self.followup(instruct,tool_parser=tool_parser, tool_choice="auto", **kwargs)
            num -= 1
            cont_ = True if self._is_invoked() else False
        if num == 0:
            await self.followup(instruct, **kwargs)

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
    
    def _call_chatcompletion(self, service=None, schema=oai_schema, **kwargs):
        service = service or self.service
        return service.serve(session=self, schema=schema, **kwargs)
        